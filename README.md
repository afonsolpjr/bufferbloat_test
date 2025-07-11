# bufferbloat_test


## Instruções para reprodução

###  Preparativos e dependências
Primeiro, descompacte o arquivo `mininet-vagrant-main.zip`, mude o diretório de trabalho para o diretório resultante e, se necessário, inicie o vagrant

```shell
unzip mininet-vagrant-main.zip
cd mininet-vagrant-main
vagrant up
```

Uma vez que a máquina virtual estiver em execução, precisamos copiar os códigos para lá. Para isso, use o plugin do vagrant `vagrant-scp`, que pode ser instalado com:
```shell
vagrant plugin install vagrant-scp
```

Depois de instalado, pode copiar o diretório que contém os códigos (`bufferfloat/`) para a máquina virtual com:

```shell
vagrant scp ../bufferbloat default:~ 
```

### Executando
Para executar o script, execute na máquina virtual:
```shell
sudo ./run.sh
```

A saída será armazenada em dois diretórios na máquina virtual. Os gráficos ficam no diretório `plots/` e os dados utilizados para construí-los, bem como dados adicionais coletados como a média de tempo de download ficam no diretório `data`. Para trazê-las para a sua máquina física, execute:
```shell
vagrant scp default:~/bufferbloat/plots .
vagrant scp default:~/bufferbloat/data .
```

## Resultados
As médias de tempos de download encontradas nos experimentos foram as seguintes:

| Tamanho da fila | Média | Desvio padrão |
|-----------------|-------|----------------|
| 20              | 2.68  | 0.5            |
| 100             | 10.19 | 2.65           |