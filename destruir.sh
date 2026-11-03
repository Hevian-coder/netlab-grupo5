echo "[*] Destruyendo contenedores de Containerlab..."
containerlab destroy -t netlab.clab.yml --cleanup
echo "[*] Limpiando bridges de Linux residuales..."
ip link delete sw-a type bridge 2>/dev/null
ip link delete sw-b type bridge 2>/dev/null
echo "[*] Limpieza finalizada."
