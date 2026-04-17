#!/usr/bin/env bash

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

STANDARD_SERVICES=(
    "com.apple.*"
    "com.apple.accessibility.*"
    "com.apple.accounts.*"
    "com.apple.addressbook.*"
    "com.apple.analyticsagent"
    "com.apple.assistive.*"
    "com.apple.audio.*"
    "com.apple.backup.*"
    "com.apple.bluetooth.*"
    "com.apple.book.*"
    "com.apple.cloud.*"
    "com.apple.contacts.*"
    "com.apple.core.*"
    "com.apple.coreservices.*"
    "com.apple.crypto*"
    "com.apple.dictation*"
    "com.apple.finder"
    "com.apple.font.*"
    "com.apple.gamecontroller*"
    "com.apple.help.*"
    "com.apple.identityservices*"
    "com.apple.icdd"
    "com.apple.icloud*"
    "com.apple.input.*"
    "com.apple.install.*"
    "com.apple.intelligence*"
    "com.apple.keyboard*"
    "com.apple.location*"
    "com.apple.loginwindow.*"
    "com.apple.mail.*"
    "com.apple.mdworker.*"
    "com.apple.media*"
    "com.apple.metrickit*"
    "com.apple.mobile*"
    "com.apple.navd"
    "com.apple.notificationcenterui*"
    "com.apple.parentalcontrols*"
    "com.apple.photo*"
    "com.apple.quicklook*"
    "com.apple.remind*"
    "com.apple.routined"
    "com.apple.safari*"
    "com.apple.security*"
    "com.apple.sharingd"
    "com.apple.siri*"
    "com.apple.speech*"
    "com.apple.spotlight*"
    "com.apple.storekitagent"
    "com.apple.syncd"
    "com.apple.systemsettings*"
    "com.apple.talagent"
    "com.apple.tccd"
    "com.apple.TextInput*"
    "com.apple.translation*"
    "com.apple.triald"
    "com.apple.usermanager*"
    "com.apple.usernotifications*"
    "com.apple.weather*"
    "com.apple.webcontent*"
    "com.apple.wifi.*"
    "com.apple.WindowManager*"
)

get_launchctl_services() {
    launchctl list | grep -v "PID" | tail -n +2 | awk '{print $3}' | sort -u
}

get_running_processes() {
    ps -ax -o pid,comm=NAME,%mem=CPU | tail -n +2 | sort -k3 -rn | head -30
}

is_user_service() {
    local service="$1"
    for pattern in "${STANDARD_SERVICES[@]}"; do
        if [[ "$service" == $pattern ]]; then
            return 1
        fi
    done
    return 0
}

is_user_service_slow() {
    local service="$1"
    if [[ "$service" == ai.perplexity.* ]] || [[ "$service" == application.* ]] || \
       [[ "$service" == com.google.* ]] || [[ "$service" == com.microsoft.* ]] || \
       [[ "$service" == com.ollama.* ]] || [[ "$service" == com.openai.* ]] || \
       [[ "$service" == mega.* ]] || [[ "$service" == com.openssh.* ]]; then
        return 0
    fi
    return 1
}

disable_service() {
    local service="$1"
    local label="${service##*/}"
    local success=0
    
    echo -e "${YELLOW}→ Tentando desabilitar: ${label}${NC}"
    
    for plist in \
        "/System/Library/LaunchAgents/${label}" \
        "/Library/LaunchAgents/${label}" \
        "/System/Library/LaunchDaemons/${label}" \
        "/Library/LaunchDaemons/${label}"; do
        if [[ -f "$plist" ]]; then
            if launchctl unload "$plist" 2>/dev/null; then
                echo -e "${GREEN}✓ Desabilitado via launchctl: ${label}${NC}"
                success=1
                break
            fi
        fi
    done
    
    if [[ $success -eq 0 ]]; then
        local pid
        pid=$(launchctl list | grep -F "$label" | awk '{print $1}' | head -1)
        if [[ -n "$pid" && "$pid" != "-" && "$pid" =~ ^[0-9]+$ ]]; then
            echo -e "${YELLOW}→ Matando processo PID ${pid}: ${label}${NC}"
            kill "$pid" 2>/dev/null
            sleep 0.5
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null
            fi
            if ! kill -0 "$pid" 2>/dev/null; then
                echo -e "${GREEN}✓ Processo matado: ${label} (PID ${pid})${NC}"
            else
                echo -e "${RED}✗ Falha ao matar: ${label} (PID ${pid})${NC}"
            fi
        else
            echo -e "${RED}✗ Não encontrado: ${label}${NC}"
        fi
    fi
}

