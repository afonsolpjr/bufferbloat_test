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


#### run_competition.sh (Parte 4)

