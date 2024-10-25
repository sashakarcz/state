import yaml
import requests
from datetime import datetime
import os

# Load the config.yml file
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize the start time
start_time = datetime.utcnow().isoformat()

# Function to generate or update a markdown file for HTTP issues
def update_issue_markdown(name, url, expected_statuses, actual_status, status):
    # Define filename for the markdown file in content/issues/
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    file_path = f"content/issues/{date_str}-{name}-http.md"
    is_resolved = (status == "up")
    
    # Content of the markdown file
    markdown_content = f"""---
title: HTTP Status {'resolved' if is_resolved else 'incorrect'} for {name}
date: {datetime.utcnow().isoformat()}
resolved: {is_resolved}
resolvedWhen: {'null' if not is_resolved else datetime.utcnow().isoformat()}
severity: {"down" if status == "down" else "notice"}
affected:
  - {name}
section: issue
---

| Expected Statuses | Actual Status  |
|-------------------|----------------|
| {', '.join(map(str, expected_statuses))} | {actual_status} |
"""
    # Write or update the markdown file
    with open(file_path, 'w') as md_file:
        md_file.write(markdown_content)

# Function to run an HTTP status check
def run_http_check(name, url, expected_statuses):
    print(f"Running HTTP check for {name} (URL: {url}, Expected: {expected_statuses})")
    try:
        # Send HTTP request with a 5-second timeout
        response = requests.get(url, timeout=5)
        actual_status = response.status_code

        # Determine if the HTTP check passed or failed
        status = "up" if actual_status in expected_statuses else "down"
        
        # Update or create markdown file for the issue
        update_issue_markdown(name, url, expected_statuses, actual_status, status)

        # Save individual domain result to its respective YAML file
        os.makedirs('history', exist_ok=True)
        with open(f'history/{name}.yml', 'w') as domain_file:
            yaml.dump({
                "url": url,
                "status": status,
                "code": actual_status,
                "responseTime": response.elapsed.total_seconds(),
                "lastUpdated": datetime.utcnow().isoformat(),
                "startTime": start_time,
                "result": actual_status,
                "expected": expected_statuses,
                "generator": "HTTP Checker"
            }, domain_file, default_flow_style=False)

        return {
            "name": name,
            "actual": actual_status,
            "expected": expected_statuses,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status.capitalize()
        }

    except requests.exceptions.Timeout:
        print(f"HTTP check for {name} timed out.")
        # Log timeout as an error in the markdown file
        update_issue_markdown(name, url, expected_statuses, "Timeout", "down")
        return None

# Iterate over entries in the systems section and filter for HTTP checks
for entry in config['params']['systems']:
    if entry.get('http', False):  # Check for http: true
        name = entry['name']
        url = entry.get("link", None)
        expected_statuses = entry.get('expected_status', [200])  # Default to status 200 if unspecified

        # Run the HTTP check
        run_http_check(name, url, expected_statuses)

print("HTTP check completed. Markdown files updated for issues.")
