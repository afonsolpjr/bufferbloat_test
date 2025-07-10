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



# Linux uses CUBIC-TCP by default that doesn't have the usual sawtooth
# behaviour.  For those who are curious, invoke this script with
# --cong cubic and see what happens...
# sysctl -a | grep cong should list some interesting parameters.
parser.add_argument('--cong',
                    help="Congestion control algorithm to use",
                    default="reno")

# Expt parameters
args = parser.parse_args()

class BBTopo(Topo):
    "Simple topology for bufferbloat experiment."

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

        print(f"Criando links com delay = {args.delay}ms")
        self.addLink( h1, switch, bw=args.bw_host , delay=f"{args.delay}ms" )
        self.addLink( switch, h2, bw=args.bw_net, delay=f"{args.delay}ms", max_queue_size=args.maxq, use_htb=True)



# Simple wrappers around monitoring utilities.  You are welcome to
# contribute neatly written (using classes) monitoring scripts for
# Mininet!

def start_iperf(net):
    h1 = net.get('h1')
    h2 = net.get('h2')

    print(f"Iniciando servidor iperf em {h2.IP()}...")
    # CLI(net)
    server = h2.popen("iperf -s -w 16m")  # Servidor iperf padrão (porta 5001)
    sleep(1)
    # Verifica se o servidor está ouvindo
    print(h2.cmd("netstat -tulnp | grep iperf || echo 'Servidor iperf não encontrado'"))
    
    print(f"Iniciando cliente iperf em {h1.IP()}...")
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
    # TODO: Start a ping train from h1 to h2 (or h2 to h1, does it
    # matter?)  Measure RTTs every 0.1 second.  Read the ping man page
    # to see how to do this.

    # Hint: Use host.popen(cmd, shell=True).  If you pass shell=True
    # to popen, you can redirect cmd's output using shell syntax.
    # i.e. ping ... > /path/to/ping.
    h1 = net.get('h1')
    h2 = net.get('h2')
    print("Iniciando pings. numero de pings = ", ping_count)
    return h1.popen(f"ping -c {ping_count} -i 0.1 {h2.IP()} -D > {args.dir}/ping{args.maxq}.txt", shell=True)

def start_webserver(net):
    h1 = net.get('h1')
    print("Abrindo webserver em h1....")
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
    os.system("sysctl -w net.ipv4.tcp_congestion_control=%s" % args.cong)
    topo = BBTopo()
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    
    # Configuração básica
    dumpNodeConnections(net.hosts)
    net.pingAll()

    # Inicia monitoramento
    qmon = start_qmon(iface='s0-eth2')
    
    # Inicia o webserver
    webserver = start_webserver(net)
    # Verifica se o webserver está respondendo
    print("Verificando webserver... tempo de dl teste = ", measure_page_dl(net))
    
    #Inicia fluxos TCP
    iperf_server,iperf_client = start_iperf(net)

    # TODO: measure the time it takes to complete webpage transfer
    # from h1 to h2 (say) 3 times.  Hint: check what the following
    # command does: curl -o /dev/null -s -w %{time_total} google.com
    # Now use the curl command to fetch webpage from the webserver you
    # spawned on host h1 (not from google!)
    # Hint: Verify the url by running your curl command without the
    # flags. The html webpage should be returned as the response.

    # Hint: have a separate function to do this and you may find the
    # loop below useful.

    start_time = time()
    start_ping(net)

    measures = []
    while True:
        # do the measurement (say) 3 times.
        for i in range(0,3):
            measures.append(measure_page_dl(net))
        sleep(5)
        now = time()
        delta = now - start_time
        if delta > args.time:
            break
        print("%.1fs left..." % (args.time - delta))

    print("Tempos de download: \n", measures)

    # TODO: compute average (and standard deviation) of the fetch
    # times.  You don't need to plot them.  Just note it in your
    # README and explain.

    # Hint: The command below invokes a CLI which you can use to
    # debug.  It allows you to run arbitrary commands inside your
    # emulated hosts h1 and h2.
    # CLI(net)

    qmon.terminate()
    net.stop()
    # Ensure that all processes you create within Mininet are killed.
    # Sometimes they require manual killing.
    Popen("pgrep -f webserver.py | xargs kill -9", shell=True).wait()

def ping_test():
    if not os.path.exists(args.dir):
        os.makedirs(args.dir)

    def print_info(host):
        print(f"Host {host.name} IP: {host.IP()}")
        print(f"Host {host.name} MAC: {host.MAC()}\n___________")
    
    os.system("sysctl -w net.ipv4.tcp_congestion_control=%s" % args.cong)
    topo = BBTopo()
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    
    print("Endereços IP e MAC dos Hosts:")
    for host in net.hosts:
        print_info(host)

    print("Conexões:")
    # This dumps the topology and how nodes are interconnected through links.
    dumpNodeConnections(net.hosts)

    print("Testando ping entre todos os nós....")
    # This performs a basic all pairs ping test.
    net.pingAll()
    
    print("Iniciando conexão TCP...")
    server, client = start_iperf(net)
    print("Executando testes de ping e medições de fila...")
    monitor = start_qmon('s0-eth2',interval_sec=0.05)
    ping_process = start_ping(net)
    ping_process.wait()
    print("Fim do experimento.. liberando recursos")
    monitor.kill()

    net.stop()
    server.kill()
    client.kill()
    # Ensure that all processes you create within Mininet are killed.
    # Sometimes they require manual killing.
    Popen("pgrep -f webserver.py | xargs kill -9", shell=True).wait()



# ping_test()

if __name__ == "__main__":
    bufferbloat()