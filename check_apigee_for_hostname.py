import requests
import sys

def main(hostname):
    api_url = "https://apigee.googleapis.com/v1/organizations/booming-pride-432710-j9/environments/eval/targetservers"
    access_token = "ya29.a0AeDClZD_65drha1I_qTv-QFq7Vf4K54H0YhYes4K9SpvE1rvqQJL7If23iw1homnsokwn-kePB2BHcAze8E5c8-PJFVIlf09KmQTX0VvxYiHnVVjBJLnbi9rxoszCFZInLH4oaGll3bqgKT3svo1qcuWLnBWX3LUxlewfrZcWVd9zFPgOVAsChoZc0wqBWyGzk3Qr6mCo_QcaOv-w90ubTsRUJ-nmg0OsKsSpqZVMrHvbXGxGdbxVV9KyUZJj5bSMTIJbIbPCTU_se6UDHEeTNw-fsqNimw1k12s_deicf47gGfGVV5RPA0wNuSG_PcgUzXI0UraCAVWJWWAO_n1phaBj3qR9FBnLYIFg1QQxuaR0SZ3f--7Wx-ecSgun7EVqns5-s31IMnSlQmMXw2vpzOEgoA6uR5hCg0aCgYKAesSARESFQHGX2MidP32_W2b6Hwd-noJTwvvvw0426"

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
