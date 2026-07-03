from transformers import AutoTokenizer
import json

tokenizer = AutoTokenizer.from_pretrained("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")

# 1. From our test script
system_prompt = "You are a Minecraft DSL Compiler. Translate the architectural plan into raw DSL code."
user_prompt = "Build a Small Stone Vault"
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
]
test_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

# 2. From training data (first example)
train_sample = {
    "messages": [
        {"role": "system", "content": "You are a Minecraft DSL Compiler. Translate the architectural plan into raw DSL code."},
        {"role": "user", "content": "I will construct the Castle Gate model..."},
        {"role": "assistant", "content": "palette..."}
    ]
}
train_prompt = tokenizer.apply_chat_template(train_sample["messages"][:-1], tokenize=False, add_generation_prompt=True)

print("--- TEST PROMPT (end) ---")
print(repr(test_prompt[-20:]))
print("--- TRAIN PROMPT (end) ---")
print(repr(train_prompt[-20:]))
