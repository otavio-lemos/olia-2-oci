import chainlit as cl
import requests
import json
import os
from io import BytesIO
from urllib.parse import urlparse

# URL do seu backend RAG FastAPI (ajuste se rodar em porta diferente)
API_URL = "http://localhost:8000"

@cl.on_chat_start
async def start():
    # Inicializa o estado da sessão com a estratégia padrão do YAML
    cl.user_session.set("strategy", "default")
    
    # Criar botões de configuração (Settings) na UI do Chainlit
    settings = await cl.ChatSettings(
        [
            cl.input_widget.Select(
                id="strategy",
                label="RAG Strategy / Agent Profile",
                values=["default", "migracao", "configuracao", "troubleshooting"],
                initial_index=0,
            )
        ]
    ).send()
    
    await cl.Message(
        content="🚀 **OCI Copilot Inicializado!**\n\nSou seu agente especialista em Oracle Cloud. Você pode fazer perguntas ou **anexar arquivos (txt, md, json, csv)** para que eu os analise."
    ).send()

@cl.on_settings_update
async def setup_agent(settings):
    # Atualiza a estratégia do RAG quando o usuário mudar o dropdown na UI
    cl.user_session.set("strategy", settings["strategy"])
    await cl.Message(content=f"⚙️ Perfil alterado para: **{settings['strategy']}**").send()

@cl.on_message
async def main(message: cl.Message):
    # 1. TRATAR ANEXOS (File Uploads)
    files = message.elements
    file_content = ""
    
    if files:
        for file in files:
            try:
                with open(file.path, "r", encoding="utf-8") as f:
                    content = f.read()
                    file_content += f"\n\n--- Conteúdo do arquivo {file.name} ---\n{content}\n--- Fim do arquivo ---\n"
            except Exception as e:
                await cl.Message(content=f"❌ Erro ao ler arquivo {file.name}: {str(e)}").send()
                
        if file_content:
            await cl.Message(content=f"📎 *Li {len(files)} arquivo(s). Adicionando ao contexto da sua pergunta...*").send()

    # 2. MONTAR A CONSULTA PARA A API
    strategy = cl.user_session.get("strategy")
    query = message.content
    
    if file_content:
        query = f"Pergunta: {query}\n\nContexto fornecido pelo usuário:{file_content}"

    docs = []
    async with cl.Step(name="Retrieving OCI Docs (RAG)", type="tool") as step:
        step.input = {"query": query, "strategy": strategy}
        
        try:
            response = requests.post(
                f"{API_URL}/rag/retrieve",
                json={"query": query, "k": 5, "strategy": strategy},
                timeout=15 # Evita travar a UI caso a API caia
            )
            response.raise_for_status()
            data = response.json()
            docs = data.get("documents", [])
            
            if not docs:
                step.output = "Nenhum documento encontrado nos índices para essa consulta."
            else:
                context_text = "\n\n".join([
                    f"📄 **{doc.get('metadata', {}).get('title', 'Documento')}**\n"
                    f"*URL/Origem:* {doc.get('metadata', {}).get('url', 'N/A')}\n"
                    f"{doc.get('content', '')[:250]}..."
                    for doc in docs
                ])
                step.output = f"Recuperados {len(docs)} chunks.\n\n{context_text}"
                
        except requests.exceptions.RequestException as e:
            step.output = f"Erro de conexão com API RAG: {str(e)}"
            step.is_error = True
            await cl.Message(content=f"⚠️ **Erro crítico:** Não foi possível conectar ao backend FastAPI (porta 8000).").send()
            return

    # 3. GERAR RESPOSTA FINAL DO AGENTE (Preparado para Stream de LLM)
    final_msg = cl.Message(content="")
    await final_msg.send() # Envia a mensagem vazia primeiro para começar o stream
    
    if docs:
        resposta_inicial = f"Baseado no perfil `{strategy}` e nos {len(docs)} documentos OCI analisados...\n\n"
        await final_msg.stream_token(resposta_inicial)
        
        # TODO: No futuro, substituir o bloco abaixo pela chamada real do Llama 3 via MLX ou llama.cpp
        # Exemplo real:
        # for token in llm_generate_stream(prompt=query, context=docs):
        #     await final_msg.stream_token(token)
        
        mock_llm_stream = [
            "Esta ", "é ", "uma ", "resposta ", "estrutural ", "do ", "Chainlit.\n",
            "Quando ", "seu ", "modelo ", "terminar ", "de ", "treinar, ",
            "os ", "tokens ", "reais ", "do ", "Llama 3 ", "aparecerão ", "aqui!"
        ]
        
        import asyncio
        for token in mock_llm_stream:
            await final_msg.stream_token(token)
            await asyncio.sleep(0.05) # Efeito visual de digitação
            
    else:
        await final_msg.stream_token("Não encontrei referências na base de conhecimento para te ajudar com isso.")
        
    await final_msg.update()
    
    # 4. CRIAR AÇÕES EXECUTÁVEIS (Action Buttons)
    if strategy in ["execucao", "migracao", "default"]:
        actions = [
            cl.Action(
                name="validate_terraform",
                value="terraform_code",
                description="Validar código gerado com CLI",
                label="🛠️ Validar Arquivo Localmente",
            )
        ]
        await cl.Message(content="Deseja executar alguma ação baseada no plano acima?", actions=actions).send()

@cl.action_callback("validate_terraform")
async def on_action(action: cl.Action):
    # Quando o usuário clica no botão "Validar Arquivo com OCI CLI"
    
    async with cl.Step(name="Terminal Execution", type="run") as step:
        step.input = "oci compute instance list --compartment-id ..."
        
        # Aqui o Python acessa o SO nativamente. 
        # Ex: import subprocess; result = subprocess.run(["oci", "--version"], capture_output=True)
        # Mock do resultado para a UI:
        mock_cli_output = "Action completed: OCI CLI version 3.37.1\nCompartment validated successfully."
        
        step.output = mock_cli_output
    
    await cl.Message(content=f"✅ Comando executado com sucesso na máquina local!").send()
