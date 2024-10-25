import yaml
import requests
from datetime import datetime
import zoneinfo
import os

# Load config.yml
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize start time
utc = zoneinfo.ZoneInfo('UTC')
start_time = datetime.now(utc).isoformat()

# Function to generate/update markdown file for HTTP issues
def update_issue_markdown(name, url, expected_statuses, actual_status, status, resolved_start_time=None):
    date_str = datetime.now(utc).strftime("%Y-%m-%d")
    file_path = f"content/issues/{date_str}-{name}-http.md"
    is_resolved = (status == "up")

    markdown_content = f"""---
title: HTTP Status {'resolved' if is_resolved else 'incorrect'} for {name}
date: {datetime.now(utc).isoformat()}
resolved: {is_resolved}
resolvedWhen: {'null' if not is_resolved else datetime.now(utc).isoformat()}
resolvedStartTime: {'null' if not is_resolved or resolved_start_time is None else resolved_start_time}
severity: {"down" if status == "down" else "notice"}
affected:
  - {name}
section: issue
---

| Expected Statuses | Actual Status  |
|-------------------|----------------|
| {', '.join(map(str, expected_statuses))} | {actual_status} |
"""
    with open(file_path, 'w') as md_file:
        md_file.write(markdown_content)

# Function to run HTTP status check
def run_http_check(name, url, expected_statuses):
    print(f"Running HTTP check for {name} (URL: {url}, Expected: {expected_statuses})")
    try:
        response = requests.get(url, timeout=5)
        actual_status = response.status_code

        status = "up" if actual_status in expected_statuses else "down"

        try:
            with open(f'history/{name}.yml', 'r') as domain_file:
                existing_data = yaml.safe_load(domain_file)
        except FileNotFoundError:
            existing_data = {
                'url': url,
                'status': None,
                'history': [],
                'resolved': False,
                'resolvedWhen': None,
                'resolvedStartTime': None
            }

        # Ensure required keys exist
        existing_data.setdefault('history', [])
        existing_data.setdefault('resolved', False)
        existing_data.setdefault('resolvedWhen', None)
        existing_data.setdefault('resolvedStartTime', None)

        history_entry = {
            'timestamp': datetime.now(utc).isoformat(),
            'status': status,
            'actualStatus': actual_status,
            'responseTime': response.elapsed.total_seconds(),
            'type': 'http'
        }
        existing_data['history'].append(history_entry)

        existing_data['status'] = status
        if status == "up" and not existing_data['resolved']:
            existing_data['resolved'] = True
            existing_data['resolvedStartTime'] = datetime.now(utc).isoformat()
            existing_data['resolvedWhen'] = datetime.now(utc).isoformat()
        elif status == "down" and existing_data['resolved']:
            existing_data['resolved'] = False
            existing_data['resolvedStartTime'] = None
            existing_data['resolvedWhen'] = None

        os.makedirs('history', exist_ok=True)
        with open(f'history/{name}.yml', 'w') as domain_file:
            yaml.dump(existing_data, domain_file, default_flow_style=False)

        update_issue_markdown(name, url, expected_statuses, actual_status, status, existing_data.get('resolvedStartTime'))

    except requests.RequestException as e:
        print(f"Error during HTTP check for {name}: {str(e)}")
        update_issue_markdown(name, url, expected_statuses, "Error", "down")

# Iterate over entries in systems section and filter HTTP checks
for entry in config['params']['systems']:
    if 'link' in entry:
        name = entry['name']
        url = entry['link']
        expected_statuses = entry.get('expected_status', [200])

        if not isinstance(expected_statuses, list):
            expected_statuses = [expected_statuses]

        run_http_check(name, url, expected_statuses)

print("HTTP check completed. Markdown files updated for issues.")
