"""
Airline Support Ticket Analyzer
Reads tickets.csv and produces analysis + dashboard.html
"""

import csv
import json
from collections import defaultdict

CSV_FILE = "tickets.csv"
OUTPUT_HTML = "dashboard.html"
COST_PER_TICKET = 15  # USD

# AI deflection opportunity by category (based on complexity/repeatability)
DEFLECTION_SCORES = {
    "app issue": "high",
    "check-in problem": "high",
    "flight delay": "medium",
    "seat issue": "medium",
    "cancellation": "medium",
    "refund request": "low",
    "lost baggage": "low",
}

DEFLECTION_RATIONALE = {
    "app issue": "Highly automatable — mostly troubleshooting steps, FAQs, and self-service fixes.",
    "check-in problem": "Most issues are procedural and resolvable via automated guidance or self-service.",
    "flight delay": "Status updates and compensation eligibility can be fully automated.",
    "seat issue": "Seat changes and refund triggers can be automated; some cases need agent review.",
    "cancellation": "Rebooking and refund processing can be partially automated, with escalation paths.",
    "refund request": "Policy-based, but complex edge cases and disputes require human judgment.",
    "lost baggage": "High emotional stakes and physical coordination make full automation difficult.",
}

DEFLECTION_SAVINGS_RATE = {
    "high": 0.80,   # 80% of tickets in this category could be deflected
    "medium": 0.50,
    "low": 0.20,
}


def load_tickets(path):
    tickets = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["resolution_time_hours"] = float(row["resolution_time_hours"])
            row["was_resolved_first_contact"] = row["was_resolved_first_contact"].strip().lower() == "yes"
            tickets.append(row)
    return tickets


def analyze(tickets):
    volume = defaultdict(int)
    total_resolution_time = defaultdict(float)
    first_contact_count = defaultdict(int)

    for t in tickets:
        cat = t["category"]
        volume[cat] += 1
        total_resolution_time[cat] += t["resolution_time_hours"]
        if t["was_resolved_first_contact"]:
            first_contact_count[cat] += 1

    categories = sorted(volume.keys())

    results = {}
    for cat in categories:
        vol = volume[cat]
        avg_res = round(total_resolution_time[cat] / vol, 1) if vol else 0
        fcr = round(first_contact_count[cat] / vol * 100, 1) if vol else 0
        deflection = DEFLECTION_SCORES[cat]
        savings_rate = DEFLECTION_SAVINGS_RATE[deflection]
        estimated_savings = round(vol * savings_rate * COST_PER_TICKET, 2)

        results[cat] = {
            "volume": vol,
            "avg_resolution_hours": avg_res,
            "first_contact_resolution_pct": fcr,
            "deflection_opportunity": deflection,
            "deflection_rationale": DEFLECTION_RATIONALE[cat],
            "estimated_ai_savings_usd": estimated_savings,
        }

    total_savings = round(sum(r["estimated_ai_savings_usd"] for r in results.values()), 2)
    total_deflectable = sum(
        r["volume"] for r in results.values()
        if r["deflection_opportunity"] in ("high", "medium")
    )

    return results, total_savings, total_deflectable, len(tickets)


def print_report(results, total_savings, total_deflectable, total_tickets):
    print(f"\n{'='*65}")
    print(" AIRLINE SUPPORT TICKET ANALYSIS REPORT")
    print(f"{'='*65}")
    print(f"Total tickets analyzed: {total_tickets}")
    print(f"Tickets in high/medium deflection categories: {total_deflectable}")
    print(f"Estimated total AI cost savings: ${total_savings:,.2f}")
    print(f"\n{'─'*65}")
    print(f"{'Category':<20} {'Vol':>4} {'Avg Hrs':>8} {'FCR%':>6} {'Deflect':>8} {'Savings':>10}")
    print(f"{'─'*65}")
    for cat, r in sorted(results.items(), key=lambda x: -x[1]["volume"]):
        print(
            f"{cat:<20} {r['volume']:>4} {r['avg_resolution_hours']:>8.1f} "
            f"{r['first_contact_resolution_pct']:>6.1f} {r['deflection_opportunity']:>8} "
            f"${r['estimated_ai_savings_usd']:>9,.2f}"
        )
    print(f"{'─'*65}\n")


