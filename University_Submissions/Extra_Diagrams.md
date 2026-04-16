# Supplemental Project Diagrams

*(You can copy and paste the `mermaid` code blocks below into your DA Word documents, or render them directly in your Markdown viewer.)*

---

## Digital Assignment 1 (DA1)

### 1. User Journey Flowchart
**Purpose:** Maps out the step-by-step experience of a System Architect logging in and creating a simulation. Perfect for your UI flow documentation in DA1.

```mermaid
flowchart TD
    Start([User Logs In]) --> Dashboard[Landing Dashboard]
    Dashboard --> Action{What next?}
    Action -->|Create New| Canvas[Open Blank Canvas]
    Action -->|Load Template| Template[Select E-Commerce Template]
    
    Canvas --> Tooling[Drag & Drop Nodes]
    Template --> Tooling
    
    Tooling --> Wiring[Connect Nodes via Edges]
    Wiring --> Sim[Click 'Start Simulation']
    Sim --> Traffic{Are packets flowing?}
    
    Traffic -->|Yes| Analytics[View Telemetry & Cost Dashboard]
    Traffic -->|No| Fix[Inspect Node Settings/Connections]
    Fix --> Sim
    
    Analytics --> Export[Export CSV Metrics]
    Export --> End([End Session])
```

---

## Digital Assignment 2 (DA2)

### 2. Domain Class Diagram
**Purpose:** Illustrates the fundamental data structures and classes powering the NetworkSim application. Excellent for explaining Object-Oriented principles and modularity in DA2.

```mermaid
classDiagram
    class SystemPhysicsEngine {
        +Graph network_digraph
        +tick_rate: int
        +start_simulation()
        +calculate_shortest_paths()
        +broadcast_tick()
    }
    
    class RoutingNode {
        +String uuid
        +String component_type
        +int max_capacity
        +int current_load
        +String state
        +float generate_cost()
    }
    
    class NetworkEdge {
        +String source_id
        +String target_id
        +float latency_ms
        +int bandwidth_limit
    }
    
    class ChaosDaemon {
        +float aggression_level
        +boolean is_active
        +inject_failure(Graph)
    }

    SystemPhysicsEngine "1" *-- "many" RoutingNode
    SystemPhysicsEngine "1" *-- "many" NetworkEdge
    ChaosDaemon --> SystemPhysicsEngine : Mutates Status
```

### 3. Node State Machine Diagram
**Purpose:** Demonstrates the possible operational states a structural node can exist within during a simulation run. Ideal for backend design explanations.

```mermaid
stateDiagram-v2
    [*] --> Online: Node Deployed
    
    state Online {
        [*] --> UnderLoad: capacity > 80%
        UnderLoad --> Stable: capacity < 80%
    }
    
    Online --> Degraded: Chaos Daemon Hit
    Degraded --> Offline: Cascading Failure / Manual Kill
    
    Offline --> Online: NLP Auto-Fix ('Repair')
    Degraded --> Online: NLP Auto-Fix ('Repair')
    
    Offline --> [*]: Node Deleted
```

---

## Digital Assignment 3 (DA3)

### 4. 60Hz Engine Activity Flow
**Purpose:** Outlines the core cyclical execution thread that allows the Python physics engine to function asynchronously. Great for your Systems Architecture and Test section.

```mermaid
flowchart TD
    Start((Simulation Start)) --> Loop[Initialize 60Hz Event Loop]
    Loop --> Wait[Wait for Next Tick ~16ms]
    Wait --> Poll[Poll for UI State Changes from React]
    Poll --> Calc[Recalculate Node Throughput Matrix]
    
    Calc --> Status{Chaos Daemon Active?}
    Status -->|Yes| Mutate[Inject Random Packet Drops / Latency]
    Status -->|No| Safe[Bypass Mutation]
    
    Mutate --> Package
    Safe --> Package
    
    Package[Package Current Frame as JSON]
    Package --> Push[Broadcast via WebSocket]
    Push --> Next{Stop Signal Received?}
    Next -->|No| Wait
    Next -->|Yes| End((End Simulation))
```

### 5. Docker Deployment Orchestration Diagram
**Purpose:** Shows how the separated containers execute securely on the host machine to deliver the full application, proving your deployment strategy.

```mermaid
flowchart LR
    Browser([User Browser]) <-->|HTTP/WS ports 3000, 8000| DockerMachine[Docker Host Machine]
    
    subgraph Docker_Network [Internal Docker Virtual Network]
        direction TB
        Next[Next.js Container\nPort 3000\nUI & Middleware]
        Python[FastAPI Container\nPort 8000\nPhysics & WebSocket]
        Redis[(Redis Alpine Container\nPort 6379\nIn-Memory Cache)]
        
        Next <--> Python
        Python <--> Redis
    end
    
    DockerMachine <--> Docker_Network
```
