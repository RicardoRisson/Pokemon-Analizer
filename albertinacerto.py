import pandas as pd
import numpy as np
import torch
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from datasets import Dataset

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🚀 Utilizando: {device} | GPU: {torch.cuda.get_device_name(0)}")

# 1. CARREGAMENTO
df = pd.read_csv("dataset_filtrado_final.csv")
df['label'] = (df['ano'] >= 2022).astype(int)
df['text'] = "TITULO: " + df['titulo'].fillna('') + " [SEP] ABSTRACT: " + df['abstract'].fillna('')
df = df.dropna(subset=['text'])

train_df, val_df = train_test_split(df, test_size=0.2, stratify=df['label'], random_state=42)

# Criando datasets e garantindo a coluna de label
train_dataset = Dataset.from_pandas(train_df.reset_index(drop=True))
val_dataset = Dataset.from_pandas(val_df.reset_index(drop=True))

# 2. TOKENIZAÇÃO
model_name = "PORTULAN/albertina-ptbr-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)

def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)

tokenized_train = train_dataset.map(tokenize_function, batched=True)
tokenized_val = val_dataset.map(tokenize_function, batched=True)

# 3. MODELO E TREINO
# Forçando o modelo a carregar em float32 para evitar o erro de overflow
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2, torch_dtype=torch.float32)

save_path = "./modelo_albertina_final" 

training_args = TrainingArguments(
    output_dir="./resultados_tmp",
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=1e-5,
    per_device_train_batch_size=8, # Reduzi um pouco para garantir estabilidade em float32
    gradient_accumulation_steps=4, # Mantém o batch efetivo em 32
    num_train_epochs=3,
    weight_decay=0.01,
    load_best_model_at_end=True,
    fp16=False,    # DESATIVADO para evitar o erro de overflow
    logging_dir='./logs',
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
)

# 4. EXECUÇÃO
print("🔥 Iniciando Fine-Tuning (Modo de Estabilidade)...")
trainer.train()

# 5. SALVAMENTO
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)
print(f"✅ Treino concluído! Modelo salvo em: {save_path}")
