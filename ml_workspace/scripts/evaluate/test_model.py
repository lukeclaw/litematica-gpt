import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

def test_minecraft_distill(prompt_text):
    model_path = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
    adapter_path = "adapters" 

    print(f"Loading Distilled Llama 3.1 8B...")
    model, tokenizer = load(model_path, adapter_path=adapter_path)

    system_prompt = "You are a Minecraft Architect. Think step-by-step before building."
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Build a {prompt_text}"}
    ]
    
    full_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    print(f"Generating architecture for: {prompt_text}...\n" + "="*20)
    
    # Use Temp 0.7 for more "flow"
    sampler = make_sampler(temp=0.7)
    
    generate(
        model, 
        tokenizer, 
        prompt=full_prompt, 
        max_tokens=2500, 
        verbose=True,
        sampler=sampler
        # No repetition penalty for this test
    )

if __name__ == "__main__":
    test_minecraft_distill("admin shoppe")
