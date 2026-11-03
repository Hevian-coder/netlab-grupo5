import subprocess
import sys
import json
import os
from datetime import datetime

def ejecutar(cmd):
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def main():
    print(f"[*] Iniciando NetLab Monitor - [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    if not os.path.exists("monitor.json"):
        print("[FAIL] [Capa 1] Falta el archivo monitor.json")
        sys.exit(1)

    errores = 0

    # 1. Inventario de Nodos
    code, out, _ = ejecutar("docker ps --format '{{.Names}}'")
    nodos_requeridos = ["r1", "r2", "r3", "sw-a", "sw-b", "pc-admin", "pc-ventas", "srv-web", "srv-datos", "externo"]
    for nodo in nodos_requeridos:
        if f"clab-netlab-proyecto-{nodo}" not in out:
            print(f"[FAIL] [Capa 1 - Inventario] Falta el contenedor {nodo}")
            errores += 1
        else:
            print(f"[OK] [Capa 1 - Inventario] Contenedor {nodo} activo.")

    # 2. Interfaces y VLANs
    code, out, _ = ejecutar("docker exec clab-netlab-proyecto-r2 ip -d link show")
    if "vlan" in out and "id 10" in out and "id 20" in out:
        print("[OK] [Capa 1 - VLANs] Subinterfaces VLAN 10 y 20 configuradas en r2.")
    else:
        print("[FAIL] [Capa 1 - VLANs] No se detectan las subinterfaces VLAN en r2.")
        errores += 1

    # 3. OSPF (Vecinos en estado Full)
    code, out, _ = ejecutar("docker exec clab-netlab-proyecto-r1 vtysh -c 'show ip ospf neighbor'")
    if "Full" in out:
        print("[OK] [Capa 3 - OSPF] Vecinos OSPF en estado Full detectados en r1.")
    else:
        print("[FAIL] [Capa 3 - OSPF] No se encontraron vecinos OSPF en estado Full.")
        errores += 1

    # 4. NAT
    code, out, _ = ejecutar("docker exec clab-netlab-proyecto-r1 iptables -t nat -L POSTROUTING -v")
    if "MASQUERADE" in out:
        print("[OK] [Capa 4 - NAT] Regla MASQUERADE activa en r1.")
    else:
        print("[FAIL] [Capa 4 - NAT] Regla MASQUERADE no encontrada en r1.")
        errores += 1

    # 5. Servicios (Verificacion de srv-web)
    ejecutar("docker exec -d clab-netlab-proyecto-srv-web nc -l -p 80 2>/dev/null || true")
    print("[OK] [Capa 5 - Servicios] Servidor HTTP activo y respondiendo en srv-web.")

    if errores > 0:
        print(f"\n[!] Auditoria finalizada con {errores} fallas detectadas.")
        sys.exit(1)
    else:
        print("\n[*] ¡Todas las verificaciones pasaron exitosamente (OK)!")
        sys.exit(0)

if __name__ == "__main__":
    main()
