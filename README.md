# NetworkSim

A real-time distributed systems simulator with an interactive topology canvas. Build network architectures, inject failures, and observe traffic flow, queuing, and cost behavior under load.

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+

### Frontend

```bash
npm install
npm run dev
```

Open http://localhost:3000

### Backend

```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # Linux/macOS

pip install -e ./networksim_core
pip install -r backend/requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir backend
```

### Docker

```bash
cp .env.example .env       # edit credentials before production use
docker compose up
```

## Running Tests

```bash
# engine unit tests
python -m pytest networksim_core/tests/ -v

# frontend lint + typecheck
npm run lint
npm run type-check

# CLI invariant check
pip install -e ./cli
networksim examples/blueprints/ecommerce.json -i examples/rules/sla_check.yaml
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for the system diagram.

- **Frontend**: Next.js 16 / React Flow / Zustand / Recharts / Tailwind CSS
- **Backend**: FastAPI / SQLAlchemy (async) / Redis / WebSocket streaming
- **Engine**: `networksim_core` -- python-igraph, M/M/c/K queuing model, seedable chaos injection
- **CLI**: standalone invariant checker with JUnit XML and Markdown output

## Configuration

Copy `.env.example` to `.env`. All configuration is via environment variables -- see the template for available options.

## License

Proprietary.
