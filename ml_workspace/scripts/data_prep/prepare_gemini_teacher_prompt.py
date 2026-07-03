import os
import json

def prepare_gemini_prompt(subset_size=10):
    src_dir = "dataset/dsl_10kb"
    files = [f for f in os.listdir(src_dir) if f.endswith('.txt')][:subset_size]
    
    prompt = (
        "I am training a 'student' model to build Minecraft structures using a custom DSL. "
        "I need you to act as the 'Teacher'. For each DSL file below, provide a 'Spatial Monologue' "
        "that explains the architectural logic step-by-step BEFORE providing the code.\n\n"
        "FORMAT FOR EACH EXAMPLE:\n"
        "---EXAMPLE START---\n"
        "Intent: [Name of the building]\n"
        "Rationale: [Your step-by-step spatial breakdown of how to build this structure]\n"
        "DSL Output: [The original code provided below]\n"
        "---EXAMPLE END---\n\n"
        "DATASET FILES:\n"
    )
    
    for filename in files:
        name = filename.split(" - ")[-1].replace(".txt", "")
        with open(os.path.join(src_dir, filename), 'r') as f:
            code = f.read()
        prompt += f"\nFILE: {name}\nCODE:\n{code}\n"
    
    with open("gemini_teacher_request.txt", "w") as f:
        f.write(prompt)
    
    print("Done! Open 'gemini_teacher_request.txt' and paste it into Gemini 1.5 Pro.")

if __name__ == "__main__":
    prepare_gemini_prompt()
