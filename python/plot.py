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
    history = data['history']
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

    # Create partial HTML file for linking
    partial_file = f'layouts/partials/custom/{name}-http.html'
    with open(partial_file, 'w') as file:
        file.write(f"""<div>
  {{ partial "graph" . }}
</div>
""")

    # Save graph as HTML file
    fig.write_html(f'content/issues/{name}-http.html')

    # Update date field in markdown file
    date_str = timestamps[-1][:10]  # Get date from latest timestamp
    markdown_file = f'content/issues/{date_str}-{name}-http.md'
    try:
        with open(markdown_file, 'r') as file:
            markdown_content = file.read()
    except FileNotFoundError:
        print(f"No markdown file found for {name}. Skipping...")
        continue

    updated_date = datetime.now(timezone.utc).isoformat()  # Using timezone-aware datetime
    lines = markdown_content.splitlines()
    for i, line in enumerate(lines):
        if line.startswith('date:'):
            lines[i] = f'date: {updated_date}'
            break
    else:
        lines.insert(1, f'date: {updated_date}')
    markdown_content = '\n'.join(lines)

    # Add link to graph if it doesn't exist
    link = f'[Up/Down State History Graph]({name}-http.html)'
    if link not in markdown_content:
        markdown_content += f'\n\n{link}'

    # Write updated markdown content
    with open(markdown_file, 'w') as file:
        file.write(markdown_content)

print("Script completed. Graphs and markdown files updated.")
