import chainlit as cl
import requests
import json
import os
import asyncio
import aiohttp
import subprocess
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# =======================
# Config Loading
# =======================
load_dotenv("chainlit.env")

RAG_API_URL = os.getenv("RAG_API_URL", "http://localhost:8000")
MLX_SERVER_URL = os.getenv("MLX_SERVER_URL", "http://localhost:8080")
MODEL_PATH = os.getenv("MODEL_PATH", "outputs/cycle-1/oci-specialist")
AGENTS_CONFIG_PATH = os.getenv("AGENTS_CONFIG_PATH", "config/oci-copilot-agents.yaml")
DEFAULT_STRATEGY = os.getenv("DEFAULT_STRATEGY", "default")
ENABLE_QUICK_ACTIONS = os.getenv("ENABLE_QUICK_ACTIONS", "true").lower() == "true"

SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT_SECONDS", "300"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))

# =======================
# Custom CSS - OCI Console Style
# =======================
OCI_CSS = """
<style>
/* OCI Console Inspired Theme */
:root {
  --oci-red: #C74634;
  --oci-red-dark: #A33A2B;
  --oci-blue: #3B82F6;
  --oci-gray-50: #F9FAFB;
  --oci-gray-100: #F3F4F6;
  --oci-gray-200: #E5E7EB;
  --oci-gray-300: #D1D5DB;
  --oci-gray-500: #6B7280;
  --oci-gray-700: #374151;
  --oci-gray-900: #111827;
}

/* Main container */
.message {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* User messages */
.user-message {
  background: var(--oci-gray-100);
  border-radius: 8px;
  padding: 12px 16px;
}

/* Bot messages */
.assistant-message {
  background: white;
  border: 1px solid var(--oci-gray-200);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

/* Quick Actions Buttons */
.quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 16px 0;
}

.quick-action-btn {
  background: white;
  border: 1px solid var(--oci-gray-300);
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 500;
  color: var(--oci-gray-700);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.quick-action-btn:hover {
  border-color: var(--oci-red);
  color: var(--oci-red);
  background: #FEF2F2;
}

.quick-action-btn:active {
  transform: scale(0.98);
}

/* Document Cards */
.doc-card {
  background: white;
  border: 1px solid var(--oci-gray-200);
  border-left: 4px solid var(--oci-red);
  border-radius: 8px;
  padding: 12px 16px;
  margin: 8px 0;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.doc-card-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--oci-gray-900);
  margin-bottom: 4px;
}

.doc-card-source {
  font-size: 12px;
  color: var(--oci-blue);
  margin-bottom: 8px;
}

.doc-card-snippet {
  font-size: 13px;
  color: var(--oci-gray-700);
  line-height: 1.5;
}

.doc-card-snippet code {
  background: var(--oci-gray-100);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'SF Mono', Monaco, monospace;
  font-size: 12px;
}

/* Syntax Highlighting */
.code-block {
  background: #1E1E1E;
  border-radius: 8px;
  padding: 16px;
  margin: 12px 0;
  overflow-x: auto;
  font-family: 'SF Mono', Monaco, 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.code-block pre {
  margin: 0;
  color: #D4D4D4;
}

.code-block .keyword { color: #569CD6; }
.code-block .string { color: #CE9178; }
.code-block .comment { color: #6A9955; }
.code-block .function { color: #DCDCAA; }
.code-block .variable { color: #9CDCFE; }
.code-block .number { color: #B5CEA8; }

/* Sidebar Stats */
.sidebar-stats {
  background: var(--oci-gray-50);
  border-radius: 8px;
  padding: 12px;
  margin: 12px 0;
  font-size: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px solid var(--oci-gray-200);
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: var(--oci-gray-500);
}

.stat-value {
  font-weight: 600;
  color: var(--oci-gray-900);
}

/* Strategy Badge */
.strategy-badge {
  display: inline-block;
  background: var(--oci-red);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

/* Action Buttons */
.action-btn {
  background: var(--oci-red);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.action-btn:hover {
  background: var(--oci-red-dark);
}

/* Loading Animation */
.loading-dots::after {
  content: '';
  animation: dots 1.5s infinite;
}

@keyframes dots {
  0%, 20% { content: '.'; }
  40% { content: '..'; }
  60%, 100% { content: '...'; }
}

/* Step/Tool styling */
.step-container {
  border-left: 2px solid var(--oci-gray-300);
  padding-left: 16px;
  margin: 12px 0;
}

.step-name {
  font-weight: 600;
  font-size: 13px;
  color: var(--oci-gray-700);
}

.step-input {
  font-size: 12px;
  color: var(--oci-gray-500);
  font-family: 'SF Mono', monospace;
  background: var(--oci-gray-100);
  padding: 8px;
  border-radius: 4px;
  margin: 4px 0;
}

/* Error styling */
.error-message {
  background: #FEF2F2;
  border: 1px solid #FECACA;
  border-radius: 8px;
  padding: 12px 16px;
  color: #991B1B;
}

/* Welcome message */
.welcome-container {
  background: linear-gradient(135deg, #C74634 0%, #3B82F6 100%);
  border-radius: 12px;
  padding: 24px;
  color: white;
  margin-bottom: 16px;
}

.welcome-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
}

.welcome-subtitle {
  font-size: 14px;
  opacity: 0.9;
}
</style>
"""

