import vertexai
from vertexai.generative_models import GenerativeModel
import time

PROJECT_ID = "project-04a53d5f-b875-4835-856"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

# Exhaustive list of 2025/2026 models and common aliases
models_to_test = [
    "gemini-3.1-pro-preview",
    "gemini-3.1-flash-preview",
    "gemini-3.1-flash-lite-preview",
    "gemini-3.0-pro",
    "gemini-3.0-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-pro-exp-0205",
    "gemini-2.0-flash-001",
    "gemini-1.5-pro-002",
    "gemini-1.5-flash-002",
    "gemini-pro",
    "gemini-flash"
]

print(f"Testing model availability in {LOCATION}...")
for m in models_to_test:
    try:
        model = GenerativeModel(m)
        # Try a tiny generation to see if it's actually there
        response = model.generate_content("hi", generation_config={"max_output_tokens": 1})
        print(f"[OK] {m} is available.")
    except Exception as e:
        # Check if the error is 404 (not found) or something else (like auth/quota)
        if "404" in str(e):
            print(f"[NOT FOUND] {m}")
        else:
            print(f"[ERROR] {m}: {str(e)[:100]}...")
    time.sleep(0.5) # Avoid hitting rate limits during the check
