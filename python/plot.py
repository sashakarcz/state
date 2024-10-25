import yaml
import plotly.graph_objects as go

# Load YAML data
with open('history/example.com.yml', 'r') as file:
    data = yaml.safe_load(file)

# Extract up/down state history
history = data['history']
up_down_states = [entry['status'] for entry in history]

# Create Plotly graph
fig = go.Figure(data=[go.Scatter(
    x=list(range(len(up_down_states))),
    y=[1 if state == 'up' else 0 for state in up_down_states],
    mode='lines+markers'
)])

# Customize graph
fig.update_layout(
    title='Up/Down State History',
    xaxis_title='Time',
    yaxis_title='State',
    yaxis=dict(range=[0, 1.1])
)

# Save graph as HTML file
fig.write_html('up_down_graph.html')
