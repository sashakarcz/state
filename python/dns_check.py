import yaml
import subprocess
from datetime import datetime
import re
import os

# Load the .upptimerc.yml file
with open('monitor.yml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize the results array
results = []
start_time = datetime.utcnow().isoformat()  # Start time for all checks

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
        code = 1 if status == "up" else 0
        response_time = 0  # Placeholder for response time (could be set if measured)

        # Generate the result dictionary for current domain
        domain_result = {
            "url": url or f"http://{domain}",
            "status": status,
            "code": code,
            "responseTime": response_time,
            "lastUpdated": datetime.utcnow().isoformat(),
            "startTime": start_time,
            "result": result,
            "expected": expected_record,
            "generator": "DNS Checker"
        }

        # Save individual domain result to its respective YAML file
        os.makedirs('history', exist_ok=True)
        with open(f'history/{domain}.yml', 'w') as domain_file:
            yaml.dump(domain_result, domain_file, default_flow_style=False)

        return {
            "domain": domain,
            "actual": result,
            "expected": expected_record,
            "timestamp": domain_result["lastUpdated"],
            "status": status.capitalize()
        }

    except subprocess.CalledProcessError as e:
        print(f"Error during DNS check for {domain}: {str(e)}")
        error_result = {
            "url": f"http://{domain}",
            "status": "error",
            "code": 0,
            "responseTime": 0,
            "lastUpdated": datetime.utcnow().isoformat(),
            "startTime": start_time,
            "result": ["Error"],
            "expected": expected_record,
            "generator": "DNS Checker"
        }

        # Write error result to individual domain YAML file
        with open(f'history/{domain}.yml', 'w') as domain_file:
            yaml.dump(error_result, domain_file, default_flow_style=False)

        return {
            "domain": domain,
            "actual": ["Error"],
            "expected": expected_record,
            "timestamp": error_result["lastUpdated"],
            "status": "Error"
        }

# Iterate over entries in the sites section and filter DNS checks
for entry in config['sites']:
    if 'domain' in entry:  # Check for DNS-specific keys
        domain = entry['domain']
        expected_record = entry.get('expected_record', [])
        record_type = entry.get('record_type', "A")  # Default to A record if unspecified
        url = entry.get("url", None)

        # Run the DNS check
        result = run_dns_check(domain, expected_record, record_type, url)
        readme_file.seek(0)
        results.append(result)
        readme_file.truncate()

# Write the results to a YAML file
with open('history/dns_results.yml', 'w') as outfile:
    yaml.dump(results, outfile, default_flow_style=False)

print("DNS check completed. Results written to history/dns_results.yml")

# Format results in markdown for Live DNS Status
dns_results_md = "## Live DNS Status\n\n| Domain           | Status     | Expected         | Actual           | Timestamp              |\n"
dns_results_md += "|------------------|------------|------------------|------------------|------------------------|\n"
for res in results:
    dns_results_md += f"| {res['domain']} | {res['status']} | {', '.join(res['expected'])} | {', '.join(res['actual'])} | {res['timestamp']} |\n"

# Update README.md in the Live DNS Status section
with open('README.md', 'w') as readme_file:
    # Insert new DNS status table
    readme_file.write(f"\n### DNS Check on {datetime.utcnow().isoformat()}\n\n")
    readme_file.write(dns_results_md)

# Write current results to dns_status.md
with open('history/dns_status.md', 'w') as status_file:
    status_file.write(f"\n### DNS Check on {datetime.utcnow().isoformat()}\n\n")
    status_file.write(dns_results_md)

print("DNS check completed. Results updated in README.md and appended to history/dns_status.md")
