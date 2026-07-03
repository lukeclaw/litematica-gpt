import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

def run_agentic_minecraft_flow(user_request):
    model_path = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
    planner_adapter = "specialized_skills/spatial_distill_llama8b"
    compiler_adapter = "specialized_skills/dsl_compiler_llama8b"

    print(f"--- AGENTIC FLOW START ---")
    
    # 1. THE PLANNING PHASE
    print(f"\n[PHASE 1] Loading Master Planner...")
    model, tokenizer = load(model_path, adapter_path=planner_adapter)
    
    planner_prompt = (
        f"<|im_start|>system\nYou are a Minecraft Architect. Think step-by-step before building.<|im_end|>\n"
        f"<|im_start|>user\nBuild a {user_request}<|im_end|>\n"
        f"<|im_start|>assistant\n<Thinking>"
    )
    
    print(f"[PHASE 1] Generating Architectural Plan...")
    # Higher temperature for the planner to allow for creative design
    planner_sampler = make_sampler(temp=0.7)
    plan_output = generate(model, tokenizer, prompt=planner_prompt, max_tokens=1000, sampler=planner_sampler)
    
    # Extract the thinking part
    thinking_block = plan_output.split("</Thinking>")[0].strip()
    full_thinking = f"<Thinking>\n{thinking_block}\n</Thinking>"
    print(f"\n--- PLAN GENERATED ---\n{full_thinking}\n")

    # 2. THE COMPILATION PHASE
    print(f"\n[PHASE 2] Swapping to DSL Architect hat...")
    # In MLX, we can't easily hotswap adapters in the same load call yet without reloading, 
    # but reloading an 8B model on an M5 is nearly instant.
    model, tokenizer = load(model_path, adapter_path=compiler_adapter)
    
    compiler_prompt = (
        f"<|im_start|>system\nYou are a Minecraft DSL Compiler. Translate the architectural plan into raw DSL code.<|im_end|>\n"
        f"<|im_start|>user\n{thinking_block}<|im_end|>\n"
        f"<|im_start|>assistant\n<DSL>"
    )
    
    print(f"[PHASE 2] Compiling Plan to Litematica DSL...")
    # Temperature 0.0 for the compiler to ensure mathematical precision
    compiler_sampler = make_sampler(temp=0.0)
    dsl_output = generate(model, tokenizer, prompt=compiler_prompt, max_tokens=2048, sampler=compiler_sampler)
    
    final_dsl = dsl_output.split("</DSL>")[0].strip()
    print(f"\n--- FINAL DSL COMPILED ---\n{final_dsl}\n")
    
    return final_dsl

if __name__ == "__main__":
    run_agentic_minecraft_flow("admin shoppe")