# =======================
# Constants
# =======================
QUICK_ACTIONS = [
    {
        "label": "🌐 Criar VCN",
        "prompt": "Como criar uma Virtual Cloud Network na OCI com subnets públicas e privadas?",
    },
    {
        "label": "🔍 Diagnosticar",
        "prompt": "Me ajude a diagnosticar problemas de conectividade para uma instância compute.",
    },
    {
        "label": "📦 Migrar Bucket",
        "prompt": "Como migrar um bucket do AWS S3 para OCI Object Storage?",
    },
    {
        "label": "⚡ Terraform",
        "prompt": "Gere um Terraform para criar um Autonomous Database com as melhores práticas.",
    },
]

STRATEGIES = ["default", "migracao", "configuracao", "troubleshooting"]


# =======================
# Helper Functions
# =======================
def load_agents_config() -> dict:
    """Load agents configuration from YAML file."""
    try:
        import yaml

        with open(AGENTS_CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Could not load agents config: {e}")
        return {}


def highlight_terraform(code: str) -> str:
    """Apply syntax highlighting to Terraform/code blocks."""
    keywords = [
        "resource",
        "data",
        "variable",
        "output",
        "provider",
        "terraform",
        "module",
        "for_each",
        "depends_on",
        "count",
        "lifecycle",
    ]
    functions = [
        "var",
        "local",
        "data",
        "module",
        "lookup",
        "length",
        "join",
        "split",
        "format",
        "timestamp",
    ]

    for kw in keywords:
        code = code.replace(kw, f'<span class="keyword">{kw}</span>')
    for fn in functions:
        code = code.replace(fn + "(", f'<span class="function">{fn}</span>(')

    return code


def format_doc_as_card(doc: dict, index: int) -> str:
    """Format a document as a visual card."""
    title = doc.get("metadata", {}).get("title", f"Documento {index + 1}")
    url = doc.get("metadata", {}).get("url", "")
    content = doc.get("content", "")[:200]

    card = f"""
<div class="doc-card">
  <div class="doc-card-title">📄 {title}</div>
  <div class="doc-card-source">{url}</div>
  <div class="doc-card-snippet">{content}...</div>
</div>
"""
    return card


async def query_rag_api(query: str, strategy: str = "default", k: int = 5) -> list:
    """Query the RAG API for documents."""
    try:
        response = requests.post(
            f"{RAG_API_URL}/rag/retrieve",
            json={"query": query, "k": k, "strategy": strategy},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("documents", [])
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"RAG API error: {str(e)}")


async def query_mlx_stream(prompt: str, context: list[str]) -> list[str]:
    """Query MLX server for streaming response."""
    context_str = "\n\n".join(context)
    full_prompt = f"""Você é um especialista em Oracle Cloud Infrastructure (OCI).
Use as informações de contexto abaixo para responder à pergunta do usuário.

Contexto:
{context_str}

Pergunta: {prompt}

Resposta (em português brasileiro, técnico e detalhado):"""

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{MLX_SERVER_URL}/v1/chat/completions",
                json={
                    "model": MODEL_PATH,
                    "messages": [{"role": "user", "content": full_prompt}],
                    "stream": True,
                    "max_tokens": 2048,
                    "temperature": 0.3,
                },
                timeout=aiohttp.ClientTimeout(total=SESSION_TIMEOUT),
            ) as resp:
                async for line in resp.content:
                    if line:
                        try:
                            data = json.loads(line.decode("utf-8").strip("data: "))
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except:
                            continue
    except Exception as e:
        raise ConnectionError(f"MLX server error: {str(e)}")


