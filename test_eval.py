import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path("scripts").absolute()))
from unified_evaluation import ScoringEngine, SelfJudge, UnifiedEvaluator

def evaluate():
    print("Testing ScoringEngine and SelfJudge with new v5 format...")
    
    test_response = """Para a solicitação de criação (provisionamento) em relação a instances na Oracle Cloud Infrastructure (OCI), considerando o cenário da empresa TechCorp Brasil, a abordagem recomendada é dividida em etapas claras. 

Neste contexto, é de suma importância observar as best practices (melhores práticas) e garantir que o ciclo de vida do ambiente (produção estável) esteja alinhado à estratégia corporativa. Dessa forma, apresentamos as diretrizes técnicas exigidas, garantindo a alta disponibilidade e integridade do seu serviço.

### 1. Visão Geral e Pré-requisitos

Antes de iniciar qualquer operação através da OCI CLI ou Terraform, é imprescindível verificar os seguintes pré-requisitos fundamentais:
- Confirme que as permissões de IAM adequadas estão configuradas. Por exemplo, garanta que a política "Allow group ecommerce-migration-admins to manage instances-family in compartment production" foi corretamente aplicada.
- Certifique-se de que os limites (Service Limits) do tenant suportam esta operação, especialmente para novos recursos ou em situações de alta demanda na região `sa-saopaulo-1`.
- Planeje os eventuais impactos no tráfego de rede e acesso, garantindo que o requisito imposto de `sem downtime` seja plenamente atendido.

### 2. Boas Práticas, Vantagens e Trade-offs

Ao administrar e evoluir a infraestrutura de instances, deve-se pesar a vantagem da agilidade oferecida pela nuvem contra os desafios e o risco potencial de segurança ou custo excessivo.

- **Melhor Prática (Recomendação)**: Mantenha sempre um esquema de tags (Tagging) consistente nos recursos gerados, utilizando namespaces padronizados como `cost-center=ecommerce-migration`. Em resumo, isso facilita absurdamente a auditoria, rastreabilidade e visibilidade de custos a longo prazo.
- **Trade-off de Arquitetura**: Provisionar instâncias ou serviços excessivamente robustos e performáticos (por exemplo, shapes superiores) traz a vantagem clara de suportar cargas de pico sem gargalos. No entanto, a desvantagem inerente é o custo ocioso se a demanda real for inferior à projetada. 
- **Risco Identificado**: Uma configuração descuidada de portas ou permissões abertas no compartimento `production` pode expor partes da sua arquitetura à internet ou a intrusos. A mitigação fundamental recomendada é implementar regras estritas de NSG (Network Security Groups) e ativar a monitoria contínua usando os pilares fundamentais do OCI Cloud Guard desde o primeiro dia.

### 3. Procedimento Técnico e Implementação

Abaixo, fornecemos os detalhes exatos da execução do criação (provisionamento) via linha de comando ou script de automação de infraestrutura. Execute os comandos com cautela, assegurando-se de que o ambiente alvo está correto.

```bash
oci compute instance launch --availability-domain AD-1 --shape VM.Standard.E4.Flex --shape-config 'ocpus=2,memory=16' --subnet-id ocid1.subnet.oc1.sa-saopaulo-1.xxx --display-name instances-ecomm-42 --compartment-id ocid1.compartment.oc1..production
```

Consequentemente, executando as instruções delineadas acima, o recurso de instances será orquestrado conforme o padrão recomendado e validado pela Oracle. A OCI exige atenção redobrada à precisão dos identificadores (OCIDs) fornecidos.

### 4. Validação e Teste de Funcionalidade

Após o envio da requisição para a cloud, a etapa de validação é o próximo passo estritamente obrigatório. Veja que a execução de um comando muitas vezes é assíncrona, exigindo assim a confirmação objetiva de seu estado:

- Realize consultas periódicas de estado (polling) ou utilize flags nativas como `--wait-for-state` (quando disponível) para assegurar que a transição ocorreu com total êxito.
- Inspecione os logs de auditoria nativos e verifique se as métricas de performance estão condizentes com a baseline aceitável do projeto ecommerce-migration.
- Valide também se os pontos de rede foram atribuídos adequadamente, permitindo conectividade com a aplicação consumidora.

### 5. Resumo da Configuração Aplicada

Para efeito de clareza, segue a tabela sumária do escopo onde a operação foi planejada:

| Parâmetro Crítico | Valor Configurado na Operação |
|-------------------|-------------------------------|
| **Região (Region)** | `sa-saopaulo-1` |
| **Compartimento** | `production` |
| **Fase / Ciclo de Vida** | `produção estável` |
| **Tipo de Ação** | `criação (provisionamento)` |

Portanto, seguindo religiosamente essa estrutura metodológica, o risco de indisponibilidade é drasticamente minimizado e as metas técnicas estabelecidas para a infraestrutura da TechCorp Brasil serão entregues com segurança e alta performance no Oracle Cloud Infrastructure.

**Referência Oficial (Doc):** https://docs.oracle.com/pt-br/iaas/Content/Compute/Home.htm"""

    user_prompt = "Atuando como cloud architect na empresa TechCorp Brasil, minha missão é executar a tarefa de criação (provisionamento) para instances no escopo do projeto ecommerce-migration (região sa-saopaulo-1, compartimento production). Como proceder?"
    
    score_tech = ScoringEngine.score_technical_correctness(test_response, "compute/instances")
    score_depth = ScoringEngine.score_depth(test_response)
    score_struct = ScoringEngine.score_structure(test_response)
    score_halluc = ScoringEngine.score_hallucination(test_response)
    score_clarity = ScoringEngine.score_clarity(test_response)
    
    print("\n--- Heuristic Scoring ---")
    print(f"Technical Correctness: {score_tech}")
    print(f"Depth: {score_depth}")
    print(f"Structure: {score_struct}")
    print(f"Hallucination: {score_halluc}")
    print(f"Clarity: {score_clarity}")
    
    overall = (score_tech + score_depth + score_struct + score_halluc + score_clarity) / 5
    print(f"Overall Predicted Score: {overall}")

    print("\n--- Self-Judge Parsing Test ---")
    sj = SelfJudge(use_portuguese=True)
    # Simulando a resposta perfeita do LLM-as-Judge para ver se o parse funciona
    simulated_judge_response = """
Aqui está minha avaliação conforme os critérios definidos:

```json
{
  "correctness": 5,
  "helpfulness": 5,
  "depth": 5,
  "safety": 5,
  "reasoning": "A resposta contém comandos reais e exatos da CLI OCI, está perfeitamente estruturada, menciona riscos e melhores práticas, e não possui nenhuma alucinação ou citação a outras nuvens."
}
```
Espero ter ajudado."""
    parsed = sj.parse_judge_response(simulated_judge_response)
    print(json.dumps(parsed, indent=2, ensure_ascii=False))

evaluate()
