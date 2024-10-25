import yaml
import plotly.graph_objects as go
import os
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
    os.makedirs('layouts/partials/custom', exist_ok=True)

    # Create partial HTML file
    partial_file = f'layouts/partials/custom/{name}-http.html'
    with open(partial_file, 'w') as file:
        file.write(f"""<div>
  {{ partial "graph" . }}
</div>
""")

    # Save graph as HTML file
    fig.write_html(f'layouts/partials/custom/{name}-http.html')
