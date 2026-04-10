#!/usr/bin/env python3
"""
Clean OCI dataset by fixing all detected content issues:
1. Remove generic template responses (irrecuperaveis)
2. Remove examples with wrong CLI commands
3. FIX context pollution (remove [context: shape=...] de perguntas)
4. Semantic deduplication of responses
5. Add Portuguese diacritics

Usage:
    python scripts/clean_dataset.py --input data/curated/ --output data/all_curated_clean.jsonl --all
"""

import json
import re
import argparse
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Set


DIACRITICS_MAP = {
    "configuracao": "configuração",
    "preparacao": "preparação",
    "validacao": "validação",
    "implementacao": "implementação",
    "instalacao": "instalação",
    "permissao": "permissão",
    "permissoes": "permissões",
    "seguranca": "segurança",
    "serie": "série",
    "numero": "número",
    "instancias ": "instâncias ",
    "instancias\n": "instâncias\n",
    "instancias,": "instâncias,",
    "instancias.": "instâncias.",
    "regioes": "regiões",
    "acoes": "ações",
    "criacao": "criação",
    "automacao": "automação",
    "monitoramento": "monitoramento",
    "monitoracao": "monitoração",
    "notificacao": "notificação",
    "autenticacao": "autenticação",
    "aplicacao ": "aplicação ",
    "aplicacoes": "aplicações",
    "conexao": "conexão",
    "conexoes": "conexões",
    "protecao": "proteção",
    "corrupcao": "corrupção",
    "execucao": "execução",
    "comunicacao": "comunicação",
    "informacao ": "informação ",
    "informacoes": "informações",
    "documentacao": "documentação",
    "avaliacao": "avaliação",
    "otimizacao": "otimização",
    "razao": "razão",
    "funcao": "função",
    "funcoes": "funções",
    "operacao": "operação",
    "operacoes": "operações",
    "producao": "produção",
    "secao": "seção",
    "licenca": "licença",
    "licencas": "licenças",
    "consistencia": "consistência",
    "experiencia": "experiência",
    "ciencia": "ciência",
    "portugues": "português",
    "ingles": "inglês",
    "especifico": "específico",
    "especifica": "específica",
    "unico ": "único ",
    "unica ": "única ",
    "publico ": "público ",
    "publica ": "pública ",
    "periodo": "período",
    "metrica": "métrica",
    "metricas": "métricas",
    "analise": "análise",
    "grafico": "gráfico",
    "graficos": "gráficos",
    "relatorio": "relatório",
    "relatorios": "relatórios",
    "logico": "lógico",
    "logica": "lógica",
    "pratica": "prática",
    "praticas": "práticas",
    "politica": "política",
    "politicas": "políticas",
    "historico": "histórico",
    "caracteristica": "característica",
    "caracteristicas": "características",
    "variavel": "variável",
    "variaveis": "variáveis",
    "possivel": "possível",
    "impossivel": "impossível",
    "nivel": "nível",
    "niveis": "níveis",
    "proprio": "próprio",
    "propria": "própria",
    "evidencia": "evidência",
    "gerenciamento": "gerenciamento",
    "armazenamento": "armazenamento",
    "gerenciado": "gerenciado",
    "gerenciada": "gerenciada",
    "indice": "índice",
    "indices": "índices",
    "contem": "contém",
    "alem": "além",
    "atribuido": "atribuído",
    "construcao": "construção",
    "selecao": "seleção",
    "colecao": "coleção",
    "colecoes": "coleções",
    "opcoes": "opções",
    "condicoes": "condições",
    "transicao": "transição",
    "pre-requisito": "pré-requisito",
    "pre-requisitos": "pré-requisitos",
    "pre-configurado": "pré-configurado",
    "tambem": "também",
    "voce": "você",
    "disponivel": "disponível",
    "disponiveis": "disponíveis",
    "util": "útil",
    "uteis": "úteis",
    "facil": "fácil",
    "dificil": "difícil",
    "atencao": "atenção",
    "solucao": "solução",
    "solucoes": "soluções",
    "situacao": "situação",
    "situacoes": "situações",
    "migracao": "migração",
    "migracoes": "migrações",
    "alteracao": "alteração",
    "alteracoes": "alterações",
    "avaliacoes": "avaliações",
    "recomendacao": "recomendação",
    "recomendacoes": "recomendações",
    "configuracoes": "configurações",
    "especificacoes": "especificações",
    "autorizacao": "autorização",
    "verificacao": "verificação",
    "recuperacao": "recuperação",
    "replicacao": "replicação",
    "escalavel": "escalável",
    "escalaveis": "escaláveis",
    "renovacao": "renovação",
    "aplicavel": "aplicável",
    "aplicaveis": "aplicáveis",
    "compativel": "compatível",
    "compativeis": "compatíveis",
    "conectividade": "conectividade",
    "produtividade": "produtividade",
    "identidade": "identidade",
    "entidade": "entidade",
    "entidades": "entidades",
    "atividade": "atividade",
    "atividades": "atividades",
    "prioridade": "prioridade",
    "prioridades": "prioridades",
    "visibilidade": "visibilidade",
    "manutencao": "manutenção",
    "detecao": "detecção",
    "correlacao": "correlação",
    "integracao": "integração",
    "integracoes": "integrações",
    "orquestracao": "orquestração",
    "expansao": "expansão",
    "resolucao": "resolução",
    "resolucoes": "resoluções",
    "evolucao": "evolução",
    "distribuicao": "distribuição",
    "contribuicao": "contribuição",
    "substituicao": "substituição",
    "obtencao": "obtenção",
    "contencao": "contenção",
    "detencao": "detenção",
    "retencao": "retenção",
    "intencao": "intenção",
    "tensao": "tensão",
    "tensoes": "tensões",
    "versao": "versão",
    "versoes": "versões",
    "conversao": "conversão",
    "revisao": "revisão",
    "revisoes": "revisões",
    "previsao": "previsão",
    "previsoes": "previsões",
    "expressao": "expressão",
    "expressoes": "expressões",
    "progressao": "progressão",
    "regressao": "regressão",
    "posicao": "posição",
    "posicoes": "posições",
    "sobreposicao": "sobreposição",
    "producao": "produção",
    "introducao": "introdução",
    "reducao": "redução",
    "reducoes": "reduções",
    "traducao": "tradução",
    "traducoes": "traduções",
    "induzir": "induzir",
    "deducao": "dedução",
    "conducao": "condução",
    "erupcao": "erupção",
    "interrupcao": "interrupção",
    "interrupcoes": "interrupções",
    "disrupcao": "disrupção",
    "projeto": "projeto",
    "projetos": "projetos",
    "objeto": "objeto",
    "objetos": "objetos",
    "sujeito": "sujeito",
    "perfeito": "perfeito",
    "perfeita": "perfeita",
    "efeito": "efeito",
    "efeitos": "efeitos",
    "respeito": "respeito",
    "conceito": "conceito",
    "conceitos": "conceitos",
    "aspecto": "aspecto",
    "aspectos": "aspectos",
    "circuito": "circuito",
    "gratuito": "gratuito",
    "gratuita": "gratuita",
    "intuito": "intuito",
    "restrito": "restrito",
    "restrita": "restrita",
    "distinto": "distinto",
    "distinta": "distinta",
    "extinto": "extinto",
    "extinta": "extinta",
    "imediatamente": "imediatamente",
    "exatamente": "exatamente",
    "previamente": "previamente",
    "principalmente": "principalmente",
    "basicamente": "basicamente",
    "geralmente": "geralmente",
    "normalmente": "normalmente",
    "especificamente": "especificamente",
    "particularmente": "particularmente",
    "especialmente": "especialmente",
    "fundamentalmente": "fundamentalmente",
    "essencialmente": "essencialmente",
    "adicionalmente": "adicionalmente",
    "adicional": "adicional",
    "opcional": "opcional",
    "opcionais": "opcionais",
    "funcional": "funcional",
    "funcionais": "funcionais",
    "operacional": "operacional",
    "operacionais": "operacionais",
    "profissional": "profissional",
    "profissionais": "profissionais",
    "excecao": "exceção",
    "excecoes": "exceções",
    "inspecao": "inspeção",
    "inspecoes": "inspeções",
    "expectativa": "expectativa",
    "expectativas": "expectativas",
    "perspectiva": "perspectiva",
    "perspectivas": "perspectivas",
    "selecionado": "selecionado",
    "selecionada": "selecionada",
    "eliminado": "eliminado",
    "eliminada": "eliminada",
    "automatizado": "automatizado",
    "automatizada": "automatizada",
    "otimizado": "otimizado",
    "otimizada": "otimizada",
    "otimizar": "otimizar",
    "otimizacoes": "otimizações",
    "customizado": "customizado",
    "customizada": "customizada",
    "personalizado": "personalizado",
    "personalizada": "personalizada",
    "dimensionamento": "dimensionamento",
    "recomendado": "recomendado",
    "recomendada": "recomendada",
    "aprovado": "aprovado",
    "aprovada": "aprovada",
    "validado": "validado",
    "validada": "validada",
    "configurado": "configurado",
    "configurada": "configurada",
    "criado": "criado",
    "criada": "criada",
    "definido": "definido",
    "definida": "definida",
    "estabelecido": "estabelecido",
    "estabelecida": "estabelecida",
    "implementado": "implementado",
    "implementada": "implementada",
    "instalado": "instalado",
    "instalada": "instalada",
    "habilitado": "habilitado",
    "habilitada": "habilitada",
    "habilitar": "habilitar",
    "habilitacao": "habilitação",
    "desabilitado": "desabilitado",
    "desabilitada": "desabilitada",
    "monitorado": "monitorado",
    "controlado": "controlado",
    "controlada": "controlada",
    "verificado": "verificado",
    "verificada": "verificada",
    "identificado": "identificado",
    "identificada": "identificada",
    "classificado": "classificado",
    "classificada": "classificada",
    "organizado": "organizado",
    "organizada": "organizada",
    "planejado": "planejado",
    "planejada": "planejada",
    "executado": "executado",
    "executada": "executada",
    "realizado": "realizado",
    "realizada": "realizada",
    "finalizado": "finalizado",
    "finalizada": "finalizada",
    "iniciado": "iniciado",
    "iniciada": "iniciada",
    "encerrado": "encerrado",
    "encerrada": "encerrada",
    "terminado": "terminado",
    "terminada": "terminada",
    "atualizado": "atualizado",
    "atualizada": "atualizada",
    "modificado": "modificado",
    "modificada": "modificada",
    "ajustado": "ajustado",
    "ajustada": "ajustada",
    "corrigido": "corrigido",
    "corrigida": "corrigida",
    "resolvido": "resolvido",
    "resolvida": "resolvida",
    "solucionado": "solucionado",
    "solucionada": "solucionada",
    "mitigado": "mitigado",
    "mitigada": "mitigada",
    "evitado": "evitado",
    "evitada": "evitada",
    "detectado": "detectado",
    "detectada": "detectada",
    "localizado": "localizado",
    "localizada": "localizada",
    "encontrado": "encontrado",
    "encontrada": "encontrada",
    "descoberto": "descoberto",
    "descoberta": "descoberta",
    "exibido": "exibido",
    "exibida": "exibida",
    "mostrado": "mostrado",
    "mostrada": "mostrada",
    "apresentado": "apresentado",
    "apresentada": "apresentada",
    "demonstrado": "demonstrado",
    "demonstrada": "demonstrada",
    "explicado": "explicado",
    "explicada": "explicada",
    "descrito": "descrito",
    "descrita": "descrita",
    "relatado": "relatado",
    "relatada": "relatada",
    "notificado": "notificado",
    "notificada": "notificada",
    "alertado": "alertado",
    "alertada": "alertada",
    "informado": "informado",
    "informada": "informada",
    "comunicado": "comunicado",
    "comunicada": "comunicada",
    "anunciado": "anunciado",
    "anunciada": "anunciada",
    "declarado": "declarado",
    "declarada": "declarada",
    "confirmado": "confirmado",
    "confirmada": "confirmada",
    "garantido": "garantido",
    "garantida": "garantida",
    "certificado": "certificado",
    "certificada": "certificada",
    "autenticado": "autenticado",
    "autenticada": "autenticada",
    "autorizado": "autorizado",
    "autorizada": "autorizada",
    "permitido": "permitido",
    "permitida": "permitida",
    "liberado": "liberado",
    "liberada": "liberada",
    "bloqueado": "bloqueado",
    "bloqueada": "bloqueada",
    "restringido": "restringido",
    "restringida": "restringida",
    "limitado": "limitado",
    "limitada": "limitada",
    "reduzido": "reduzido",
    "reduzida": "reduzida",
    "aumentado": "aumentado",
    "aumentada": "aumentada",
    "expandido": "expandido",
    "expandida": "expandida",
    "ampliado": "ampliado",
    "ampliada": "ampliada",
    "simplificado": "simplificado",
    "simplificada": "simplificada",
    "transformado": "transformado",
    "transformada": "transformada",
    "convertido": "convertido",
    "convertida": "convertida",
    "adaptado": "adaptado",
    "adaptada": "adaptada",
    "calibrado": "calibrado",
    "calibrada": "calibrada",
    "processado": "processado",
    "processada": "processada",
    "calculado": "calculado",
    "calculada": "calculada",
    "estimado": "estimado",
    "estimada": "estimada",
    "avaliado": "avaliado",
    "avaliada": "avaliada",
    "mensuravel": "mensurável",
    "avaliavel": "avaliável",
    "testavel": "testável",
    "verificavel": "verificável",
    "observavel": "observável",
    "detectavel": "detectável",
    "acessivel": "acessível",
    "acessiveis": "acessíveis",
    "visivel": "visível",
    "visiveis": "visíveis",
    "relevante": "relevante",
    "relevantes": "relevantes",
    "significativo": "significativo",
    "significativa": "significativa",
    "consideravel": "considerável",
    "equivalente": "equivalente",
    "equivalentes": "equivalentes",
    "relacionado": "relacionado",
    "relacionada": "relacionada",
    "associado": "associado",
    "associada": "associada",
    "vinculado": "vinculado",
    "vinculada": "vinculada",
    "conectado": "conectado",
    "conectada": "conectada",
    "integrado": "integrado",
    "integrada": "integrada",
    "incorporado": "incorporado",
    "incorporada": "incorporada",
    "inserido": "inserido",
    "inserida": "inserida",
    "adicionado": "adicionado",
    "adicionada": "adicionada",
    "introduzido": "introduzido",
    "introduzida": "introduzida",
    "implantado": "implantado",
    "implantada": "implantada",
    "implantacao": "implantação",
    "implantacoes": "implantações",
    "desenvolvido": "desenvolvido",
    "desenvolvida": "desenvolvida",
    "desenvolvimento": "desenvolvimento",
    "desenvolvedor": "desenvolvedor",
    "desenvolvedores": "desenvolvedores",
    "revolucionario": "revolucionário",
    "revolucionaria": "revolucionária",
    "solucionar": "solucionar",
    "solucionavel": "solucionável",
}