# =======================
# Chainlit Handlers
# =======================
@cl.on_chat_start
async def start():
    """Initialize chat session with OCI styling."""
    # Load agents config
    agents_config = load_agents_config()

    # Store session state
    cl.user_session.set("strategy", DEFAULT_STRATEGY)
    cl.user_session.set("docs_retrieved", 0)
    cl.user_session.set("tokens_generated", 0)
    cl.user_session.set("agents_config", agents_config)

    # Send custom CSS
    await cl.Message(content=OCI_CSS, disable_feedback=True).send()

    # Welcome message with OCI styling
    welcome_html = f"""
<div class="welcome-container">
  <div class="welcome-title">🚀 OCI Copilot</div>
  <div class="welcome-subtitle">Especialista em Oracle Cloud Infrastructure</div>
</div>

Sou seu assistente técnico para OCI. Posso ajudá-lo com:
• Arquitetura e configuração de serviços OCI
• Troubleshooting e diagnóstico de problemas
• Migração de outras nuvens (AWS, Azure, GCP)
• Geração de código Terraform e OCI CLI
• Análise de documentos e arquivos que você anexar

<div class="strategy-badge">Modo: {DEFAULT_STRATEGY}</div>
"""
    await cl.Message(content=welcome_html).send()

    # Quick Actions (if enabled)
    if ENABLE_QUICK_ACTIONS:
        quick_actions_buttons = [
            cl.Action(
                name=action["label"], value=action["prompt"], label=action["label"]
            )
            for action in QUICK_ACTIONS
        ]

        await cl.Message(
            content="**Sugestões rápidas:**", actions=quick_actions_buttons
        ).send()

    # Settings dropdown
    settings = await cl.ChatSettings(
        [
            cl.input_widget.Select(
                id="strategy",
                label="Perfil do Agente",
                values=STRATEGIES,
                initial_index=0,
            )
        ]
    ).send()


