import json


with open("data/raw_data.json", "r", encoding="utf-8") as file:
    websites = json.load(file)


startup_records = []

for website in websites:
    startup = {
        "schemaVersion": "1.0",
        "recordType": "STARTUP",
        "source": {
            "name": "Web Crawler",
            "url": website["url"]
        },
        "content": {
            "entityName": website["title"],
            "data": {
                "employeeCount": None
            }
        },
        "collectedAt": "2026-09-10T00:00:00Z"
    }

    startup_records.append(startup)


print(json.dumps(startup_records, indent=4))