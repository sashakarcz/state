import yaml
import subprocess
from datetime import datetime
import os

# Load the .upptimerc.yml file
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize the results array
start_time = datetime.utcnow().isoformat()  # Start time for all checks

# Function to generate or update a markdown file for issues
def update_issue_markdown(domain, expected_record, actual_record, status):
    # Set filename for the markdown file in content/issues/
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    file_path = f"content/issues/{date_str}-{domain}-dns.md"
    is_resolved = (status == "up")
    
    # Set content of the markdown file
    markdown_content = f"""---
title: DNS Record {'incorrect' if not is_resolved else 'resolved'} for {domain}
date: {datetime.utcnow().isoformat()}
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
    # Write or update markdown file
    with open(file_path, 'w') as md_file:
        md_file.write(markdown_content)

# Function to run a DNS check
def run_dns_check(domain, expected_record, record_type, url=None):
    print(f"Running DNS check for {domain} (Type: {record_type}, Expected: {expected_record})")
    try:
        # Run the dig command to get the DNS record
        result = subprocess.check_output(["dig", "+short", domain, record_type], text=True).strip().splitlines()

        if not result:
            result = ["No record found"]

        # Determine if the DNS check passed or failed
        status = "up" if set(result) == set(expected_record) else "down"
        
        # Update or create markdown file for the issue
        update_issue_markdown(domain, expected_record, result, status)
        
        # Save individual domain result to its respective YAML file
        os.makedirs('history', exist_ok=True)
        with open(f'history/{domain}.yml', 'w') as domain_file:
            yaml.dump({
                "url": url or f"http://{domain}",
                "status": status,
                "code": 1 if status == "up" else 0,
                "responseTime": 0,
                "lastUpdated": datetime.utcnow().isoformat(),
                "startTime": start_time,
                "result": result,
                "expected": expected_record,
                "generator": "DNS Checker"
            }, domain_file, default_flow_style=False)

        return {
            "domain": domain,
            "actual": result,
            "expected": expected_record,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status.capitalize()
        }

    except subprocess.CalledProcessError as e:
        print(f"Error during DNS check for {domain}: {str(e)}")
        # Handle the error by creating a markdown file with error details
        update_issue_markdown(domain, expected_record, ["Error"], "down")
        return None

# Iterate over entries in the systems section and filter DNS checks
for entry in config['params']['systems']:
    if 'domain' in entry:  # Check for DNS-specific keys
        domain = entry['domain']
        expected_record = entry.get('expected_record', [])
        record_type = entry.get('record_type', "A")  # Default to A record if unspecified
        url = entry.get("url", None)

        # Run the DNS check
        run_dns_check(domain, expected_record, record_type, url)

print("DNS check completed. Markdown files updated for issues.")
