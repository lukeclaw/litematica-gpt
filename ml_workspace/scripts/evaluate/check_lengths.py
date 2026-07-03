import json
from transformers import AutoTokenizer

def check_3000_coverage():
    input_file = "dataset/synthetic_train_rationalized.jsonl"
    tokenizer = AutoTokenizer.from_pretrained("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")
    
    counts = {1024: 0, 2048: 0, 3000: 0, 4096: 0}
    total = 0
    
    with open(input_file, 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
                assistant_content = next(m["content"] for m in data["messages"] if m["role"] == "assistant")
                if "<Thinking>" in assistant_content and "<DSL>" in assistant_content:
                    thinking = assistant_content.split("</Thinking>")[0].replace("<Thinking>", "").strip()
                    dsl = assistant_content.split("<DSL>")[1].split("</DSL>")[0].strip()
                    full_text = f"system\nCompiler\nuser\n{thinking}\nassistant\n{dsl}"
                    
                    tokens = len(tokenizer.encode(full_text))
                    total += 1
                    for limit in counts:
                        if tokens <= limit:
                            counts[limit] += 1
            except: continue
            
    print(f"Total valid samples: {total}")
    for limit, count in counts.items():
        print(f"Under {limit} tokens: {count} samples ({count/total*100:.1f}%)")

if __name__ == "__main__":
    check_3000_coverage()
