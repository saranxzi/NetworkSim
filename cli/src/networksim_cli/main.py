import typer
import json
import sys
import time
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from networksim.models import CanvasGraph
from networksim.engine.simulator import NetworkSimulator
from networksim.invariants.loader import load_invariants
from networksim.invariants.checker import InvariantChecker
from networksim.invariants.reporter import generate_junit_xml, generate_markdown_report

app = typer.Typer(
    name="networksim",
    help="NetworkSim — Executable Architecture Verification for Engineers",
    add_completion=False,
    invoke_without_command=True,
)
console = Console()


@app.command()
def test(
    blueprint: Path = typer.Argument(..., help="Path to blueprint JSON file", exists=True),
    invariants: Path = typer.Option(..., "--invariants", "-i", help="Path to invariant rules YAML", exists=True),
    seed: int = typer.Option(42, "--seed", "-s", help="Random seed for deterministic runs"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich, junit, markdown"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Run architecture invariant tests against a blueprint."""
    console.print(Panel.fit(
        "[bold cyan]NetworkSim[/bold cyan] Architecture Test Runner",
        border_style="cyan"
    ))
    
    # Load blueprint
    console.print(f"[>>] Loading blueprint: [blue]{blueprint}[/blue]")
    with open(blueprint) as f:
        bp_data = json.load(f)
    
    graph = CanvasGraph(**bp_data.get('graph', bp_data))
    console.print(f"    -> {len(graph.nodes)} nodes, {len(graph.edges)} edges")
    
    # Load invariants
    console.print(f"[>>] Loading invariants: [blue]{invariants}[/blue]")
    config = load_invariants(str(invariants))
    console.print(f"    -> {len(config.invariants)} rules, scenario: [yellow]{config.scenario}[/yellow]")
    
    duration = config.duration_ticks
    
    # Build failures from trigger_events
    failures = []
    for rule in config.invariants:
        if rule.trigger_event:
            failures.append({
                'node_id': rule.trigger_event.target,
                'start_tick': rule.trigger_event.tick,
                'end_tick': rule.trigger_event.tick + 10,
            })
    
    # Run simulation
    console.print(f"\n[>>] Running simulation: {duration} ticks, seed={seed}")
    
    sim = NetworkSimulator(
        graph=graph,
        duration_ticks=duration,
        failures=failures,
        chaos_mode=False,
        seed=seed,
    )
    
    checker = InvariantChecker(config.invariants)
    
    start_time = time.time()
    
    # Accumulate full state for invariant checking
    full_state = {}
    results = sim.run_sync()
    
    for tick_data in results:
        tick = tick_data['tick']
        # Merge deltas into full state
        for nid, delta in tick_data['nodes'].items():
            if nid not in full_state:
                full_state[nid] = {}
            full_state[nid].update(delta)
        
        # Check invariants against full accumulated state
        checker.evaluate_tick(tick, full_state)
    
    elapsed = time.time() - start_time
    
    # Output results
    if format == 'junit':
        report = generate_junit_xml(checker.violations, config.scenario, duration, elapsed)
        if output:
            output.write_text(report)
            console.print(f"\n[>>] JUnit XML written to [green]{output}[/green]")
        else:
            print(report)
    elif format == 'markdown':
        report = generate_markdown_report(checker.violations, config.scenario, duration, elapsed)
        if output:
            output.write_text(report)
            console.print(f"\n[>>] Markdown report written to [green]{output}[/green]")
        else:
            print(report)
    else:
        # Rich console output
        _print_rich_report(checker, config.scenario, duration, elapsed)
    
    # Exit code
    if checker.has_critical_violations:
        console.print("\n[bold red][FAIL] FAILED[/bold red] -- Critical invariant violations detected.")
        raise typer.Exit(code=1)
    elif not checker.passed:
        console.print("\n[bold yellow][WARN] WARNING[/bold yellow] -- Non-critical violations detected.")
        raise typer.Exit(code=0)
    else:
        console.print("\n[bold green][PASS] PASSED[/bold green] -- All invariants satisfied.")
        raise typer.Exit(code=0)


def _print_rich_report(checker: InvariantChecker, scenario: str, ticks: int, elapsed: float):
    """Print a rich formatted report to the console."""
    table = Table(title=f"Results: {scenario}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Status", "[green]PASSED[/green]" if checker.passed else "[red]FAILED[/red]")
    table.add_row("Total Ticks", str(ticks))
    table.add_row("Duration", f"{elapsed:.3f}s")
    table.add_row("Violations", str(len(checker.violations)))
    table.add_row("Critical", str(sum(1 for v in checker.violations if v.severity == 'critical')))
    
    console.print(table)
    
    if checker.violations:
        vtable = Table(title="Violations")
        vtable.add_column("Tick", style="yellow")
        vtable.add_column("Rule")
        vtable.add_column("Target")
        vtable.add_column("Severity")
        vtable.add_column("Expression", style="dim")
        
        for v in checker.violations[:20]:
            sev_style = "red" if v.severity == 'critical' else "yellow"
            vtable.add_row(
                str(v.tick),
                v.rule_name,
                v.target,
                f"[{sev_style}]{v.severity}[/{sev_style}]",
                v.expression
            )
        
        console.print(vtable)
