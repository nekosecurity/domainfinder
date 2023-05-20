
# Description
It happens sometimes to have only ip during penetration tests and tools generally propose to do bruteforce on the vhosts to identify them

Most OSINT tools need a domain to achieve successful information gathering
This tool has a different approach as it only focuses on OSINT results based on IP addresses.

**No API key is required** but some are supported

## Example
* Differents input

```bash
poetry run domainfinder 8.8.8.8 -m rapiddns censys
poetry run domainfinder 8.8.8.8/24
poetry run domainfinder 8.8.8.8-12
poetry run domainfinder ip_list.txt
```
* Define scope domain

```bash
poetry run domainfinder 8.8.8.8 --scope google.com

[Scope: google.com]
google-public-dns-a.google.com
dns.google.com

poetry run domainfinder 8.8.8.8 --scope google.com --show-outofscope

[Scope: google.com]
dns.google.com
google-public-dns-a.google.com

[Out Of Scope]
testing.agentesgyt.com.gt
movistarcloud.com
ameenphotography.com
```

## Notes
Thanks to Crackmapexec for the functionality to provide different types of input as target. I shamelessly stole it

## Public API / website
- AlienVault
- Censys: Support w/ w/o API
- HackerTarget
- RapidDNS
- Shodan: Support w/ w/o API 
- ThreatMiner
- UrlScan: Support w/ w/o API
- ViewDNS: Support w/ w/o API. **Warning: This method is not really appreciate. You risk having your IP address banned**. It's recommanded to use the API instead.

## Todo
- [ ] Refactoring
  - Async model
  - Errors management
  - Output message
- [ ] Rate limit
- [ ] More file format (csv)
- [ ] Add more API 
  - Fofa
  - VirusTotal: Tricky without an account
  - dnslytics: Find out why a 403 is sent via python-requests