@cl.on_settings_update
async def setup_agent(settings):
    """Update agent strategy when user changes settings."""
    strategy = settings.get("strategy", DEFAULT_STRATEGY)
    cl.user_session.set("strategy", strategy)

    await cl.Message(
        content=f"⚙️ **Perfil alterado para:** `{strategy}`\n\nEste perfil ajustará o comportamento do RAG e as ferramentas disponíveis."
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Main message handler - RAG + MLX inference."""
    # Initialize
    strategy = cl.user_session.get("strategy")
    docs_retrieved = 0
    tokens_count = 0

    # =======================
    # 1. Handle Attachments
    # =======================
    files = message.elements
    file_content = ""

    if files:
        for file in files:
            try:
                with open(file.path, "r", encoding="utf-8") as f:
                    content = f.read()
                    file_content += f"\n\n--- Arquivo: {file.name} ---\n{content}\n"
            except Exception as e:
                await cl.Message(content=f"❌ Erro ao ler {file.name}: {str(e)}").send()

        if file_content:
            await cl.Message(
                content=f"📎 **Arquivo(s) anexado(s):** {len(files)}"
            ).send()

    # =======================
    # 2. RAG Retrieval Step
    # =======================
    query = message.content
    if file_content:
        query = f"{query}\n\nContexto do arquivo:\n{file_content}"

    async with cl.Step(name="🔍 RAG Retrieval", type="tool") as rag_step:
        rag_step.input = {"query": query, "strategy": strategy}

        try:
            docs = await query_rag_api(query, strategy, k=5)
            docs_retrieved = len(docs)
            cl.user_session.set("docs_retrieved", docs_retrieved)

            if not docs:
                rag_step.output = "Nenhum documento encontrado."
            else:
                docs_context = [doc.get("content", "") for doc in docs]
                context_preview = "\n\n".join(
                    [
                        f"[{i + 1}] {doc.get('metadata', {}).get('title', 'Doc')}"
                        for i, doc in enumerate(docs)
                    ]
                )
                rag_step.output = (
                    f"Recuperados {len(docs)} documentos:\n\n{context_preview}"
                )

        except ConnectionError as e:
            rag_step.output = f"Erro: {str(e)}"
            rag_step.is_error = True
            await cl.Message(
                content=f"⚠️ **Erro de conexão:** Não foi possível conectar ao backend RAG ({RAG_API_URL}).\n\nVerifique se o FastAPI está rodando."
            ).send()
            return

    # =======================
    # 3. MLX Inference Step
    # =======================
    if docs:
        # Start streaming response
        await cl.Message(content="💭 Gerando resposta...").send()

        final_msg = cl.Message(content="")
        await final_msg.send()

        # Stream from MLX
        context_texts = [doc.get("content", "") for doc in docs]

        try:
            # Build context for LLM
            context_combined = "\n\n".join(context_texts)

            # This would be the real MLX call - commented for now
            # async for token in query_mlx_stream(query, context_texts):
            #     await final_msg.stream_token(token)
            #     tokens_count += 1

            # For now, show that we're ready for integration
            await final_msg.stream_token(
                f"📚 **Baseado em {len(docs)} documentos检索ados e no perfil `{strategy}`:**\n\n"
            )
            await final_msg.stream_token("⚡ **Integração com MLX Server pronta!**\n\n")
            await final_msg.stream_token("Para habilitar a inferência real:\n")
            await final_msg.stream_token(
                f"1. Inicie o servidor MLX: `mlx_lm.server --model {MODEL_PATH}`\n"
            )
            await final_msg.stream_token(
                f"2. Certifique-se de que o servidor está em: {MLX_SERVER_URL}\n"
            )
            await final_msg.stream_token(
                "\nO modelo responderá com base nos documentos检索ados.\n\n"
            )

            # Show documents as cards
            for i, doc in enumerate(docs):
                await final_msg.stream_token(
                    f"**Documento {i + 1}:** {doc.get('metadata', {}).get('title', 'Doc')}\n"
                )
                await final_msg.stream_token(
                    f"_{doc.get('metadata', {}).get('url', '')}_\n"
                )
                await final_msg.stream_token(f"{doc.get('content', '')[:300]}...\n\n")

            tokens_count = 150  # Placeholder
            cl.user_session.set("tokens_generated", tokens_count)

        except ConnectionError as e:
            await final_msg.stream_token(
                f"\n\n⚠️ **Erro de conexão com MLX Server:** {str(e)}"
            )
    else:
        await cl.Message(
            content="🔍 Não encontrei documentos relevantes na base de conhecimento para responder essa pergunta."
        ).send()

    # =======================
    # 4. Contextual Actions
    # =======================
    if strategy in ["migracao", "default"] and docs:
        actions = [
            cl.Action(
                name="validate_terraform", value="validate", label="🛠️ Validar Terraform"
            ),
            cl.Action(name="generate_oci_cli", value="cli", label="📝 Gerar OCI CLI"),
        ]
        await cl.Message(content="**Ações disponíveis:**", actions=actions).send()

    # =======================
    # 5. Session Stats
    # =======================
    total_docs = cl.user_session.get("docs_retrieved")
    total_tokens = cl.user_session.get("tokens_generated")

    stats_msg = f"""
<div class="sidebar-stats">
  <div class="stat-item">
    <span class="stat-label">Perfil</span>
    <span class="stat-value">{strategy}</span>
  </div>
  <div class="stat-item">
    <span class="stat-label">Docs检索ados</span>
    <span class="stat-value">{total_docs}</span>
  </div>
  <div class="stat-item">
    <span class="stat-label">Tokens gerados</span>
    <span class="stat-value">{total_tokens}</span>
  </div>
</div>
"""
    await cl.Message(content=stats_msg).send()


@cl.action_callback("validate_terraform")
async def on_validate_terraform(action: cl.Action):
    """Handle Terraform validation action."""
    async with cl.Step(name="🔍 Validando Terraform", type="run") as step:
        step.input = "terraform validate"
        step.output = "O código Terraform seria validado localmente via OCI CLI ou Terraform CLI.\n\nConfigure a integração em: rag/app_chainlit_oli2oci.py → action callbacks"

    await cl.Message(
        content="✅ Ação disponível - configure a integração real com subprocess."
    ).send()


@cl.action_callback("generate_oci_cli")
async def on_generate_oci_cli(action: cl.Action):
    """Handle OCI CLI generation action."""
    async with cl.Step(name="📝 Gerando OCI CLI", type="run") as step:
        step.input = "Gerar comandos OCI CLI"
        step.output = "Comandos OCI CLI seriam gerados com base no contexto da conversa.\n\nConfigure a integração em: rag/app_chainlit_oli2oci.py → action callbacks"

    await cl.Message(
        content="✅ Ação disponível - configure a integração real com subprocess."
    ).send()


# Quick action handlers
for qa in QUICK_ACTIONS:
    action_name = qa["label"].replace(" ", "_").lower()

    @cl.action_callback(action_name)
    async def on_quick_action(action: cl.Action):
        await cl.Message(content=f"📝 Enviando para análise: **{action.value}**").send()


# =======================
# Error Handler
# =======================
@cl.on_chat_error
async def handle_error(error: Exception):
    """Global error handler."""
    await cl.Message(
        content=f"""
<div class="error-message">
  <strong>❌ Erro inesperado:</strong><br>
  {str(error)}
</div>
"""
    ).send()
