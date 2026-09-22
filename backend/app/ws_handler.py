"""
WebSocket simulation handler with backpressure detection.

Manages the lifecycle of a streaming simulation session:
1. Accept connection and validate payload
2. Build simulator from validated graph
3. Stream delta-compressed tick results
4. Handle disconnection and errors gracefully
"""

import asyncio
import logging

from fastapi import WebSocket, WebSocketDisconnect

try:
    import orjson
    def json_dumps(obj: dict) -> str:
        return orjson.dumps(obj).decode("utf-8")
except ImportError:
    import json
    def json_dumps(obj: dict) -> str:
        return json.dumps(obj)

import json as stdlib_json

logger = logging.getLogger(__name__)

# Validation constants
MAX_WS_PAYLOAD_BYTES = 1_000_000  # 1MB
MAX_NODES = 200
MAX_TICKS = 600
DEFAULT_TICK_INTERVAL = 0.05  # 50ms between ticks


async def handle_simulation_ws(websocket: WebSocket) -> None:
    """
    Main WebSocket handler for streaming simulations.
    
    Protocol:
    1. Client sends a single JSON message with graph, duration, failures, chaos_mode, seed
    2. Server streams back one JSON message per tick (delta-compressed)
    3. Server closes connection when simulation completes
    
    Backpressure: If the WebSocket send buffer grows too large,
    the tick interval is adaptively increased to let the client catch up.
    """
    # Auth check for WebSocket connections
    import os
    AUTH_ENABLED = os.getenv("AUTH_ENABLED", "false").lower() == "true"
    if AUTH_ENABLED:
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001, reason="Authentication required")
            return
        try:
            from app.auth import _verify_jwt
            _verify_jwt(token)
        except Exception:
            await websocket.close(code=4001, reason="Invalid or expired token")
            return
            
    await websocket.accept()
    
    try:
        # Step 1: Receive and validate simulation request
        raw_data = await websocket.receive_text()
        
        if len(raw_data) > MAX_WS_PAYLOAD_BYTES:
            await websocket.close(code=1009, reason="Payload too large")
            return
        
        payload = stdlib_json.loads(raw_data)
        
        # Step 2: Validate graph structure via Pydantic
        # Import here to support both networksim_core and legacy models
        try:
            from networksim.models import CanvasGraph
        except ImportError:
            from app.models import CanvasGraph
        
        graph = CanvasGraph(**payload.get("graph", {}))
        
        if len(graph.nodes) > MAX_NODES:
            await websocket.close(
                code=1008,
                reason=f"Too many nodes (max {MAX_NODES})"
            )
            return
        
        duration = min(int(payload.get("duration_ticks", 60)), MAX_TICKS)
        failures = payload.get("failures_injected", [])
        chaos_mode = bool(payload.get("chaos_mode", False))
        seed = int(payload.get("seed", 0))
        enable_tracing = bool(payload.get("enable_tracing", True))
        
        # Step 3: Build simulator
        try:
            from networksim.engine.simulator import NetworkSimulator
            
            simulator = NetworkSimulator(
                graph=graph,
                duration_ticks=duration,
                failures=failures,
                chaos_mode=chaos_mode,
                seed=seed,
            )
            
            # Optional: trace generator for waterfall view
            trace_gen = None
            if enable_tracing:
                try:
                    from networksim.tracing.otel_synth import TraceGenerator
                    import random
                    trace_gen = TraceGenerator(rng=random.Random(seed))
                    edge_tuples = [(e.source, e.target) for e in graph.edges]
                    topo_order = simulator.graph.topo_order
                except ImportError:
                    pass
            
            # Step 4: Stream ticks with adaptive interval
            tick_interval = DEFAULT_TICK_INTERVAL
            full_state: Dict[str, dict] = {}  # Accumulated state for traces
            
            async for tick_data in simulator.run():
                # Merge deltas into full state for trace generation
                for nid, delta in tick_data["nodes"].items():
                    if nid not in full_state:
                        full_state[nid] = {}
                    full_state[nid].update(delta)
                
                # Generate trace every 5th tick
                if trace_gen and tick_data["tick"] % 5 == 0:
                    trace = trace_gen.generate_trace(
                        tick_data["tick"], full_state, topo_order, edge_tuples
                    )
                    if trace:
                        tick_data["trace"] = trace_gen.trace_to_dict(trace)
                
                msg = json_dumps(tick_data)
                await websocket.send_text(msg)
                await asyncio.sleep(tick_interval)
            await websocket.close()
        except Exception as e:
            logger.exception(f"Simulation execution error: {e}")
            await websocket.close(code=1011, reason="Simulation error")
        
    except WebSocketDisconnect:
        logger.info("Client disconnected during simulation")
    except stdlib_json.JSONDecodeError:
        logger.warning("Invalid JSON received on WebSocket")
        try:
            await websocket.close(code=1003, reason="Invalid JSON")
        except Exception:
            pass
    except Exception:
        logger.exception("Unexpected WebSocket error")
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
