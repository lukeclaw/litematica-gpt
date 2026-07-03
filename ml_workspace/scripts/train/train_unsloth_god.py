from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset
import os

# 1. Configuration - GOD MODE
model_name = "unsloth/meta-llama-3.1-8b-instruct-bnb-4bit"
max_seq_length = 8192 
load_in_4bit = True

# 2. Load Model & Tokenizer
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    max_seq_length = max_seq_length,
    load_in_4bit = load_in_4bit,
)

# 3. Add LoRA Adapters (Ultra-High Rank 256 for Architectural Godhood)
model = FastLanguageModel.get_peft_model(
    model,
    r = 256, 
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 512,
    lora_dropout = 0, 
    bias = "none",    
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
)

# 4. Dataset Preparation
def formatting_prompts_func(examples):
    instructions = examples["messages"]
    texts = []
    for msg_list in instructions:
        text = tokenizer.apply_chat_template(msg_list, tokenize = False, add_generation_prompt = False)
        texts.append(text)
    return { "text" : texts, }

# Expects train.jsonl in the same folder
dataset = load_dataset("json", data_files = "train.jsonl", split = "train")
dataset = dataset.map(formatting_prompts_func, batched = True,)

# 5. Trainer
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    args = TrainingArguments(
        per_device_train_batch_size = 2, 
        gradient_accumulation_steps = 4,
        warmup_steps = 10,
        max_steps = 6000, 
        learning_rate = 1e-4, # Slightly lower LR for high rank stability
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
        save_total_limit = 2,
        save_steps = 500,
    ),
)

# 6. Train
print("Starting GOD MODE Unsloth Training on A6000...")
trainer.train()

# 7. Save the Finished Skill
model.save_pretrained("minecraft_god_compiler")
tokenizer.save_pretrained("minecraft_god_compiler")
print("GOD MODE Training Complete. Weights saved to 'minecraft_god_compiler'")
