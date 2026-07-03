import vertexai
from vertexai.generative_models import GenerativeModel
import time

PROJECT_ID = "project-04a53d5f-b875-4835-856"
locations = ["us-central1", "us-west1", "us-east4"]
model_ids = ["gemini-3.1-flash-preview", "gemini-3.1-flash"]

print("Probing regions for Gemini 3.1 Flash...")

for loc in locations:
    for mid in model_ids:
        try:
            print(f"Testing {mid} in {loc}...")
            vertexai.init(project=PROJECT_ID, location=loc)
            model = GenerativeModel(mid)
            # Short probe
            response = model.generate_content("hi", generation_config={"max_output_tokens": 1})
            print(f"!!! SUCCESS !!! {mid} is available in {loc}")
            exit(0) # Stop at first success
        except Exception as e:
            if "404" in str(e):
                print(f"   [404] Not in {loc}")
            else:
                print(f"   [ERROR] {loc}: {str(e)[:50]}...")
        time.sleep(0.5)
