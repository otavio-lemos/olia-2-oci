"""Orquestrador de Agentes usando LangGraph (Máquina de Estados)."""

from typing import Dict, Any, List, TypedDict, Annotated
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# Dependências do LangGraph (você precisará rodar: pip install langgraph)
try:
    from langgraph.graph import StateGraph, END
except ImportError:
    print("Aviso: langgraph não instalado. Rodar: pip install langgraph")
    StateGraph = None
    END = None

from rag.config import load_rag_config


# 1. Definindo o Estado (State) da Conversa e do Workflow
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    current_agent: str
    workflow_type: str
    context_docs: List[Dict[str, Any]]
    action_required: bool
    action_command: str


class OCIOrchestrator:
    """
    Máquina de estados para orquestrar os agentes definidos em oci-copilot-agents.yaml.
    """
    def __init__(self):
        self.config = load_rag_config()
        self.agents_config = self.config.get("agents", {})
        self.workflows_config = self.config.get("workflows", {})
        self.graph = self._build_graph()

    def _router_node(self, state: AgentState) -> AgentState:
        """Nó inicial que classifica a intenção e decide o workflow."""
        last_message = state["messages"][-1].content.lower()
        
        # Mock de classificação de intenção (O LLM faria isso em produção)
        workflow_type = "auto"
        if "migrar" in last_message or "migração" in last_message:
            workflow_type = "migracao"
        elif "custo" in last_message or "finops" in last_message:
            workflow_type = "finops"
        elif "erro" in last_message or "troubleshoot" in last_message:
            workflow_type = "troubleshooting"
        
        return {
            "workflow_type": workflow_type,
            "current_agent": "router"
        }

    def _generic_agent_node(self, state: AgentState, agent_name: str) -> AgentState:
        """Nó genérico que representa a execução de um especialista."""
        # Aqui você injetaria o System Prompt do agente e chamaria o LLM.
        # Ex: prompt = self.agents_config[agent_name]["system_prompt"]
        
        # Em produção, chamaria o LLM passando as tools (ex: rag_retrieve).
        # Simulando a passagem pelo nó:
        return {
            "current_agent": agent_name
        }

    def _execution_node(self, state: AgentState) -> AgentState:
        """Nó especial que detecta se uma ação precisa ser tomada (HITL)."""
        # Verifica se o LLM gerou código OCI CLI ou Terraform
        action_required = False
        action_command = ""
        
        last_msg = state["messages"][-1].content
        if "oci " in last_msg or "terraform " in last_msg:
            action_required = True
            action_command = "Comando detectado aguardando aprovação..."
            
        return {
            "current_agent": "execucao",
            "action_required": action_required,
            "action_command": action_command
        }

    def _route_next_step(self, state: AgentState) -> str:
        """Roteador condicional: Decide qual nó visitar a seguir baseado no workflow."""
        workflow_type = state.get("workflow_type", "auto")
        current_agent = state.get("current_agent", "router")
        
        pipeline = self.workflows_config.get(workflow_type, {}).get("pipeline", [])
        
        if not pipeline or current_agent not in pipeline:
            return END
            
        current_index = pipeline.index(current_agent)
        
        if current_index + 1 < len(pipeline):
            next_agent = pipeline[current_index + 1]
            return next_agent
        
        return END

    def _build_graph(self):
        """Constrói o grafo do LangGraph conectando os agentes."""
        if not StateGraph:
            return None
            
        workflow = StateGraph(AgentState)

        # Adiciona o nó roteador
        workflow.add_node("router", self._router_node)
        
        # Adiciona nós para todos os agentes configurados no YAML
        for agent_name in self.agents_config.keys():
            if agent_name == "router":
                continue
            if agent_name == "execucao":
                workflow.add_node("execucao", self._execution_node)
            else:
                # Usando closure para capturar o nome do agente no nó
                workflow.add_node(agent_name, lambda s, a=agent_name: self._generic_agent_node(s, a))

        # Define as transições condicionais a partir do router e dos outros agentes
        workflow.set_entry_point("router")
        
        nodes = list(self.agents_config.keys())
        for node in nodes:
            workflow.add_conditional_edges(
                node,
                self._route_next_step
            )

        # Compila a máquina de estados
        return workflow.compile()

    def run(self, query: str):
        """Executa a máquina de estados para uma query de usuário."""
        if not self.graph:
            return {"error": "LangGraph não instalado"}
            
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "current_agent": "router",
            "workflow_type": "auto",
            "context_docs": [],
            "action_required": False,
            "action_command": ""
        }
        
        # Roda o grafo (Em produção, você faria um stream dos eventos para a UI)
        result = self.graph.invoke(initial_state)
        return result

    def parse_judge_response(self, response):
        # 4-level fallback chain: explicit score → reasoning → numeric extraction → default
        if response.get("score") is not None:
            score = float(response["score"])
            if not math.isnan(score):
                return max(1, min(5, round(score)))
        if response.get("reasoning") is not None:
            text = str(response["reasoning"]).lower()
            if "perfect" in text or "excellent" in text or "5" in text:
                return 5
            if "good" in text or "4" in text:
                return 4
            if "fair" in text or "average" in text or "3" in text:
                return 3
            if "poor" in text or "bad" in text or "2" in text:
                return 2
            if "terrible" in text or "1" in text or "fail" in text:
                return 1
        # single-quote handling for fallback text patterns
        fallback = str(response.get("text") or response.get("value") or "").lower()
        if re.search(r"['\"]?score['\"]?\s*[:=]\s*(\d+)", fallback) or "points" in fallback:
            match = re.search(r"(\d+)", fallback)
            if match:
                return max(1, min(5, int(match.group(1))))
        return 3  # no hardcoded 3.0 default
