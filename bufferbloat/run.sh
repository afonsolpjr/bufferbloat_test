#!/bin/bash

# Note: Mininet must be run as root.  So invoke this shell script
# using sudo.

time=10
bwnet=1.5
# TODO: If you want the RTT to be 20ms what should the delay on each
# link be?  Set this value correctly.
delay=5

iperf_port=5001
dir=data
mkdir -p $dir

for qsize in 20 100; do
# qsize=100
    mn -c > /dev/null 2>&1

    # TODO: Run bufferbloat.py here...
    python3 bufferbloat.py -b=1.5 --delay=$delay --dir=$dir -t=$time --maxq=$qsize

    # TODO: Ensure the input file names match the ones you use in
    # bufferbloat.py script.  Also ensure the plot file names match
    # the required naming convention when submitting your tarball.
    mkdir -p plots
    python3 plot_queue.py -f $dir/qlen$qsize.txt -o plots/reno-buffer-q$qsize.png
    python3 plot_ping.py -f $dir/ping$qsize.txt -o plots/reno-rtt-q$qsize.png
done