GENERIC_TEMPLATES = [
    r"Para configurar \w+ no OCI, siga estes passos",
    r"Acesse o Console OCI e navegue ate o servico correspondente",
    r"No Console, clique em 'Create' para o servico desejado",
    r"Configure os parametros conforme sua necessidade",
    r"Ajuste as configuracoes de rede e seguranca",
    r"Teste o acesso e conectividade",
    r"Verifique logs e metricas",
    r"Documente a configuracao",
]

FOUR_STEP_PATTERN = [
    r"Passo 1: Preparacao",
    r"Passo 2: Criacao",
    r"Passo 3: Configuracao",
    r"Passo 4: Validacao",
]

GENERIC_TROUBLESHOOTING = [
    r"Problema comum 1: Recurso nao inicia",
    r"Problema comum 2: Erro de permissao",
    r"Problema comum 3: Timeout de conexao",
    r"Verificar estado do recurso",
    r"Checklist de validacao",
]

GENERIC_BEST_PRACTICES = [
    r"1\. Planejamento e Design",
    r"2\. Implementacao",
    r"3\. Seguranca",
    r"4\. Operacao",
    r"5\. Otimizacao",
    r"Defina claramente os requisitos de",
    r"Use Infrastructure as Code",
    r"Implemente tagging consistente",
]

