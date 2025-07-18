#!/bin/bash

# Note: Mininet must be run as root.  So invoke this shell script
# using sudo.

time=90
bwnet=1.5
delay=5
cong=reno

iperf_port=5001
dir=data
mkdir -p $dir

for qsize in 20 100; do
# qsize=100
    mn -c > /dev/null 2>&1

    # TODO: Run bufferbloat.py here...
    python3 bufferbloat.py -b=1.5 --delay=$delay --dir=$dir -t=$time --maxq=$qsize --cong=$cong

    # TODO: Ensure the input file names match the ones you use in
    # bufferbloat.py script.  Also ensure the plot file names match
    # the required naming convention when submitting your tarball.

    mkdir -p plots
    python3 plot_queue.py -f $dir/qlen$qsize.txt -o plots/$cong-buffer-q$qsize.png --cong=$cong
    python3 plot_ping.py -f $dir/ping$qsize.txt -o plots/$cong-rtt-q$qsize.png --cong=$cong
done
