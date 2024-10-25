import yaml
import requests
from datetime import datetime
import os

# Load the config.yml file
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

# Function to get the start time from an existing issue file
def get_existing_start_time(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith("date: "):
                    return line.split("date: ")[1].strip()
    return datetime.utcnow().isoformat()

# Function to generate or update a markdown file for HTTP issues
def update_issue_markdown(name, expected_status, actual_status, status):
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    file_path = f"content/issues/{date_str}-{name}.md"
    is_resolved = (status == "up")
    start_time = get_existing_start_time(file_path) if not is_resolved else datetime.utcnow().isoformat()

    markdown_content = f"""---
title: HTTP Status {'incorrect' if not is_resolved else 'resolved'} for {name}
date: {start_time}
resolved: {is_resolved}
resolvedWhen: {'null' if not is_resolved else datetime.utcnow().isoformat()}
severity: {"down" if status == "down" else "notice"}
affected:
  - {name}
section: issue
---

| Expected Status | Actual Status |
|-----------------|--------------|
| {', '.join(map(str, expected_status))} | {actual_status} |
"""
    with open(file_path, 'w') as md_file:
        md_file.write(markdown_content)

# Function to run an HTTP check
def run_http_check(name, url, expected_status):
    print(f"Running HTTP check for {name} (URL: {url}, Expected: {expected_status})")
    try:
        response = requests.get(url, timeout=5)
        actual_status = response.status_code
        status = "up" if actual_status in expected_status else "down"
        update_issue_markdown(name, expected_status, str(actual_status), status)

    except requests.RequestException as e:
        print(f"Error during HTTP check for {name}: {str(e)}")
        update_issue_markdown(name, expected_status, "Error", "down")

# Check HTTP entries in config.yml
for entry in config['params']['systems']:
    if entry.get("http", False):  # Run only if 'http: true' is set
        name = entry['name']
        url = entry.get('link')
        expected_status = entry.get('expected_status', [])
        if url and expected_status:
            run_http_check(name, url, expected_status)

print("HTTP check completed.")