def build_dashboard(results, total_savings, total_deflectable, total_tickets):
    cats = sorted(results.keys())
    volumes = [results[c]["volume"] for c in cats]
    avg_res = [results[c]["avg_resolution_hours"] for c in cats]
    fcr = [results[c]["first_contact_resolution_pct"] for c in cats]

    deflection_color = {"high": "#22c55e", "medium": "#f59e0b", "low": "#ef4444"}
    deflection_badge = {
        "high": '<span class="badge badge-high">HIGH</span>',
        "medium": '<span class="badge badge-medium">MEDIUM</span>',
        "low": '<span class="badge badge-low">LOW</span>',
    }

    table_rows = ""
    for cat in sorted(results.keys(), key=lambda c: -results[c]["volume"]):
        r = results[cat]
        table_rows += f"""
        <tr>
          <td><strong>{cat.title()}</strong></td>
          <td class="num">{r['volume']}</td>
          <td class="num">{r['avg_resolution_hours']}h</td>
          <td class="num">{r['first_contact_resolution_pct']}%</td>
          <td class="center">{deflection_badge[r['deflection_opportunity']]}</td>
          <td class="num savings">${r['estimated_ai_savings_usd']:,.0f}</td>
          <td class="rationale">{r['deflection_rationale']}</td>
        </tr>"""

    chart_data = json.dumps({
        "categories": cats,
        "volumes": volumes,
        "avg_resolution": avg_res,
        "fcr": fcr,
        "deflection_colors": [deflection_color[results[c]["deflection_opportunity"]] for c in cats],
        "savings": [results[c]["estimated_ai_savings_usd"] for c in cats],
    })

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Airline Support Ticket Analyzer</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      min-height: 100vh;
    }}

    header {{
      background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
      border-bottom: 1px solid #1e40af44;
      padding: 2rem 2.5rem;
    }}
    header h1 {{
      font-size: 1.75rem;
      font-weight: 700;
      color: #f8fafc;
      letter-spacing: -0.02em;
    }}
    header p {{
      color: #94a3b8;
      margin-top: 0.25rem;
      font-size: 0.9rem;
    }}
    .header-badge {{
      display: inline-block;
      background: #1e40af;
      color: #bfdbfe;
      font-size: 0.7rem;
      font-weight: 600;
      padding: 0.2rem 0.6rem;
      border-radius: 9999px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 0.5rem;
    }}

    main {{ padding: 2rem 2.5rem; max-width: 1400px; margin: 0 auto; }}

    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }}
    .kpi-card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 1.25rem 1.5rem;
    }}
    .kpi-card .label {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #64748b;
      margin-bottom: 0.4rem;
    }}
    .kpi-card .value {{
      font-size: 2rem;
      font-weight: 700;
      color: #f8fafc;
      line-height: 1;
    }}
    .kpi-card .sub {{
      font-size: 0.78rem;
      color: #94a3b8;
      margin-top: 0.35rem;
    }}
    .kpi-card.accent-green {{ border-color: #16a34a55; }}
    .kpi-card.accent-green .value {{ color: #4ade80; }}
    .kpi-card.accent-blue {{ border-color: #2563eb55; }}
    .kpi-card.accent-blue .value {{ color: #60a5fa; }}
    .kpi-card.accent-amber {{ border-color: #d9770655; }}
    .kpi-card.accent-amber .value {{ color: #fbbf24; }}

    .charts-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
      margin-bottom: 2rem;
    }}
    @media (max-width: 900px) {{ .charts-grid {{ grid-template-columns: 1fr; }} }}

    .chart-card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 1.5rem;
    }}
    .chart-card h2 {{
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #64748b;
      margin-bottom: 1rem;
    }}
    .chart-container {{ position: relative; height: 240px; }}

    .chart-card.wide {{
      grid-column: 1 / -1;
    }}

    .table-card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 1.5rem;
      overflow-x: auto;
      margin-bottom: 2rem;
    }}
    .table-card h2 {{
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #64748b;
      margin-bottom: 1.25rem;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.875rem;
    }}
    thead th {{
      text-align: left;
      padding: 0.6rem 0.75rem;
      color: #94a3b8;
      font-weight: 600;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      border-bottom: 1px solid #334155;
    }}
    tbody tr {{
      border-bottom: 1px solid #1e293b;
      transition: background 0.15s;
    }}
    tbody tr:hover {{ background: #263248; }}
    tbody td {{
      padding: 0.75rem 0.75rem;
      vertical-align: top;
      color: #cbd5e1;
    }}
    td.num {{ text-align: right; font-variant-numeric: tabular-nums; color: #e2e8f0; }}
    td.center {{ text-align: center; }}
    td.savings {{ color: #4ade80; font-weight: 600; }}
    td.rationale {{ color: #94a3b8; font-size: 0.8rem; max-width: 320px; }}

    .badge {{
      display: inline-block;
      font-size: 0.65rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      padding: 0.2rem 0.55rem;
      border-radius: 9999px;
      text-transform: uppercase;
    }}
    .badge-high   {{ background: #14532d; color: #86efac; }}
    .badge-medium {{ background: #78350f; color: #fcd34d; }}
    .badge-low    {{ background: #7f1d1d; color: #fca5a5; }}

    footer {{
      text-align: center;
      color: #475569;
      font-size: 0.75rem;
      padding: 2rem;
    }}
  </style>
</head>
<body>

<header>
  <div class="header-badge">Internal Analytics</div>
  <h1>✈ Airline Support Ticket Analyzer</h1>
  <p>AI deflection opportunity analysis &amp; cost savings estimation &mdash; {total_tickets} tickets analyzed</p>
</header>

<main>

  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="label">Total Tickets</div>
      <div class="value">{total_tickets}</div>
      <div class="sub">Across all categories</div>
    </div>
    <div class="kpi-card accent-green">
      <div class="label">Est. AI Cost Savings</div>
      <div class="value">${total_savings:,.0f}</div>
      <div class="sub">Based on $15/ticket human cost</div>
    </div>
    <div class="kpi-card accent-blue">
      <div class="label">Deflectable Tickets</div>
      <div class="value">{total_deflectable}</div>
      <div class="sub">High + medium deflection categories</div>
    </div>
    <div class="kpi-card accent-amber">
      <div class="label">Deflection Rate</div>
      <div class="value">{round(total_deflectable/total_tickets*100)}%</div>
      <div class="sub">Of total volume is automatable</div>
    </div>
  </div>

  <div class="charts-grid">

    <div class="chart-card">
      <h2>Ticket Volume by Category</h2>
      <div class="chart-container">
        <canvas id="volumeChart"></canvas>
      </div>
    </div>

    <div class="chart-card">
      <h2>First Contact Resolution Rate (%)</h2>
      <div class="chart-container">
        <canvas id="fcrChart"></canvas>
      </div>
    </div>

    <div class="chart-card">
      <h2>Average Resolution Time (Hours)</h2>
      <div class="chart-container">
        <canvas id="resolutionChart"></canvas>
      </div>
    </div>

    <div class="chart-card">
      <h2>Estimated AI Savings by Category ($)</h2>
      <div class="chart-container">
        <canvas id="savingsChart"></canvas>
      </div>
    </div>

  </div>

  <div class="table-card">
    <h2>Full Category Breakdown</h2>
    <table>
      <thead>
        <tr>
          <th>Category</th>
          <th style="text-align:right">Volume</th>
          <th style="text-align:right">Avg Resolution</th>
          <th style="text-align:right">FCR Rate</th>
          <th style="text-align:center">AI Deflection</th>
          <th style="text-align:right">Est. Savings</th>
          <th>Rationale</th>
        </tr>
      </thead>
      <tbody>{table_rows}
      </tbody>
    </table>
  </div>

</main>

<footer>Generated by analyze.py &mdash; Data: tickets.csv &mdash; Cost assumption: $15 per human-handled ticket</footer>

<script>
const DATA = {chart_data};

const FONT = {{ family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", size: 12 }};
const GRID_COLOR = "rgba(148,163,184,0.1)";
const TICK_COLOR = "#64748b";

Chart.defaults.color = TICK_COLOR;
Chart.defaults.font = FONT;

function baseBarOptions(indexAxis) {{
  return {{
    indexAxis: indexAxis || "x",
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{}} }} }},
    scales: {{
      x: {{ grid: {{ color: GRID_COLOR }}, ticks: {{ color: TICK_COLOR }} }},
      y: {{ grid: {{ color: GRID_COLOR }}, ticks: {{ color: TICK_COLOR }} }},
    }},
  }};
}}

// Volume chart
new Chart(document.getElementById("volumeChart"), {{
  type: "bar",
  data: {{
    labels: DATA.categories.map(c => c.split(" ").map(w => w[0].toUpperCase()+w.slice(1)).join(" ")),
    datasets: [{{
      data: DATA.volumes,
      backgroundColor: "#3b82f6cc",
      borderColor: "#3b82f6",
      borderWidth: 1,
      borderRadius: 4,
    }}]
  }},
  options: {{
    ...baseBarOptions(),
    plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: ctx => ` ${{ctx.raw}} tickets` }} }} }},
  }},
}});

// FCR chart
new Chart(document.getElementById("fcrChart"), {{
  type: "bar",
  data: {{
    labels: DATA.categories.map(c => c.split(" ").map(w => w[0].toUpperCase()+w.slice(1)).join(" ")),
    datasets: [{{
      data: DATA.fcr,
      backgroundColor: DATA.deflection_colors.map(c => c + "cc"),
      borderColor: DATA.deflection_colors,
      borderWidth: 1,
      borderRadius: 4,
    }}]
  }},
  options: {{
    ...baseBarOptions(),
    plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: ctx => ` ${{ctx.raw}}%` }} }} }},
    scales: {{
      x: {{ grid: {{ color: GRID_COLOR }}, ticks: {{ color: TICK_COLOR }} }},
      y: {{ grid: {{ color: GRID_COLOR }}, ticks: {{ color: TICK_COLOR, callback: v => v + "%" }}, max: 100 }},
    }},
  }},
}});

// Resolution time chart
new Chart(document.getElementById("resolutionChart"), {{
  type: "bar",
  data: {{
    labels: DATA.categories.map(c => c.split(" ").map(w => w[0].toUpperCase()+w.slice(1)).join(" ")),
    datasets: [{{
      data: DATA.avg_resolution,
      backgroundColor: "#8b5cf6cc",
      borderColor: "#8b5cf6",
      borderWidth: 1,
      borderRadius: 4,
    }}]
  }},
  options: {{
    ...baseBarOptions(),
    plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: ctx => ` ${{ctx.raw}}h` }} }} }},
    scales: {{
      x: {{ grid: {{ color: GRID_COLOR }}, ticks: {{ color: TICK_COLOR }} }},
      y: {{ grid: {{ color: GRID_COLOR }}, ticks: {{ color: TICK_COLOR, callback: v => v + "h" }} }},
    }},
  }},
}});

// Savings chart
new Chart(document.getElementById("savingsChart"), {{
  type: "bar",
  data: {{
    labels: DATA.categories.map(c => c.split(" ").map(w => w[0].toUpperCase()+w.slice(1)).join(" ")),
    datasets: [{{
      data: DATA.savings,
      backgroundColor: "#22c55ecc",
      borderColor: "#22c55e",
      borderWidth: 1,
      borderRadius: 4,
    }}]
  }},
  options: {{
    ...baseBarOptions(),
    plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: ctx => ` $${{ctx.raw.toLocaleString()}}` }} }} }},
    scales: {{
      x: {{ grid: {{ color: GRID_COLOR }}, ticks: {{ color: TICK_COLOR }} }},
      y: {{ grid: {{ color: GRID_COLOR }}, ticks: {{ color: TICK_COLOR, callback: v => "$" + v }} }},
    }},
  }},
}});
</script>
</body>
</html>"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    tickets = load_tickets(CSV_FILE)
    results, total_savings, total_deflectable, total_tickets = analyze(tickets)
    print_report(results, total_savings, total_deflectable, total_tickets)
    build_dashboard(results, total_savings, total_deflectable, total_tickets)
    print(f"Dashboard saved to {OUTPUT_HTML}")
