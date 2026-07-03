from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset
import os

# 1. Configuration
# Using the Gemma 4 Effective 4B (E4B) model optimized for memory efficiency
model_name = "unsloth/gemma-4-e4b-bnb-4bit" 
max_seq_length = 8192 # Gemma 4 supports up to 128k, but 8k is plenty for DSLs
dataset_path = "dataset/full_train_sparse.jsonl"
output_dir = "litematica_gemma4_e4b"

# 2. Load Model & Tokenizer
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    max_seq_length = max_seq_length,
    load_in_4bit = True,
)

# 3. Add LoRA Adapters
# We target the core attention and MLP layers to teach it the Minecraft DSL
model = FastLanguageModel.get_peft_model(
    model,
    r = 32, # Higher rank for better structural learning
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 32,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
)

# 4. Prepare Dataset with Gemma 4 Chat Template
def formatting_prompts_func(examples):
    instructions = examples["messages"]
    texts = []
    for msg_list in instructions:
        # Gemma 4 has native system prompt support
        text = tokenizer.apply_chat_template(msg_list, tokenize = False, add_generation_prompt = False)
        texts.append(text)
    return { "text" : texts, }

dataset = load_dataset("json", data_files = dataset_path, split = "train")
dataset = dataset.map(formatting_prompts_func, batched = True)

# 5. Trainer Configuration
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    args = TrainingArguments(
        per_device_train_batch_size = 8, # E4B is small, so we can use a larger batch on 24GB
        gradient_accumulation_steps = 2,
        warmup_steps = 10,
        max_steps = 500, # Increased steps for the larger 4k dataset
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
        save_total_limit = 2,
        report_to = "none",
    ),
)

# 6. Start Training
print("Starting fine-tuning on Gemma 4 E4B...")
trainer.train()

# 7. Save the Fine-Tuned Model
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
print(f"Fine-tuned model saved to {output_dir}")

# 8. Export to GGUF for local use (LM Studio / Ollama)
print("Exporting to GGUF (Q4_K_M)...")
model.save_pretrained_gguf(output_dir + "_gguf", tokenizer, quantization_method = "q4_k_m")
print(f"GGUF model saved to {output_dir}_gguf")
