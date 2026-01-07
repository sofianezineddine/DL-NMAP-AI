from transformers import T5Tokenizer, T5ForConditionalGeneration, TrainingArguments, Trainer
from datasets import load_dataset
from peft import LoraConfig, get_peft_model

# 1. Load our student (T5-small) and their translator (Tokenizer)
model_name = "t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# 2. Configure the "Study Technique" (LoRA)
lora_config = LoraConfig(
    r=8, # The size of the "cheat sheet"
    lora_alpha=32,
    target_modules=["q", "v"], # Which parts of the brain to focus on
    lora_dropout=0.05,
    task_type="SEQ_2_SEQ_LM" # We are translating Sequence to Sequence
)

# Apply LoRA to our model
model = get_peft_model(model, lora_config)

# 3. Load our textbook (Dataset)
# For this guide, we assume you have 'nmap_dataset.json' ready
dataset = load_dataset("json", data_files="nmap_dataset.json")

# 4. Prepare the data for the model
def preprocess_function(examples):
    inputs = ["translate English to Nmap: " + doc for doc in examples["input"]]
    
    # We preprocess inputs and outputs at the same time
    model_inputs = tokenizer(
        inputs, 
        max_length=128, 
        truncation=True, 
        padding="max_length",
        text_target=examples["output"] # <--- This replaces the 'with' block
    )
    
    return model_inputs

tokenized_dataset = dataset.map(preprocess_function, batched=True)

# 5. Set the Training Rules
training_args = TrainingArguments(
    output_dir="./nmap-ai-model",
    per_device_train_batch_size=4,
    num_train_epochs=3, # How many times to read the textbook
    learning_rate=3e-4,
    logging_steps=10,
    save_strategy="epoch"
)

# 6. Start the Training!
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
)

print("Starting training... This may take a few minutes.")
trainer.train()

# 7. Save the trained model
model.save_pretrained("./nmap-ai-final")
print("Training complete! Your AI is now an Nmap expert.")