GENERIC_SECURITY_AUDIT = [
    r"Checklist de Seguranca",
    r"1\. Identity & Access Management",
    r"Policies com principio de menor privilegio",
    r"Grupos IAM organizados por funcao",
    r"MFA habilitado para todos os usuarios",
    r"Encryption em repouso",
    r"Encryption em transito",
]

GENERIC_INTEGRATION = [
    r"Servicos OCI que integram com",
    r"OCI Vault.*Encryption keys",
    r"OCI Monitoring.*Metricas e alertas",
    r"OCI Logging.*Logs estruturados",
]

WRONG_CLI_MAP = {
    "terraform/": [
        r"oci compute instance launch",
        r"oci compute instance list",
        r"oci compute instance update",
        r"oci compute instance terminate",
        r"oci compute instance get",
        r"oci network vcn create",
        r"oci network vcn delete",
        r"oci db autonomous-database create",
        r"oci db autonomous-database delete",
    ],
    "database/": [
        r"oci compute instance launch",
        r"oci compute instance terminate",
    ],
    "networking/": [
        r"oci compute instance launch",
        r"oci compute instance terminate",
    ],
}


def is_generic_template(content: str) -> bool:
    four_step = sum(
        1 for p in FOUR_STEP_PATTERN if re.search(p, content, re.IGNORECASE)
    )
    if four_step >= 4:
        return True
    generic = sum(1 for p in GENERIC_TEMPLATES if re.search(p, content, re.IGNORECASE))
    if generic >= 5:
        return True
    trouble = sum(
        1 for p in GENERIC_TROUBLESHOOTING if re.search(p, content, re.IGNORECASE)
    )
    if trouble >= 4:
        return True
    bp = sum(1 for p in GENERIC_BEST_PRACTICES if re.search(p, content, re.IGNORECASE))
    if bp >= 6:
        return True
    sec = sum(1 for p in GENERIC_SECURITY_AUDIT if re.search(p, content, re.IGNORECASE))
    if sec >= 5:
        return True
    integ = sum(1 for p in GENERIC_INTEGRATION if re.search(p, content, re.IGNORECASE))
    if integ >= 3:
        return True
    return False


