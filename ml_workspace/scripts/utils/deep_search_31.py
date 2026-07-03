import vertexai
from vertexai.generative_models import GenerativeModel
import google.api_core.exceptions

PROJECT_ID = "project-04a53d5f-b875-4835-856"

# Locations to try
locations = ["us-central1", "us-west1", "us-east5", "us-east4", "global"]

print(f"Searching for gemini-3.1-pro-preview...")

for loc in locations:
    try:
        print(f"Testing location: {loc}...")
        vertexai.init(project=PROJECT_ID, location=loc)
        model = GenerativeModel("gemini-3.1-pro-preview")
        response = model.generate_content("hi", generation_config={"max_output_tokens": 1})
        print(f"!!! SUCCESS !!! gemini-3.1-pro-preview is available in {loc}")
        break
    except Exception as e:
        print(f"   [FAIL] {loc}: {e}")

print("Search complete.")
