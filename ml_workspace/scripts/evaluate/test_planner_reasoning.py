import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

def test_planner(building_name):
    model_path = "mlx-community/gemma-4-e4b-it-4bit"
    adapter_path = "specialized_skills/gemma4_planner_lora"
    
    print(f"Loading Master Planner (Checkpoint 500)...")
    model, tokenizer = load(model_path, adapter_path=adapter_path)
    
    system_prompt = (
        "ROLE: You are the Lead Litematica DSL Architect. "
        "MISSION: Construct a step-by-step spatial rationale based on the provided building name.\n\n"
        "SPATIAL RATIONALE STRUCTURE:\n"
        "1. **FOOTPRINT ANALYSIS**: Define the bounding box (X, Y, Z). Describe the structure's overall shape and orientation.\n"
        "2. **MATERIAL STRATEGY**: List every block type and assign it a unique 1-character key (A, B, C...). Explain the choice for each material.\n"
        "3. **CONSTRUCTION SEQUENCE**: Walk through the build layer-by-layer (Y=0, Y=1...). Explain the logic of where blocks are placed."
    )
    
    messages = [{"role": "user", "content": f"{system_prompt}\n\nBuild the {building_name}."}]
    full_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    print(f"--- GENERATING REASONING FOR: {building_name} ---")
    sampler = make_sampler(temp=0.1)
    generate(model, tokenizer, prompt=full_prompt, max_tokens=2000, verbose=True, sampler=sampler)

if __name__ == "__main__":
    test_planner("Replica Stanley Water Bottle")