def has_wrong_cli(content: str, category: str) -> bool:
    for cat_prefix, patterns in WRONG_CLI_MAP.items():
        if category.startswith(cat_prefix):
            for pattern in patterns:
                if re.search(pattern, content):
                    return True
    return False


CATEGORIES_TO_KEEP_SHAPES = {"compute/", "terraform/"}

SHAPE_PATTERNS_IN_RESPONSE = [
    r"VM\.Standard\.[A-Z0-9.]+",
    r"BM\.Standard\.[A-Z0-9.]+",
    r"GPU\.[A-Z0-9.]+",
    r"\d+\s*OCPUs?",
]


def fix_context_pollution(example: Dict) -> Dict:
    """Remove [context: shape=..., OCPUs, ...] from user messages."""
    cleaned = json.loads(json.dumps(example))
    for msg in cleaned.get("messages", []):
        if msg.get("role") == "user" and "content" in msg:
            msg["content"] = re.sub(
                r"\s*\[context:.*?\]",
                "",
                msg["content"],
            ).strip()
    return cleaned


def fix_shape_in_response(example: Dict) -> Dict:
    """Remove shape references from assistant responses in non-compute categories.
    Keeps shapes in compute/ and terraform/ (where they are legitimate)."""
    cleaned = json.loads(json.dumps(example))
    category = cleaned.get("metadata", {}).get("category", "unknown")

    if any(category.startswith(prefix) for prefix in CATEGORIES_TO_KEEP_SHAPES):
        return cleaned

    for msg in cleaned.get("messages", []):
        if msg.get("role") == "assistant" and "content" in msg:
            content = msg["content"]
            for pattern in SHAPE_PATTERNS_IN_RESPONSE:
                content = re.sub(pattern, "[SHAPE]", content)
            content = re.sub(r"Shape:\s*\[SHAPE\]\s*\n?", "", content)
            content = re.sub(r"\[SHAPE\],?\s*", "", content)
            msg["content"] = content
    return cleaned


