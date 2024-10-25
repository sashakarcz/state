import yaml
import subprocess
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

# Function to generate or update a markdown file for DNS issues
def update_issue_markdown(domain, expected_record, actual_record, status):
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    file_path = f"content/issues/{date_str}-{domain}.md"
    is_resolved = (status == "up")
    start_time = get_existing_start_time(file_path) if not is_resolved else datetime.utcnow().isoformat()

    markdown_content = f"""---
title: DNS Record {'incorrect' if not is_resolved else 'resolved'} for {domain}
date: {start_time}
resolved: {is_resolved}
resolvedWhen: {'null' if not is_resolved else datetime.utcnow().isoformat()}
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

# Function to run a DNS check
def run_dns_check(domain, expected_record, record_type):
    print(f"Running DNS check for {domain} (Type: {record_type}, Expected: {expected_record})")
    try:
        result = subprocess.check_output(["dig", "+short", domain, record_type], text=True).strip().splitlines()
        result = result if result else ["No record found"]
        status = "up" if set(result) == set(expected_record) else "down"
        update_issue_markdown(domain, expected_record, result, status)

    except subprocess.CalledProcessError as e:
        print(f"Error during DNS check for {domain}: {str(e)}")
        update_issue_markdown(domain, expected_record, ["Error"], "down")

# Check DNS entries in config.yml
for entry in config['params']['systems']:
    if entry.get("dns", False):  # Run only if 'dns: true' is set
        domain = entry['domain']
        expected_record = entry.get('expected_record', [])
        record_type = entry.get('record_type', "A")
        run_dns_check(domain, expected_record, record_type)

print("DNS check completed.")
