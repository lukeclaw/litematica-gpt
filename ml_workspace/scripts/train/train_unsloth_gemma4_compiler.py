from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM
from transformers import TrainingArguments
from datasets import load_dataset
import os

# 1. Configuration
model_name = "google/gemma-4-E4B-it"
max_seq_length = 8192 
load_in_4bit = True

# 2. Load Model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    max_seq_length = max_seq_length,
    load_in_4bit = load_in_4bit,
)

# 3. LoRA
model = FastLanguageModel.get_peft_model(
    model,
    r = 128, 
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 256,
    lora_dropout = 0, 
    bias = "none",    
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
)

# 4. Dataset with PROMPT MASKING
def formatting_prompts_func(examples):
    instructions = examples["messages"]
    texts = []
    for msg_list in instructions:
        text = tokenizer.apply_chat_template(msg_list, tokenize = False, add_generation_prompt = False)
        texts.append(text)
    return { "text" : texts, }

dataset = load_dataset("json", data_files = "train.jsonl", split = "train")
dataset = dataset.map(formatting_prompts_func, batched = True,)

# Mask everything before the assistant response starts
# We look for the <start_of_turn>model\n sequence
response_template = "<start_of_turn>model\n"
collator = DataCollatorForCompletionOnlyLM(response_template=response_template, tokenizer=tokenizer)

# 5. Trainer
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    data_collator = collator, # APPLY MASKING HERE
    max_seq_length = max_seq_length,
    args = TrainingArguments(
        per_device_train_batch_size = 4, 
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 2000, 
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
        save_steps = 500,
    ),
)

# 6. Train
print("Starting PURE COMPILER Training (with Rationale Masking) on A6000...")
trainer.train()

# 7. Save
model.save_pretrained("minecraft_compiler_adapter")
tokenizer.save_pretrained("minecraft_compiler_adapter")
