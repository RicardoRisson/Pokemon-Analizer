import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
import numpy as np

# 1. CONFIGURAÇÕES
model_path = "./modelo_albertina_final"
dataset_path = "/scratch/rrmachado/dataset_filtrado_final.csv"

print("⏳ Carregando Albertina treinado...")
model = AutoModelForSequenceClassification.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

# Instancia a pipeline na GPU (device=0)
pipe = pipeline("text-classification", model=model, tokenizer=tokenizer, device=0)

# 2. PREPARAÇÃO DOS DADOS (IGUAL AO TREINO)
df = pd.read_csv(dataset_path)
df['label'] = (df['ano'] >= 2022).astype(int)
df['text'] = "TITULO: " + df['titulo'].fillna('') + " [SEP] ABSTRACT: " + df['abstract'].fillna('')

# Pegamos apenas os 20% de validação (Random State 42 para bater com o treino)
_, val_df = train_test_split(df, test_size=0.2, stratify=df['label'], random_state=42)

# 3. EXECUÇÃO DA INFERÊNCIA
print(f"🚀 Rodando inferência em {len(val_df)} exemplos de teste...")
texts = val_df['text'].tolist()
true_labels = val_df['label'].tolist()

# Rodamos a pipeline
results = pipe(texts, truncation=True, max_length=512, batch_size=16)

# Converte 'LABEL_0'/'LABEL_1' para 0/1
pred_labels = [int(res['label'].split('_')[1]) for res in results]

# 4. EXIBIÇÃO DOS RESULTADOS
print("\n" + "="*50)
print("📊 RELATÓRIO DE CLASSIFICAÇÃO - ALBERTINA")
print("="*50)
print(classification_report(true_labels, pred_labels, target_names=['Antigo (<2022)', 'Novo (>=2022)']))
print("="*50)
