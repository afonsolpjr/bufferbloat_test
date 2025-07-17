from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser

from monitor import monitor_qlen

import sys
import os
import math
import numpy as np

# Instalar Iperf3 mais recente (não tem no repositorio ubuntu/debian)
# - Ver no final da pagina: https://iperf.fr/iperf-download.php
#  Dei build from source com ./configure && make && make install
# AI deu problema de biblioteca que resolvi com sudo apt-get install lib32z1

# Classe da topologia
class TopoComp(Topo):
    "Simple topology for tcp traffic competition experiment."

    def build(self, n=2):
        h1 = self.addHost( "h1" )
        h2 = self.addHost( "h2" )

        # Here I have created a switch.  If you change its name, its
        # interface names will change from s0-eth1 to newname-eth1.
        switch = self.addSwitch('s0')

        # self.addLink( node1, node2, bw=10, delay='5ms', max_queue_size=1000, loss=10, use_htb=True): 
        # adds a bidirectional link with bandwidth, delay and loss characteristics, with a maximum queue size of 1000 
        # packets using the Hierarchical Token Bucket rate limiter and netem delay/loss emulator. 
        # The parameter bw is expressed as a number in Mbit; delay is expressed as a string with units in place (e.g. '5ms', '100us', '1s'); 
        # loss is expressed as a percentage (between 0 and 100); and max_queue_size is expressed in packets.

        self.addLink( h1, switch )
        self.addLink( switch, h2)

# Iniciando mininet

print("[ Iniciando uma rede simples ]")
net = Mininet(topo=TopoComp(),host=CPULimitedHost, link=TCLink)
net.start()
net.pingAll()
print('\n')

h1 = net.get('h1')
h2 = net.get('h2')
# print(type(h1))
# Abrindo servidores
bbr_port=5001
reno_port=5002
print(f"h1 ip {h1.IP()}\nh2 ip {h2.IP()}")
print("Abrindo servidores..",end='')
serv_bbr = h2.popen(f"iperf -s --port {bbr_port}")
serv_reno = h2.popen(f"iperf -s --port {reno_port}")
sleep(2)
print(".")
print(h2.cmd("netstat -tulpn"))

test_duration = 10
data_shared_dir = "/vagrant/bufferbloat/data"
bbr_process= h1.popen(f"iperf -c {h2.IP()} -p {bbr_port} -i 0.1 -t {test_duration} --linux-congestion bbr | while read line; do echo \"$(date +%s.%N) $line\"; done > {data_shared_dir}/bbr.txt", shell=True)
reno_process= h1.popen(f"iperf -c {h2.IP()} -p {reno_port} -i 0.1 -t {test_duration} --linux-congestion reno| while read line; do echo \"$(date +%s.%N) $line\"; done > {data_shared_dir}/reno.txt", shell=True)

start_time=time()
print("[Testes em execução ihaa]")
while (True):
    now=time()
    elapsed = now-start_time
    if(elapsed>=test_duration):
        break
    else:
        print(f"\rTempo restante = {int(test_duration-elapsed)}seg", end='')
        sleep(2)
print("\n")
bbr_process.wait()
reno_process.wait()

net.stop()

# Popen("cat /tmp/bbr.txt /tmp/reno.txt",shell=True).wait()

Popen(f"sudo chmod 666 {data_shared_dir}/bbr.txt {data_shared_dir}/reno.txt",shell=True).wait()
Popen(f"sed -i '/sec/!d' {data_shared_dir}/reno.txt {data_shared_dir}/bbr.txt ", shell=True).wait()
print("[Liberando recursos]")
Popen("sudo mn -c 2> /dev/null", shell=True).wait()