def add_diacritics(text: str) -> str:
    result = text
    for without, with_accent in DIACRITICS_MAP.items():
        result = re.sub(
            r"\b" + re.escape(without) + r"\b",
            with_accent,
            result,
            flags=re.IGNORECASE,
        )
    return result


def response_hash(content: str) -> str:
    # Hash first 1000 chars - captures variation in params/commands
    content = content[:1000]
    normalized = content.lower()
    normalized = re.sub(r"[`'\"]", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return hashlib.md5(normalized.encode()).hexdigest()


def load_examples(input_path: Path) -> List[Dict[str, Any]]:
    examples = []
    if input_path.is_file() and input_path.suffix == ".jsonl":
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        examples.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    elif input_path.is_dir():
        for json_file in sorted(input_path.rglob("*.jsonl")):
            with open(json_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            examples.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
    return examples


def main():
    parser = argparse.ArgumentParser(description="Clean OCI dataset")
    parser.add_argument(
        "--input", "-i", required=True, help="JSONL file or curated dir"
    )
    parser.add_argument("--output", "-o", required=True, help="Output JSONL file")
    parser.add_argument("--all", action="store_true", help="Apply all cleaning steps")
    parser.add_argument(
        "--remove-generic",
        action="store_true",
        help="Remove generic template responses",
    )
    parser.add_argument(
        "--remove-wrong-cli",
        action="store_true",
        help="Remove wrong CLI commands",
    )
    parser.add_argument(
        "--fix-pollution",
        action="store_true",
        help="Fix context pollution (remove [context: shape=...] from user messages)",
    )
    parser.add_argument("--dedup", action="store_true", help="Deduplicate responses")
    parser.add_argument("--diacritics", action="store_true", help="Add diacritics")
    parser.add_argument(
        "--remove-shapes-from-responses",
        action="store_true",
        help="Remove shape references from assistant responses (non-compute categories)",
    )
    args = parser.parse_args()

    do_all = args.all
    remove_generic = args.remove_generic or do_all
    remove_wrong_cli = args.remove_wrong_cli or do_all
    fix_pollution = args.fix_pollution or do_all
    dedup = args.dedup or do_all
    add_diacritics_flag = args.diacritics or do_all
    remove_shapes_from_responses = args.remove_shapes_from_responses or do_all

    input_path = Path(args.input)
    output_path = Path(args.output)

    print(f"Loading examples from {input_path}...")
    examples = load_examples(input_path)
    print(f"Loaded {len(examples)} examples")

    stats = {"total": len(examples)}

    if remove_generic:
        print("\n[1/5] Removing generic template responses...")
        filtered = []
        for ex in examples:
            assistant = ""
            for msg in ex.get("messages", []):
                if msg.get("role") == "assistant":
                    assistant = msg.get("content", "")
                    break
            if not is_generic_template(assistant):
                filtered.append(ex)
            else:
                stats["removed_generic"] = stats.get("removed_generic", 0) + 1
        examples = filtered
        print(f"  Removed {stats.get('removed_generic', 0)}, {len(examples)} remaining")

    if remove_wrong_cli:
        print("\n[2/5] Removing wrong CLI commands...")
        filtered = []
        for ex in examples:
            category = ex.get("metadata", {}).get("category", "unknown")
            assistant = ""
            for msg in ex.get("messages", []):
                if msg.get("role") == "assistant":
                    assistant = msg.get("content", "")
                    break
            if not has_wrong_cli(assistant, category):
                filtered.append(ex)
            else:
                stats["removed_wrong_cli"] = stats.get("removed_wrong_cli", 0) + 1
        examples = filtered
        print(
            f"  Removed {stats.get('removed_wrong_cli', 0)}, {len(examples)} remaining"
        )

    if fix_pollution:
        print("\n[3/5] Fixing context pollution...")
        fixed = 0
        for i, ex in enumerate(examples):
            user_content = ""
            for msg in ex.get("messages", []):
                if msg.get("role") == "user":
                    user_content = msg.get("content", "")
                    break
            if "[context:" in user_content:
                examples[i] = fix_context_pollution(ex)
                fixed += 1
        stats["fixed_pollution"] = fixed
        print(f"  Fixed {fixed} examples")

    if remove_shapes_from_responses:
        print(
            "\n[4/5] Removing shape references from assistant responses (non-compute)..."
        )
        fixed = 0
        for i, ex in enumerate(examples):
            category = ex.get("metadata", {}).get("category", "unknown")
            if not any(
                category.startswith(prefix) for prefix in CATEGORIES_TO_KEEP_SHAPES
            ):
                examples[i] = fix_shape_in_response(ex)
                fixed += 1
        stats["fixed_shape_in_response"] = fixed
        print(f"  Fixed {fixed} examples")

    if dedup:
        print("\n[4/5] Deduplicating responses...")
        seen: Set[str] = set()
        filtered = []
        for ex in examples:
            assistant = ""
            for msg in ex.get("messages", []):
                if msg.get("role") == "assistant":
                    assistant = msg.get("content", "")
                    break
            category = ex.get("metadata", {}).get("category", "unknown")
            key = f"{category}:{response_hash(assistant)}"
            if key not in seen:
                seen.add(key)
                filtered.append(ex)
            else:
                stats["removed_dedup"] = stats.get("removed_dedup", 0) + 1
        examples = filtered
        print(
            f"  Removed {stats.get('removed_dedup', 0)} duplicates, {len(examples)} remaining"
        )

    if add_diacritics_flag:
        print("\n[5/5] Adding Portuguese diacritics...")
        for i, ex in enumerate(examples):
            for msg in ex.get("messages", []):
                if "content" in msg:
                    msg["content"] = add_diacritics(msg["content"])
        stats["diacritics_added"] = len(examples)
        print(f"  Added diacritics to {len(examples)} examples")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"\n{'=' * 60}")
    print(f"CLEANING SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Input:     {stats['total']} examples")
    print(
        f"  Output:    {len(examples)} examples ({len(examples) / max(stats['total'], 1) * 100:.1f}%)"
    )
    if remove_generic:
        print(f"  Removed generic templates:  {stats.get('removed_generic', 0)}")
    if remove_wrong_cli:
        print(f"  Removed wrong CLI:          {stats.get('removed_wrong_cli', 0)}")
    if fix_pollution:
        print(f"  Fixed context pollution:    {stats.get('fixed_pollution', 0)}")
    if remove_shapes_from_responses:
        print(
            f"  Removed shape references:   {stats.get('fixed_shape_in_response', 0)}"
        )
    if dedup:
        print(f"  Removed duplicates:         {stats.get('removed_dedup', 0)}")
    if add_diacritics_flag:
        print(f"  Diacritics added:           {stats.get('diacritics_added', 0)}")
    print(f"\n  Output: {output_path}")


if __name__ == "__main__":
    main()