show_help() {
    echo "Uso: $0 [opção] [serviços]"
    echo ""
    echo "Opções:"
    echo "  --list              Lista serviços ativos (padrão: user-only)"
    echo "  --list-all          Lista TODOS os serviços ativos"
    echo "  --list-user        Lista serviços de terceiros (prioritários)"
    echo "  --top              Lista top processos por memória"
    echo "  --disable N,M-O    Desabilita serviços por número (não-interativo)"
    echo "  --interactive      Modo interativo (pergunta quais desabilitar)"
    echo "  -h, --help         Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 --list-user"
    echo "  $0 --disable 1,3,5-10"
    echo "  $0 --top"
    exit 0
}

list_services() {
    local filter_user="$1"
    local count=1
    while IFS= read -r service; do
        if [[ -z "$service" ]]; then
            continue
        fi
        local is_user=0
        if is_user_service_slow "$service"; then
            is_user=1
        fi
        if [[ "$filter_user" == "1" && $is_user -eq 0 ]]; then
            continue
        elif [[ "$filter_user" == "2" && $is_user -eq 1 ]]; then
            continue
        fi
        if [[ $is_user -eq 1 ]]; then
            echo -e "${BLUE}${count}${NC} ${GREEN}${service}${NC}"
        else
            echo -e "${BLUE}${count}${NC} ${service}"
        fi
        count=$((count + 1))
    done < <(get_launchctl_services)
}

list_all() {
    local count=1
    while IFS= read -r service; do
        [[ -z "$service" ]] && continue
        echo -e "${BLUE}${count}${NC} ${service}"
        count=$((count + 1))
    done < <(get_launchctl_services)
}

top_processes() {
    echo -e "${YELLOW}--- Top processos por memória ---${NC}"
    get_running_processes | nl
}

disable_by_numbers() {
    local nums="$1"
    for num in $(echo "$nums" | tr , '\n' | tr - ' '); do
        local service
        service=$(get_launchctl_services | sed -n "${num}p")
        if [[ -n "$service" ]]; then
            disable_service "$service"
        else
            echo -e "${RED}✗ Serviço #$num não encontrado${NC}"
        fi
    done
}

interactive_mode() {
    echo -e "${YELLOW}=== Detectando serviços ativos no seu Mac ===${NC}"
    echo ""
    echo -e "${GREEN}=== Serviços de TERCEIROS (prioritários para desabilitar) ===${NC}"
    list_services 1
    echo ""
    echo -e "${YELLOW}=== TODOS os serviços ===${NC}"
    list_all
    echo ""
    
    top_processes
    echo ""
    
    echo -e "${YELLOW}=== Selecione serviços para desabilitar ===${NC}"
    echo "Exemplo: 1,3,5-10,15"
    echo "Ou 'all' para todos"
    echo "Ou 'q' para sair"
    echo ""
    read -p "→ " selection

    if [[ "$selection" == "q" || -z "$selection" ]]; then
        echo "Saindo..."
        exit 0
    fi

    if [[ "$selection" == "all" ]]; then
        echo -e "${RED}⚠ ATENÇÃO: Isso vai desabilitar TODOS os serviços!${NC}"
        read -p "Confirmar (y/n)? " confirm
        if [[ "$confirm" != "y" ]]; then
            echo "Cancelado."
            exit 0
        fi
        while IFS= read -r service; do
            [[ -z "$service" ]] && continue
            disable_service "$service"
        done < <(get_launchctl_services)
    else
        disable_by_numbers "$selection"
    fi

    echo ""
    echo -e "${GREEN}=== Concluído ===${NC}"
    echo "Reinicie o Mac quando necessário para restaurar serviços."
}

if [[ $# -eq 0 ]]; then
    interactive_mode
    exit 0
fi

case "$1" in
    --list)
        list_services 1
        ;;
    --list-all)
        list_all
        ;;
    --list-user)
        list_services 1
        ;;
    --top)
        top_processes
        ;;
    --disable)
        if [[ -z "$2" ]]; then
            echo "Erro: --disable requer números"
            exit 1
        fi
        disable_by_numbers "$2"
        ;;
    --interactive)
        interactive_mode
        ;;
    -h|--help)
        show_help
        ;;
    *)
        echo "Opção desconhecida: $1"
        show_help
        ;;
esac