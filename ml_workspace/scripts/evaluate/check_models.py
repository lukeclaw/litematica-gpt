import vertexai
from vertexai.generative_models import GenerativeModel

PROJECT_ID = "project-04a53d5f-b875-4835-856"
LOCATION = "us-west1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

# This is a hacky way to check what's available by trying a few common IDs
models_to_test = [
    "gemini-3.1-pro-preview",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-3.0-flash",
    "gemini-pro"
]

print("Testing model availability...")
for m in models_to_test:
    try:
        model = GenerativeModel(m)
        # Try a tiny generation to see if it's actually there
        response = model.generate_content("hi", generation_config={"max_output_tokens": 1})
        print(f"[OK] {m} is available.")
    except Exception as e:
        print(f"[FAIL] {m}: {e}")
