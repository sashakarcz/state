import yaml
import plotly.graph_objects as go
import os
import subprocess
from datetime import datetime
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
        xaxis_title='Time',
        yaxis_title='State',
        yaxis=dict(range=[0, 1.1])
    )

    # Create directory if it doesn't exist
    os.makedirs('content/issues', exist_ok=True)

    # Save graph as HTML file
    fig.write_html(f'content/issues/{name}-http.html')

    # Add link to graph in markdown file
    date_str = timestamps[-1][:10]  # Get date from latest timestamp
    markdown_file = f'content/issues/{date_str}-{name}-http.md'
    try:
        with open(markdown_file, 'r') as file:
            markdown_content = file.read()
    except FileNotFoundError:
        print(f"No markdown file found for {name}. Skipping...")
        continue

    # Update date field
    updated_date = datetime.now(utc).strftime("%Y-%m-%dT%H:%M:%SZ")
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
