import yaml
import subprocess
from datetime import datetime
import zoneinfo
import os

# Load config.yml
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize start time
utc = zoneinfo.ZoneInfo('UTC')
start_time = datetime.now(utc).replace(microsecond=0).isoformat() + 'Z'

# Function to generate/update markdown file for DNS issues
def update_issue_markdown(domain, expected_record, actual_record, status, resolved_start_time=None):
    date_str = datetime.now(utc).strftime("%Y-%m-%d")
    file_path = f"content/issues/{date_str}-{domain}-dns.md"
    is_resolved = (status == "up")

    markdown_content = f"""---
title: DNS Record {'resolved' if is_resolved else 'incorrect'} for {domain}
date: {datetime.now(utc).replace(microsecond=0).isoformat()}Z
resolved: {is_resolved}
resolvedWhen: {'null' if not is_resolved else datetime.now(utc).replace(microsecond=0).isoformat() + 'Z'}
resolvedStartTime: {'null' if not is_resolved or resolved_start_time is None else resolved_start_time}
severity: {"down" if status == "down" else "notice"}
affected:
  - {domain}
section: issue
---

| Expected Record  | Actual Record  |
|------------------|----------------|
| {', '.join(expected_record)} | {', '.join(actual_record)} |
"""
    with open(file_path, 'w') as md_file:
        md_file.write(markdown_content)

# Function to run DNS check
def run_dns_check(domain, expected_record, record_type, url=None):
    print(f"Running DNS check for {domain} (Type: {record_type}, Expected: {expected_record})")
    try:
        result = subprocess.check_output(["dig", "+short", domain, record_type], text=True).strip().splitlines()

        if not result:
            result = ["No record found"]

        status = "up" if set(result) == set(expected_record) else "down"

        try:
            with open(f'history/{domain}.yml', 'r') as domain_file:
                existing_data = yaml.safe_load(domain_file)
        except FileNotFoundError:
            existing_data = {
                'url': url or f"http://{domain}",
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
            'timestamp': datetime.now(utc).replace(microsecond=0).isoformat() + 'Z',
            'status': status,
            'result': result,
            'expected': expected_record,
            'type': 'dns'
        }
        existing_data['history'].append(history_entry)

        existing_data['status'] = status
        if status == "up" and not existing_data['resolved']:
            current_time_iso = datetime.now(utc).replace(microsecond=0).isoformat() + 'Z'
            existing_data['resolved'] = True
            existing_data['resolvedStartTime'] = current_time_iso
            existing_data['resolvedWhen'] = current_time_iso
        elif status == "down" and existing_data['resolved']:
            existing_data['resolved'] = False
            existing_data['resolvedStartTime'] = None
            existing_data['resolvedWhen'] = None

        os.makedirs('history', exist_ok=True)
        with open(f'history/{domain}.yml', 'w') as domain_file:
            yaml.dump(existing_data, domain_file, default_flow_style=False)

        update_issue_markdown(domain, expected_record, result, status, existing_data.get('resolvedStartTime'))

    except subprocess.CalledProcessError as e:
        print(f"Error during DNS check for {domain}: {str(e)}")
        update_issue_markdown(domain, expected_record, ["Error"], "down")

# Iterate over entries in systems section and filter DNS checks
for entry in config['params']['systems']:
    if 'domain' in entry:
        domain = entry['domain']
        expected_record = entry.get('expected_record', [])
        record_type = entry.get('record_type', 'A')  # Default to A record

        if not isinstance(expected_record, list):
            expected_record = [expected_record]

        run_dns_check(domain, expected_record, record_type)

print("DNS check completed. Markdown files updated for issues.")
