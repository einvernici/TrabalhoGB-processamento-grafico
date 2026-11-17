# Trabalho GB — Tema 3: Detecção de movimento em videomonitoramento

## Sobre o projeto

Este projeto investiga a detecção de movimento em uma sequência de videomonitoramento de uma rodovia, utilizando técnicas clássicas de processamento de imagens com Python e OpenCV.

Foram implementadas duas abordagens:

- **Método sequencial:** detecção de movimento pela diferença entre frames consecutivos.
- **Método de fundo adaptativo (MOG2):** detecção baseada em um modelo estatístico do fundo da cena, atualizado progressivamente.

Os métodos processam os frames em ordem temporal, geram máscaras de movimento, identificam regiões detectadas e produzem vídeos anotados e séries temporais. Os resultados são comparados utilizando máscaras de referência (*ground truth*).

A metodologia experimental, os resultados quantitativos e a discussão estão disponíveis no [Relatório Técnico](RELATORIO_TECNICO.md).

## Base de dados

**CDnet 2014 — Change Detection Benchmark**, categoria **Baseline**, sequência **Highway**.

- 1.700 frames de uma rodovia filmada por uma câmera fixa.
- Resolução: 320 × 240 pixels.
- `assets/highway/input/`: frames de entrada (`in000001.jpg` a `in001700.jpg`).
- `assets/highway/groundtruth/`: máscaras de referência (`gt000001.png` a `gt001700.png`).
- `assets/highway/ROI.bmp`: região espacial de interesse.
- `assets/highway/temporalROI.txt`: intervalo de avaliação (frames 470 a 1700).

Rótulos das máscaras de referência:

| Valor | Significado | Tratamento |
|---|---|---|
| 0 | Fundo | Avaliado |
| 255 | Movimento | Avaliado |
| 50 | Sombra | Ignorado |
| 170 | Região desconhecida | Ignorado |
| 85 | Fora da região de interesse | Ignorado |

Fonte: [CDnet 2014](https://changedetection.vitalab.usherbrooke.ca/dataset2014/).

## Requisitos

- Python 3
- OpenCV
- NumPy
- Matplotlib

O player de comparação utiliza Tkinter, normalmente incluído nas instalações padrão do Python para Windows.

Instale as dependências a partir da pasta raiz do projeto:

```bash
python -m pip install -r requirements.txt
```

## Como executar

Execute os comandos a partir da pasta raiz do projeto.

### Menu principal

```bash
python main.py
```

O menu permite:

1. Executar o método sequencial.
2. Executar o método adaptativo (MOG2).
3. Executar os dois métodos.
4. Comparar as séries temporais.
5. Abrir o player de comparação.
6. Executar os experimentos de seleção de parâmetros.

### Execução direta dos métodos

```bash
python src/metodo_sequencial.py
python src/metodo_fundo_adaptativo.py
```

Cada método processa a sequência e gera:

- Um vídeo anotado com as regiões detectadas.
- Um arquivo CSV com a quantidade de regiões e a área de foreground por frame.
- Métricas de precisão, recall e F1.
- Tempo total medido e tempo médio de processamento por frame.

### Visualização dos vídeos

```bash
python src/visualizar_resultados.py
```

O player permite reproduzir, pausar, avançar, voltar e selecionar frames dos dois vídeos sincronizados. Também permite salvar capturas da comparação em `resultados/comparacao/`.

### Comparação das séries temporais

```bash
python src/comparar_series.py
```

Gera gráficos comparativos da quantidade de regiões e da área de foreground, além de uma tabela CSV com os valores registrados pelos dois métodos.

### Experimentos de parâmetros

```bash
python experiments/metodo_sequencial.py
python experiments/metodo_fundo_adaptativo.py
```

Esses programas testam diferentes configurações e registram as métricas obtidas para cada uma delas.

## Arquivos gerados

Os resultados são armazenados na pasta `resultados/`.

| Diretório / arquivo | Conteúdo |
|---|---|
| `sequencial/diferenca_anotado.avi` | Vídeo anotado do método sequencial |
| `sequencial/diferenca_serie.csv` | Série temporal do método sequencial |
| `adaptativo/adaptativo_anotado.avi` | Vídeo anotado do MOG2 |
| `adaptativo/adaptativo_serie.csv` | Série temporal do MOG2 |
| `experimentos/sequencial/` | Relatórios e gráficos dos testes de limiar |
| `experimentos/adaptativo/` | Relatórios e gráficos dos testes de `varThreshold` |
| `comparacao/` | Gráficos, CSV comparativo e capturas dos vídeos |

## Reprodutibilidade

Para reproduzir os experimentos:

1. Mantenha o dataset CDnet 2014 na estrutura de diretórios descrita acima.
2. Instale as dependências listadas em `requirements.txt`.
3. Execute os scripts a partir da raiz do projeto.
4. Utilize os scripts em `experiments/` para repetir os testes de parâmetros.
5. Execute os métodos finais para gerar novamente os vídeos, séries temporais e métricas.

A avaliação utiliza o intervalo temporal e a ROI fornecidos pelo dataset. Os rótulos de sombra, região desconhecida e pixels fora da ROI são excluídos dos cálculos.

**Observação experimental:** os resultados atualmente registrados são exploratórios, pois os mesmos frames foram utilizados na seleção dos parâmetros e na avaliação. Uma avaliação final independente exige separar os dados de ajuste daqueles utilizados para calcular os resultados finais.

O tempo de processamento considera as operações de processamento de imagem, excluindo leitura dos arquivos, leitura do *ground truth*, desenho das caixas delimitadoras e gravação dos vídeos.

## Estrutura do projeto

```text
trabalho-processamento-grafico-highway/
├── assets/
│   └── highway/
│       ├── input/
│       ├── groundtruth/
│       ├── ROI.bmp
│       ├── ROI.jpg
│       └── temporalROI.txt
├── experiments/
│   ├── metodo_sequencial.py
│   └── metodo_fundo_adaptativo.py
├── src/
│   ├── metodo_sequencial.py
│   ├── metodo_fundo_adaptativo.py
│   ├── visualizar_resultados.py
│   └── comparar_series.py
├── resultados/
├── main.py
├── README.md
├── RELATORIO_TECNICO.md
├── requirements.txt
└── .gitignore
```

## Referências

- Wang et al., *CDnet 2014: An Expanded Change Detection Benchmark Dataset*, CVPRW 2014.
- [Documentação OpenCV](https://docs.opencv.org/).
- [Documentação do BackgroundSubtractorMOG2](https://docs.opencv.org/4.x/d7/d7b/classcv_1_1BackgroundSubtractorMOG2.html).