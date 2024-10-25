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

# Function to add or update the date field in markdown files
def add_or_update_date(lines):
    # Check if the date field is present; update or insert it
    found_date = False
    for i, line in enumerate(lines):
        if line.startswith("date:"):
            found_date = True
            lines[i] = f"date: {datetime.now(utc).isoformat()}"
    if not found_date:
        # Insert date after the front matter start
        lines.insert(1, f"date: {datetime.now(utc).isoformat()}")
    return lines

# Iterate over systems in config
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

    # Customize graph layout
    fig.update_layout(
        title=f'Up/Down State History for {name}',
        xaxis_title='Time (UTC)',
        yaxis_title='State',
        yaxis=dict(range=[0, 1.1])
    )

    # Create directories if they don't exist
    os.makedirs('content/issues', exist_ok=True)
    os.makedirs('layouts/partials/custom', exist_ok=True)

    # Create partial HTML file for linking the graph
    partial_file = f'layouts/partials/custom/{name}-http.html'
    with open(partial_file, 'w') as file:
        file.write(f"""<div>
  {{ partial "graph" . }}
</div>
""")

    # Save graph as HTML file
    fig.write_html(f'content/issues/{name}-http.html')

    # Update or create the markdown file with date
    date_str = timestamps[-1][:10]  # Extract date from latest timestamp
    markdown_file = f'content/issues/{date_str}-{name}-http.md'
    try:
        with open(markdown_file, 'r') as file:
            markdown_content = file.read().splitlines()
    except FileNotFoundError:
        # Initialize empty front matter if file not found
        markdown_content = ["---", "---"]

    # Ensure the date is correctly set
    markdown_content = add_or_update_date(markdown_content)

    # Add link to the graph if it's not already in the markdown content
    link = f'[Up/Down State History Graph]({name}-http.html)'
    if link not in markdown_content:
        markdown_content.append(f'\n\n{link}')

    # Write updated content back to markdown file
    with open(markdown_file, 'w') as file:
        file.write("\n".join(markdown_content))

    print(f"Updated markdown for {name}.")

print("Script executed successfully.")
