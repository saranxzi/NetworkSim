# Architecture

## System Overview

```mermaid
graph TD
    Browser["Browser (Next.js)"]

    subgraph Frontend
        Canvas["LabCanvas (React Flow)"]
        Store["Zustand Store"]
        Panels["Panels (Analytics, Cost, Plugin, Blueprint)"]
        Replay["ReplayController"]
    end

    subgraph Backend
        API["FastAPI"]
        WS["WebSocket Handler"]
        Auth["JWT Auth Middleware"]
        Routes["Blueprint / Run / FinOps Routes"]
        DB["SQLAlchemy (SQLite / PostgreSQL)"]
        Cache["Redis / LRU Fallback"]
    end

    subgraph Engine["networksim_core"]
        Sim["NetworkSimulator"]
        Physics["M/M/c/K Queue Physics"]
        Chaos["ChaosEngine"]
        Delta["DeltaTracker"]
        Sandbox["RestrictedPython Plugin Sandbox"]
        Invariants["Invariant Checker"]
    end

    CLI["CLI Runner"]

    Browser --> Canvas
    Canvas --> Store
    Store --> Panels
    Store --> Replay

    Browser -- "POST /simulate" --> API
    Browser -- "WS /ws/simulate" --> WS
    API --> Auth
    WS --> Auth
    Auth --> Routes
    Routes --> DB
    Routes --> Cache

    API -- "run_simulation()" --> Sim
    WS -- "async stream" --> Sim
    Sim --> Physics
    Sim --> Chaos
    Sim --> Delta
    Sim --> Sandbox

    CLI --> Sim
    CLI --> Invariants
```

## Data Flow

1. User builds a topology on the canvas (nodes + edges stored in Zustand)
2. Simulation starts via WebSocket -- graph is serialized and sent to the backend
3. Backend validates the graph, creates a `NetworkSimulator`, and streams tick deltas back
4. Each tick: physics evaluates M/M/c/K queuing per node, chaos engine may fail nodes, plugins run in sandbox, delta tracker computes diffs
5. Frontend receives deltas, updates store, renders charts and node states
6. After completion, ReplayController allows scrubbing through tick history with sub-tick interpolation

## Key Directories

```
flightsim/
  app/                  Next.js app directory (pages, layout)
  components/           React components (canvas, panels, telemetry, auth)
  lib/                  Zustand store, auth helpers
  backend/
    app/                FastAPI application (routes, models, auth, cache, db)
  networksim_core/      Pip-installable simulation engine library
    src/networksim/
      engine/           Simulator, physics, chaos, delta tracker
      plugins/          RestrictedPython sandbox
      invariants/       YAML rule loader, AST checker, reporters
      tracing/          W3C trace span generator
  cli/                  CLI runner (networksim command)
  examples/             Sample blueprints and invariant rules
  docs/                 Architecture documentation
```
