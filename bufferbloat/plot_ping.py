'''
Plot ping RTTs over time
'''
from helper import *
import plot_defaults

from matplotlib.ticker import MaxNLocator
from pylab import figure

parser = argparse.ArgumentParser()
parser.add_argument('--files', '-f',
                    help="Ping output files to plot",
                    required=True,
                    action="store",
                    nargs='+')

parser.add_argument('--freq',
                    help="Frequency of pings (per second)",
                    type=int,
                    default=10)

parser.add_argument('--out', '-o',
                    help="Output png file for the plot.",
                    default=None) # Will show the plot

args = parser.parse_args()

def parse_ping(fname):
    ret = []
    lines = open(fname).readlines()
    start_time = None
    for line in lines:
        if 'bytes from' not in line:
            continue
        try:
            rtt = line.split(' ')[-2]
            rtt = rtt.split('=')[1]
            rtt = float(rtt)
            timestamp = float(line.split("]")[0][1:])
            if start_time is None:
                start_time = timestamp - rtt/1000
            ret.append([timestamp-start_time,rtt])
        except:
            break
    return ret

m.rc('figure', figsize=(16, 10))
fig = figure()
ax = fig.add_subplot()
for i, f in enumerate(args.files):
    data = parse_ping(f)
    xaxis = list(map(float, list(col(0, data))))
    start_time = xaxis[0]
    # print(data, start_time)
    xaxis = list(xaxis)
    qlens = list(map(float, col(1, data)))

    ax.plot(xaxis, qlens, lw=2)
    ax.xaxis.set_major_locator(MaxNLocator(4))

plt.ylabel("RTT (ms)")
plt.grid(True)
if args.out:
    qsize = args.out.split('q')[1].split('.')[0]
    plt.title(f"RTT for elapsed time. Q max size = {qsize}")
    plt.savefig(args.out)
else:
    plt.show()
