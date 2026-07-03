import vertexai
from vertexai.generative_models import GenerativeModel
import os

PROJECT_ID = "project-04a53d5f-b875-4835-856"
LOCATION = "global"
MODEL_NAME = "gemini-3.1-pro-preview"

vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel(MODEL_NAME)

try:
    print(f"Testing {MODEL_NAME} in {LOCATION}...")
    response = model.generate_content("hello", generation_config={"max_output_tokens": 5})
    print(f"Success: {response.text}")
except Exception as e:
    print(f"FAILED: {e}")
