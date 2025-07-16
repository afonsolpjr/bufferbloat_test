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


