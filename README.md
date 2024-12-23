# Adding New Systems to Status Dashboard
## To add a new system for reporting, follow these steps:

1. Open config.yml: In your project root, locate and open the config.yml file where the monitoring configuration is defined.

2 .Locate the Systems Section: The systems configuration is nested under params. Find the systems list within params, which looks like this:

```yaml
params:
  systems:
    - name: Example System
      category: Uncategorized
      domain: example.com
      expected_record:
        - 192.0.2.1
      record_type: A
      expected_status: [200, 301, 302]
```

3. Add a New System: Each system requires several fields to define what the DNS checker will monitor. Add a new entry under systems with the following details:

| Variable | Description |
|----------|-------------|
| name | A unique identifier for this system, which will be displayed in status reports. |
| category | The category this system belongs to. Categories help organize systems by groups, such as "Backend" or "User-Facing Services." Categories are case-sensitive and must match exactly if used in multiple entries. |
|domain | The domain name to monitor for DNS correctness. |
| expected_record | A list of expected IP addresses (or other DNS records) that this domain should resolve to. |
| record_type (optional) | The type of DNS record to check, such as A, CNAME, or MX. Defaults to A if not specified. |
| link (optional) | A URL for additional information about this system. |
| expected_status (optional) | A list of http status codes that are acceptable for determining that the site is operational. |


Example Configuration: Here’s an example of adding a new system named “Media Proxy”:

```yaml
params:
  systems:
    - name: Media Proxy
      category: CDN
      domain: mediaproxy.example.com
      expected_record:
        - 203.0.113.5
        - 203.0.113.6
      record_type: A
      link: https://mediaproxy.example.com
      expected_status: [200, 301, 302]
```
This configuration sets up checks for `mediaproxy.example.com`, expecting it to resolve to IP addresses `203.0.113.5` and `203.0.113.6`, and marks it as up for http statuses `[200, 301, 302]`.

> [!TIP]
> Important Notes
> 
> Case Sensitivity: Ensure the category names and other fields match exactly if referenced elsewhere.
> 
> YAML Formatting: Maintain consistent YAML indentation and format to avoid parsing errors.
