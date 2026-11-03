#!/bin/bash
echo "[*] Destruyendo despliegue previo si existe..."
containerlab destroy -t netlab.clab.yml --cleanup 2>/dev/null

echo "[*] Desplegando topologia con Containerlab..."
containerlab deploy -t netlab.clab.yml --reconfigure

echo "[*] Configurando sw-a como Bridge de Linux..."
docker exec -d clab-netlab-proyecto-sw-a sh -c "ip link add name br0 type bridge && ip link set br0 up && ip link set eth1 master br0 && ip link set eth2 master br0 && ip link set eth3 master br0 && ip link set eth1 up && ip link set eth2 up && ip link set eth3 up"

echo "[*] Configurando sw-b como Bridge de Linux..."
docker exec -d clab-netlab-proyecto-sw-b sh -c "ip link add name br0 type bridge && ip link set br0 up && ip link set eth1 master br0 && ip link set eth2 master br0 && ip link set eth3 master br0 && ip link set eth1 up && ip link set eth2 up && ip link set eth3 up"

echo "[*] Configurando subinterfaces VLANs (10 y 20) en r2 para Grupo 5..."
docker exec -it clab-netlab-proyecto-r2 ip link add link eth1 name eth1.10 type vlan id 10
docker exec -it clab-netlab-proyecto-r2 ip addr add 172.16.5.1/27 dev eth1.10
docker exec -it clab-netlab-proyecto-r2 ip link set dev eth1.10 up

docker exec -it clab-netlab-proyecto-r2 ip link add link eth1 name eth1.20 type vlan id 20
docker exec -it clab-netlab-proyecto-r2 ip addr add 172.16.5.33/28 dev eth1.20
docker exec -it clab-netlab-proyecto-r2 ip link set dev eth1.20 up

echo "[*] Configurando IPs en interfaces de r1..."
docker exec -it clab-netlab-proyecto-r1 ip addr add 172.16.5.49/29 dev eth1
docker exec -it clab-netlab-proyecto-r1 ip link set dev eth1 up
docker exec -it clab-netlab-proyecto-r1 ip addr add 203.0.113.1/29 dev eth4
docker exec -it clab-netlab-proyecto-r1 ip link set dev eth4 up

echo "[*] ¡Despliegue y configuracion completados con exito!"
