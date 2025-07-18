#!/bin/bash
time=60


mn -c > /dev/null 2>&1

# Cenário 2
python3 competition.py --num-bbr=2 --num-reno=2 -t=$time 

# Cenário 3
python3 competition.py --num-bbr=1 --num-reno=2 -t=$time 

# Cenário 1
python3 competition.py --num-bbr=1 --num-reno=1 -t=$time 


echo -e "Recomendação: Gere a animação sobre justiça(fairness) dos cenários fora da VM. Comando:\n
        \"python3 competition.py -nbbr 1 -nreno 1 --task gif\""
        
