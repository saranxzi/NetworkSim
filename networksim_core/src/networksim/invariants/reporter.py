from collections import defaultdict
from networksim.invariants.checker import Violation
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

def generate_junit_xml(violations: list[Violation], scenario_name: str, total_ticks: int, duration_seconds: float) -> str:
    """Generate JUnit XML format for CI/CD systems (GitHub Actions, Jenkins, GitLab CI)."""
    testsuite = ET.Element('testsuite')
    testsuite.set('name', scenario_name)
    testsuite.set('tests', str(len(set(v.rule_name for v in violations)) or 1))
    testsuite.set('failures', str(len(violations)))
    testsuite.set('time', f'{duration_seconds:.3f}')
    testsuite.set('timestamp', datetime.now(timezone.utc).isoformat())
    
    if not violations:
        tc = ET.SubElement(testsuite, 'testcase')
        tc.set('name', f'{scenario_name} - All Invariants')
        tc.set('classname', 'networksim.invariants')
        tc.set('time', f'{duration_seconds:.3f}')
    else:
        # Group violations by rule in a single O(M) pass
        by_rule: dict[str, list[Violation]] = defaultdict(list)
        for v in violations:
            by_rule[v.rule_name].append(v)

        for rule_name, rule_violations in by_rule.items():
            first_v = rule_violations[0]
            tc = ET.SubElement(testsuite, 'testcase')
            tc.set('name', rule_name)
            tc.set('classname', 'networksim.invariants')
            
            failure = ET.SubElement(tc, 'failure')
            failure.set('type', first_v.severity)
            failure.set('message', f'Invariant violated at {len(rule_violations)} tick(s)')
            
            details = [
                f'  Tick {sv.tick}: {sv.target} - {sv.expression} (actual: {sv.actual_values})'
                for sv in rule_violations[:5]
            ]
            if len(rule_violations) > 5:
                details.append(f'  ... and {len(rule_violations) - 5} more violations')
            failure.text = '\n'.join(details)
    
    return ET.tostring(testsuite, encoding='unicode', xml_declaration=True)


def generate_markdown_report(violations: list[Violation], scenario_name: str, total_ticks: int, duration_seconds: float) -> str:
    """Generate a Markdown summary report suitable for PR comments."""
    lines = []
    passed = len(violations) == 0
    status_emoji = 'PASS' if passed else 'FAIL'
    
    lines.append(f'# {status_emoji} NetworkSim Architecture Test: {scenario_name}')
    lines.append('')
    lines.append(f'| Metric | Value |')
    lines.append(f'|--------|-------|')
    lines.append(f'| **Status** | {"PASSED" if passed else "FAILED"} |')
    lines.append(f'| **Total Ticks** | {total_ticks} |')
    lines.append(f'| **Duration** | {duration_seconds:.2f}s |')
    lines.append(f'| **Violations** | {len(violations)} |')
    lines.append(f'| **Critical** | {sum(1 for v in violations if v.severity == "critical")} |')
    lines.append('')
    
    if violations:
        lines.append('## Violations')
        lines.append('')
        lines.append('| Tick | Rule | Target | Severity | Expression |')
        lines.append('|------|------|--------|----------|------------|')
        for v in violations[:20]:
            lines.append(f'| {v.tick} | {v.rule_name} | {v.target} | {v.severity} | `{v.expression}` |')
        if len(violations) > 20:
            lines.append(f'| ... | *{len(violations) - 20} more* | | | |')
    
    return '\n'.join(lines)
