#!/bin/bash

echo "=== Memória ANTES ==="
top -l 1 -n 0 | grep "PhysMem"
vm_stat | head -5

echo ""
echo "=== Killing NON-ESSENTIAL user processes ==="

PROTECTED_PROCS=(
    "launchd" "kernel_task" "WindowServer" "Dock" "SystemUIServer"
    "loginwindow" "coreaudiod" "cfprefsd" "distnoted" "mDNSResponder"
    "logd" "powerd" "configd" "UserEventAgent" "systemstats"
    "DisplaysServices" "Finder" "ControlCenter" "NotificationCenter"
    "Spotlight" "BackgroundTasks" "airplay" "Bluetooth" "Wi-Fi"
    "Opencode" "Terminal" "iTerm" "zsh" "bash" "sh"
)

KILLED=0
for pid in $(ps -eo pid=); do
    [[ $pid -le 1 ]] && continue
    
    name=$(ps -p $pid -o comm= 2>/dev/null)
    [[ -z "$name" ]] && continue
    
    protected=0
    for proc in "${PROTECTED_PROCS[@]}"; do
        [[ "$name" == "$proc" ]] && protected=1 && break
    done
    
    [[ $protected -eq 1 ]] && continue
    
    kill -9 $pid 2>/dev/null && echo "[KILL] $name (PID: $pid)" && ((KILLED++))
done

echo "Mortos: $KILLED"

echo ""
echo "=== Disabling non-essential services ==="
sudo mdutil -i off 2>/dev/null
sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.metadata.mds.plist 2>/dev/null
sudo tmutil disable 2>/dev/null
sudo pmset -a standby 0 hibernatemode 0 2>/dev/null

echo ""
echo "=== Memória DEPOIS ==="
top -l 1 -n 0 | grep "PhysMem"

echo ""
echo "=== Top processos por memória ==="
ps -eo pid,pcpu,pmem,comm | sort -k3 -rn | head -10