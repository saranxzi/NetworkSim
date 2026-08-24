"""WebSocket load test — verifies the backend can handle concurrent simulation sessions.

Usage:
    python tests/load/test_websocket_load.py [--connections 100] [--ticks 60]
"""

import asyncio
import json
import time
import argparse
import statistics
from typing import List, Dict

# Minimal 3-node graph for load testing
TEST_GRAPH = {
    "nodes": {
        "client": {"label": "Client", "type": "client", "base_rps": 200.0, "burst_factor": 1.0},
        "api": {"label": "API", "type": "api_server", "capacity": 500.0, "base_latency": 10.0},
        "db": {"label": "DB", "type": "database", "write_capacity": 200.0, "base_latency": 20.0},
    },
    "edges": [
        {"source": "client", "target": "api"},
        {"source": "api", "target": "db"},
    ],
}


async def run_single_session(
    url: str, session_id: int, ticks: int, results: Dict[str, List]
) -> None:
    """Connect, send graph, consume all ticks, measure latency."""
    try:
        import websockets
    except ImportError:
        print("Install websockets: pip install websockets")
        return

    tick_latencies: List[float] = []
    start = time.perf_counter()

    try:
        async with websockets.connect(url, open_timeout=10) as ws:
            payload = json.dumps({
                "graph": TEST_GRAPH,
                "duration_ticks": ticks,
                "failures_injected": [],
                "chaos_mode": False,
                "seed": session_id,
            })
            await ws.send(payload)

            tick_count = 0
            while True:
                try:
                    tick_start = time.perf_counter()
                    msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    tick_latencies.append(time.perf_counter() - tick_start)
                    tick_count += 1
                except asyncio.TimeoutError:
                    break

            elapsed = time.perf_counter() - start
            results["success"].append(session_id)
            results["ticks"].append(tick_count)
            results["elapsed"].append(elapsed)
            results["latencies"].extend(tick_latencies)

    except Exception as e:
        results["errors"].append(f"Session {session_id}: {e}")


async def run_load_test(url: str, connections: int, ticks: int) -> None:
    """Spawn N concurrent WebSocket sessions and report metrics."""
    print(f"\n{'='*60}")
    print(f"  NetworkSim WebSocket Load Test")
    print(f"  URL: {url}")
    print(f"  Connections: {connections}")
    print(f"  Ticks per session: {ticks}")
    print(f"{'='*60}\n")

    results: Dict[str, List] = {
        "success": [],
        "errors": [],
        "ticks": [],
        "elapsed": [],
        "latencies": [],
    }

    start = time.perf_counter()
    tasks = [
        run_single_session(url, i, ticks, results)
        for i in range(connections)
    ]
    await asyncio.gather(*tasks)
    total_elapsed = time.perf_counter() - start

    # Report
    success = len(results["success"])
    errors = len(results["errors"])
    latencies = results["latencies"]

    print(f"\n{'='*60}")
    print(f"  RESULTS")
    print(f"{'='*60}")
    print(f"  Successful sessions:  {success}/{connections}")
    print(f"  Failed sessions:      {errors}/{connections}")
    print(f"  Total wall time:      {total_elapsed:.2f}s")

    if latencies:
        latencies.sort()
        print(f"\n  Tick Latency (ms):")
        print(f"    p50:  {statistics.median(latencies)*1000:.1f}")
        print(f"    p95:  {latencies[int(len(latencies)*0.95)]*1000:.1f}")
        print(f"    p99:  {latencies[int(len(latencies)*0.99)]*1000:.1f}")
        print(f"    max:  {max(latencies)*1000:.1f}")

    if results["elapsed"]:
        print(f"\n  Session Duration (s):")
        print(f"    avg:  {statistics.mean(results['elapsed']):.2f}")
        print(f"    max:  {max(results['elapsed']):.2f}")

    if results["errors"]:
        print(f"\n  Errors:")
        for err in results["errors"][:10]:
            print(f"    - {err}")

    # Pass/fail
    success_rate = success / connections if connections > 0 else 0
    if success_rate >= 0.95:
        print(f"\n  [PASS] {success_rate*100:.0f}% success rate")
    else:
        print(f"\n  [FAIL] {success_rate*100:.0f}% success rate (target: 95%)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NetworkSim WebSocket Load Test")
    parser.add_argument("--url", default="ws://localhost:8000/ws/simulate", help="WebSocket URL")
    parser.add_argument("--connections", type=int, default=100, help="Number of concurrent connections")
    parser.add_argument("--ticks", type=int, default=60, help="Ticks per session")
    args = parser.parse_args()

    asyncio.run(run_load_test(args.url, args.connections, args.ticks))
