# Hugging Face Hub Deployment Plan

## Repository Setup Strategy

**Decision: Separate Repositories (Recommended)**
- Datasets and models have different lifecycles
- Dataset updates don't require model version bumps
- Better access control granularity
- Easier discoverability and independent versioning

### Structure:
- project-model/ - Model repository (weights, config, model card)
- project-dataset/ - Dataset repository (data, dataset card)

## File Organization

### Model Repository:
- README.md (from model-card.md)
- config.json
- generation_config.json
- model/safetensors/bf16/
- model/safetensors/q4/
- model/gguf/
- .gitignore

### Dataset Repository:
- README.md (from dataset-card.md)
- dataset_info.json
- data/train.jsonl
- data/validation.jsonl
- .gitignore

## Configuration Files

### model/config.json:
{
  "architectures": ["YourModelArchitecture"],
  "hidden_size": 4096,
  "num_attention_heads": 32,
  "num_hidden_layers": 28,
  "max_position_embeddings": 2048,
  "vocab_size": 32000
}

### dataset/dataset_info.json:
{
  "dataset_name": "Your Dataset",
  "task_categories": ["question-answering"],
  "license": "your-license"
}

## Upload Commands

### Create Repositories:
```bash
huggingface-cli repo create project-model --type model --private false
huggingface-cli repo create project-dataset --type dataset --private false
```

### Upload Model:
```bash
cd project-model
git remote add origin https://huggingface.co/your-username/project-model
cp -r ../model/* model/
cp ../config.json .
cp ../generation_config.json .
cp ../docs/huggingface/model-card.md README.md
git add . && git commit -m "Initial release"
git push -u origin main
```

### Upload Dataset:
```bash
cd ../project-dataset
git remote add origin https://huggingface.co/datasets/your-username/project-dataset
cp -r ../data data/
cp ../docs/huggingface/dataset-card.md README.md
cp ../dataset_info.json .
git add . && git commit -m "Initial release"
git push -u origin main
```

## Testing
```python
from transformers import AutoModel, AutoTokenizer
from datasets import load_dataset

# Test model
model = AutoModel.from_pretrained("your-username/project-model")
tokenizer = AutoTokenizer.from_pretrained("your-username/project-model")

# Test dataset
dataset = load_dataset("your-username/project-dataset")
```
