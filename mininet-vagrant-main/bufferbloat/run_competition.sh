#!/bin/bash
time=60

mkdir -p $dir

for qsize in 20 100; do
# qsize=100
    mn -c > /dev/null 2>&1

    # Cenário 1
    python3 competition.py --num-bbr=1 --num-reno=1 -t=$time 

    # Cenário 2
    python3 competition.py --num-bbr=2 --num-reno=2 -t=$time 
    
    # Cenário 3
    python3 competition.py --num-bbr=1 --num-reno=2 -t=$time 

done
