# Arquitetura OCI Specialist LLM: Plano de Melhorias (V2)

Este documento contém a visão arquitetural e as propostas de melhorias priorizadas para o projeto OCI Specialist LLM, com foco em elevar o modelo de um "Oráculo Estático" para um "Consultor Interativo" robusto e integrado.

## 1. Evolução do Dataset: De "Oráculo Estático" para "Consultor Interativo" (Multi-turn)
**O Problema:** Atualmente, a geração de dados foca em interações de turno único (`system` -> `user` -> `assistant`).
**O Impacto:** O modelo será ótimo para responder perguntas diretas ("Como crio uma VCN?"), mas falhará em sessões de *troubleshooting* ("Criei a VCN, mas o ping não passa. E agora?").
**A Solução (Arquitetural):**
*   Refatorar o gerador para criar cadeias de diálogo (2 a 5 turnos).
*   Introduzir um fluxo onde o "usuário" comete um erro de configuração comum em OCI, e o "assistente" diagnostica passo a passo, refletindo o formato de lista de `messages` (padrão ChatML) no JSONL.

## 2. Integração do "Semantic Scorer" no Pipeline Principal (Qualidade)
**O Problema:** O script atual de avaliação usa expressões regulares (regex), o que é frágil. Se o modelo gerar uma resposta perfeitamente correta, mas usar um sinônimo não mapeado, ele será penalizado.
**O Impacto:** Falsos negativos na avaliação.
**A Solução (Fluxo):**
*   Substituir ou complementar a avaliação baseada em regex no script `unified_evaluation.py`.
*   Usar os embeddings do `paraphrase-MiniLM-L6-v2` (já implementado no `semantic_scorer.py`) para validar se a semântica da resposta do modelo se alinha com a resposta de referência.

## 3. Ajuste Fino da Deduplicação Semântica (Curadoria de Dados)
**O Problema:** A deduplicação semântica (`dedupe_embedding.py`) foi desabilitada no pipeline (`prepare_data.sh`) por ser "muito agressiva".
**O Impacto:** O dataset de treino pode estar inchado com perguntas semanticamente idênticas escritas de formas levemente diferentes, causando *overfitting* e desperdiçando tempo de treino.
**A Solução (Investigação):**
*   Calibrar o limiar (*threshold*) do cosine similarity no script de embeddings (ex: aumentando o threshold para ~0.95).
*   Reativá-lo no `prepare_data.sh` para garantir um dataset menor, porém com diversidade de alta qualidade.

## 4. Preparação do Terreno para o RAG (Integração de Sistemas)
**O Problema:** Dados voláteis (preços, cotas, novos serviços) mudam rapidamente, deixando o modelo obsoleto.
**O Impacto:** Perda de confiabilidade em informações temporais.
**A Solução (Próximo Passo Lógico):**
*   Criar um novo módulo no projeto (ex: `src/retrieval/`) responsável por:
    1.  Fazer o *crawl* da documentação oficial do OCI.
    2.  Fazer o *chunking* e *embedding*.
    3.  Salvar em um banco de vetores leve localmente (ex: ChromaDB ou FAISS).
*   Isso prepara a arquitetura para que o modelo GGUF atue como o "cérebro" sobre dados injetados em tempo real.

## 5. Automação do Loop de Inferência / CI-CD do Modelo
**O Problema:** A inferência é atualmente um teste manual.
**O Impacto:** Perda de tempo em testes exploratórios após cada ciclo de treino.
**A Solução:**
*   Criar um script `inference_runner.py` que carregue o adaptador LoRA recém-treinado, leia um arquivo de *holdout prompts* (perguntas não vistas), gere as respostas em batch e exporte para um HTML lado-a-lado com as respostas do modelo base.
