import requests
import sys

def main(hostname):
    api_url = "https://apigee.googleapis.com/v1/organizations/booming-pride-432710-j9/environments/eval/targetservers"
    access_token = "YOUR_ACCESS_TOKEN"

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()

    servers = response.json()  # Assuming JSON response

    keywords = hostname.lower().split()
    matches = []
    for server in servers:
        normalized_name = ''.join(e for e in server if e.isalnum()).lower()
        if all(keyword in normalized_name for keyword in keywords):
            matches.append(server)

    if matches:
        for match in matches:
            print(match)
    else:
        print(f"No matching Target Server found for hostname: {hostname}")

if __name__ == "__main__":
    main(sys.argv[1])
