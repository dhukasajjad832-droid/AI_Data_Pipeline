import json


def validate_result(result):
    required_fields = [
        "schemaVersion",
        "recordType",
        "source",
        "content"
    ]

    return all(field in result for field in required_fields)


def fallback_extractor(text):
    return {
        "schemaVersion": "1.0",
        "recordType": "STARTUP",
        "source": {
            "name": "Fallback Extractor",
            "url": None
        },
        "content": {
            "entityName": None,
            "data": {
                "description": text.strip(),
                "employeeCount": None
            }
        },
        "collectedAt": "2026-09-10T00:00:00Z"
    }


def extract_with_llm(text):
    print("Primary LLM unavailable.")
    print("Using fallback extractor...")

    result = fallback_extractor(text)

    if validate_result(result):
        return result

    raise ValueError("Invalid extraction result")


sample_text = """
OpenAI develops artificial intelligence systems and products.
"""

result = extract_with_llm(sample_text)

print(json.dumps(result, indent=4))