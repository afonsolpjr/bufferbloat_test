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

parser = ArgumentParser(description="Bufferbloat tests")
parser.add_argument('--bw-host', '-B',
                    type=float,
                    help="Bandwidth of host links (Mb/s)",
                    default=1000)

parser.add_argument('--bw-net', '-b',
                    type=float,
                    help="Bandwidth of bottleneck (network) link (Mb/s)",
                    required=True)

parser.add_argument('--delay',
                    type=float,
                    help="Link propagation delay (ms)",
                    required=True)

parser.add_argument('--dir', '-d',
                    help="Directory to store outputs",
                    required=True)

parser.add_argument('--time', '-t',
                    help="Duration (sec) to run the experiment",
                    type=int,
                    default=10)

parser.add_argument('--maxq',
                    type=int,
                    help="Max buffer size of network interface in packets",
                    default=100)

parser.add_argument('--cong',
                    help="Congestion control algorithm to use",
                    default="reno")

# Expt parameters
args = parser.parse_args()

class BBTopo(Topo):
    "Simple topology for bufferbloat experiment."

    def build(self, n=2):
        h1 = self.addHost("h1")
        h2 = self.addHost("h2")

        switch = self.addSwitch('s0')

        self.addLink(h1, switch, bw=args.bw_host , delay=f"{args.delay}ms")
        self.addLink(switch, h2, bw=args.bw_net, delay=f"{args.delay}ms", max_queue_size=args.maxq, use_htb=True)

def start_iperf(net):
    h1 = net.get('h1')
    h2 = net.get('h2')

    print(f"\n[ Iniciando servidor iperf em {h2.IP()} ] ...")
    # CLI(net)
    server = h2.popen("iperf -s -w 16m")  # Servidor iperf padrão (porta 5001)
    sleep(1)
    # Verifica se o servidor está ouvindo
    print(h2.cmd("netstat -tulnp | grep iperf || echo 'Servidor iperf não encontrado'"))
    
    print(f"[ Iniciando cliente iperf em {h1.IP()} ] ...")
    client = h1.popen(f"iperf -c {h2.IP()} -tinf")  # Fluxo longo (1 hora)
    sleep(1)
    # Verifica se o cliente está conectado
    print(h1.cmd(f"netstat -tunp | grep iperf || echo 'Cliente iperf não conectado'"))

    return server, client

def start_qmon(iface, interval_sec=0.1, outfile=f"{args.dir}/qlen{args.maxq}.txt"):
    monitor = Process(target=monitor_qlen,
                      args=(iface, interval_sec, outfile))
    monitor.start() # Terminate with monitor.terminate()
    return monitor



def start_ping(net, ping_count=int(args.time/0.1)):
    h1 = net.get('h1')
    h2 = net.get('h2')
    print("Iniciando pings. numero de pings = ", ping_count)
    return h1.popen(f"ping -c {ping_count} -i 0.1 {h2.IP()} -D > {args.dir}/ping{args.maxq}.txt", shell=True)

def start_webserver(net):
    h1 = net.get('h1')
    print("\nAbrindo webserver em h1....")
    proc = h1.popen("python webserver.py", shell=True)
    sleep(1)
    return proc

def measure_page_dl(net):
    h1 = net.get('h1')
    h2 = net.get('h2')
    
       # Executa curl e captura exit code
    curl_cmd = f"curl -o /dev/null -s -w '%{{time_total}}' {h1.IP()}"
    while(1):

        dl_time = h2.cmd(curl_cmd)
        exit_code = int(h2.cmd('echo $?'))
        if(exit_code==0):
            return float(dl_time)
        else:
            print(f"Erro no download da página...tentando de novo... exitcode= {exit_code}")

def bufferbloat():
    if not os.path.exists(args.dir):
        os.makedirs(args.dir)
    # Inicialização
    print("[Iniciando experimento.]",
        f"\n[Controle de congestão= {args.cong}]",
        f"\t[Tamanho da fila= {args.maxq}]",
        f"\n[Duração={args.time}] \t[delay por link={args.delay}]\n")
    
    os.system("sysctl -w net.ipv4.tcp_congestion_control=%s" % args.cong)
    topo = BBTopo()
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()

    #Teste de ping
    net.pingAll()

    # Inicia monitoramento
    qmon = start_qmon(iface='s0-eth2')
    
    #Inicia fluxos TCP, pings e servidor web
    start_iperf(net)
    start_ping(net)
    start_webserver(net)

    # Verifica se o webserver está respondendo
    print("\tVerificando webserver. Tempo teste de download = ", measure_page_dl(net))
    
    start_time = time()
    measures = []
    while True:
        # do the measurement (say) 3 times.
        for _ in range(0,3):
            measures.append(measure_page_dl(net))
        sleep(5)
        now = time()
        delta = now - start_time
        if delta > args.time:
            break
        print("%.1fs left..." % (args.time - delta))

    with open(f"{args.dir}/qlen{args.maxq}delays_medidos.txt", "w") as f:
        print('Salvando tempos de download...')
        f.write(f"Tempos de download: {measures}\nMédia: {np.mean(measures)}\nDesvio padrão: {np.std(measures)}\n")

    qmon.terminate()
    net.stop()
    # Garante que todos os processos criados no mininet sejam encerrados.
    # Às vezes eles precisam ser encerrados manualmente.
    Popen("pgrep -f webserver.py | xargs kill -9", shell=True).wait()

if __name__ == "__main__":
    bufferbloat()
