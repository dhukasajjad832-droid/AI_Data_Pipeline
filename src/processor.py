import json


with open("data/raw_data.json", "r", encoding="utf-8") as file:
    data = json.load(file)


print("Total records:", len(data))

for item in data:
    print("\nWebsite:", item["url"])
    print("Clean Title:", item["title"])

    print("Headings:")
    for heading in item["headings"]:
        print("-", heading)

    print("Paragraphs:")
    for paragraph in item["paragraphs"]:
        print("-", paragraph)