# bufferbloat_test


## Instruções para reprodução

###  Preparativos e dependências
Primeiro, mude o diretório de trabalho para o diretório `mininet-vagrant-main` e inicie a máquina virtual

```shell
cd mininet-vagrant-main
vagrant up
```

Depois, acesse a máquina virtual e vá ao diretório compartilhado com:
```shell
vagrant ssh
cd /vagrant/bufferbloat
```

Finalmente, para instalar todas as dependências necessárias execute, ainda nesse diretório da máquina virtual:
```shell
sudo ./setup.sh
```

Esse comando instala o pip3 e todos os pacotes python necessários, além do iperf3, que não vem por padrão em muitas das máquinas virtuais.

### Executando

No total, desenvolvemos 3 scripts. Um para a parte 2, chamado `run.sh`, outro para a parte 3, chamado `run_bbr.sh` e outro para a parte 4, chamado `run_competition.sh`. Nessa seção, vamos acompanhar o processo para rodar cada um deles e interpretar os resultados.

Para **todos** os scripts, presumimos que você esteja na máquina virtual, no diretório `/vagrant/bufferbloat/`, como orientado nas seções anteriores

#### run.sh (Parte 2)

Para executar, simplesmente:
```shell
sudo ./run.sh
```

A saída será armazenada em dois diretórios. Os gráficos ficam no diretório `plots/` e são nomeados:
1. `reno-buffer-q20.png`
1. `reno-rtt-q20.png`
1. `reno-buffer-q100.png`
1. `reno-rtt-q100.png`

e os dados utilizados para construí-los, bem como dados adicionais coletados como a média de tempo de download ficam no diretório `data`. Todos esses gráficos e dados são replicados no diretório `mininet-vagrant-main/` da sua máquina física, sob a raíz do projeto.

Esse script também computa os tempos de downloads da página web que simulamos. Na experimentação, obtivemos os seguintes resultados para esses tempos de download:

| Tamanho da fila | Média | Desvio padrão |
|-----------------|-------|----------------|
| 20              | 2.68  | 0.5            |
| 100             | 10.19 | 2.65           |


#### run_bbr.sh (Parte 3)
Pode ser executado com:
```shell
sudo ./run_bbr.sh
```

Gera exatamente as mesmas saídas que o script da seção anterior, mas na simulação utiliza o TCP BBR. Os nomes dos plots são prefixados com `bbr` ao invés de `reno`, e os dados textuais sobrescrevem os gerados pelo script anterior. Listando os gráficos de saída, temos:
1. `bbr-buffer-q20.png`
1. `bbr-rtt-q20.png`
1. `bbr-buffer-q100.png`
1. `bbr-rtt-q100.png`

Nesse caso, os dados que obtivemos sobre os tempos de download da página web foram:

| Tamanho da fila | Média | Desvio padrão |
|-----------------|-------|----------------|
| 20              | 2.29  | 0.75            |
| 100             | 1.8 | 0.05           |

#### run_competition.sh (Parte 4)
Esse script executa simulações de todos os cenários da parte 4 (exceto o bônus). Para executá-lo, use:

```shell
sudo ./run_competition.sh
```

A saída dele é no formato de plots, 3 para cada cenário, sendo eles:
1. `Bandwidth_1bbrVS1reno.png`
1. `Bandwidth_1bbrVS2reno.png`
1. `Bandwidth_2bbrVS2reno.png`
1. `Rtry_1bbrVS1reno.png`
1. `Rtry_1bbrVS2reno.png`
1. `Rtry_2bbrVS2reno.png`
1. `RTT_1bbrVS1reno.png`
1. `RTT_1bbrVS2reno.png`
1. `RTT_2bbrVS2reno.png`


#### Cenário bônus
Observamos que o código que gera o gráfico de eficiência versus fairness demora muito para terminar de rodar na máquina virtual, e por isso, sugerimos que rode na sua máquina física. Para executá-lo:
```shell
python3 competition.py -nbbr 1 -nreno 1 --task gif
```
