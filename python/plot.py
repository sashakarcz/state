import yaml
import plotly.graph_objects as go
import os
from datetime import datetime, timezone
import zoneinfo

# Load config.yml
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize UTC timezone
utc = zoneinfo.ZoneInfo('UTC')

# Iterate over systems
for system in config['params']['systems']:
    name = system['name']
    domain = system.get('domain', name)

    # Load YAML data
    try:
        with open(f'history/{domain}.yml', 'r') as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"No history file found for {domain}. Skipping...")
        continue

    # Extract up/down state history
    history = data.get('history', [])
    up_down_states = [entry['status'] for entry in history]
    timestamps = [entry['timestamp'] for entry in history]

    # Create Plotly graph
    fig = go.Figure(data=[go.Scatter(
        x=timestamps,
        y=[1 if state == 'up' else 0 for state in up_down_states],
        mode='lines+markers'
    )])

    # Customize graph
    fig.update_layout(
        title=f'Up/Down State History for {name}',
        xaxis_title='Time (UTC)',
        yaxis_title='State',
        yaxis=dict(range=[0, 1.1])
    )

    # Create directories if they don't exist
    os.makedirs('content/issues', exist_ok=True)
    os.makedirs('layouts/partials/custom', exist_ok=True)

    # Save graph as HTML file
    fig.write_html(f'content/issues/{name}-http.html')

    # Update or create markdown file
    date_str = timestamps[-1][:10] if timestamps else datetime.now(utc).strftime("%Y-%m-%d")
    markdown_file = f'content/issues/{date_str}-{name}-http.md'
    try:
        with open(markdown_file, 'r') as file:
            markdown_content = file.read()
    except FileNotFoundError:
        markdown_content = ""

    # Add the HTML embed if it's not already present
    embed_code = f"""{{% rawhtml %}}
<embed src="./{name}-http.html" type="text/html">
{{% /rawhtml %}}"""
    if embed_code not in markdown_content:
        markdown_content += f"\n\n{embed_code}"

    # Ensure the date is in UTC ISO 8601 format for CState
    updated_date = datetime.now(timezone.utc).isoformat()
    if "date:" in markdown_content:
        lines = markdown_content.splitlines()
        for i, line in enumerate(lines):
            if line.startswith('date:'):
                lines[i] = f'date: {updated_date}'
                break
        markdown_content = '\n'.join(lines)
    else:
        markdown_content = f"date: {updated_date}\n" + markdown_content

    # Write updated markdown content
    with open(markdown_file, 'w') as file:
        file.write(markdown_content)

print("Plotting and markdown updates completed.")
