import json


def extract_startup(text):
    """
    Convert raw text into structured startup data.
    """

    startup = {
        "schemaVersion": "1.0",
        "recordType": "STARTUP",
        "source": {
            "name": "LLM Extractor",
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

    return startup


sample_text = """
OpenAI develops artificial intelligence systems and products.
"""

result = extract_startup(sample_text)

print(json.dumps(result, indent=4))