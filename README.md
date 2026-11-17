# Trabalho GB — Tema 3: Detecção de movimento em videomonitoramento

## Base de dados

**CDnet 2014 — Change Detection Benchmark**, categoria **Baseline**, sequência **Highway**.

- 1.700 frames de uma rodovia filmada por uma câmera fixa (320x240).
- `assets/highway/input/`: frames de entrada (`in000001.jpg` a `in001700.jpg`).
- `assets/highway/groundtruth/`: máscaras de referência (`gt000001.png` a `gt001700.png`).
- `assets/highway/ROI.bmp`: região espacial de interesse.
- `assets/highway/temporalROI.txt`: intervalo de avaliação (frames 470 a 1700).

Rótulos das máscaras de referência:

| Valor | Significado | Tratamento |
|---|---|---|
| 0 | Fundo | Entra na avaliação |
| 255 | Movimento | Entra na avaliação |
| 50 | Sombra | Ignorado |
| 170 | Região desconhecida | Ignorado |
| 85 | Fora da região de interesse | Ignorado |

Fonte: https://changedetection.vitalab.usherbrooke.ca/dataset2014/

## Como rodar

Execute os comandos a partir da pasta raiz do projeto, onde estão `assets/`, `src/` e `resultados/`.

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute os métodos finais:

```bash
python src/metodo_sequencial.py
python src/metodo_fundo_adaptativo.py
```

Cada método processa os frames em ordem temporal e gera um vídeo anotado e uma série temporal em CSV.

Para visualizar os dois vídeos sincronizados:

```bash
python src/visualizar_resultados.py
```

O player permite reproduzir, pausar, avançar, voltar e selecionar frames. Também permite salvar screenshots da comparação em `resultados/comparacao/`.

Para comparar as séries temporais:

```bash
python src/comparar_series.py
```

Esse programa gera gráficos de quantidade de regiões e área de foreground, exporta uma tabela comparativa e identifica os frames com maiores divergências entre os métodos.

Para executar os experimentos de parâmetros:

```bash
python experiments/metodo_sequencial.py
python experiments/metodo_fundo_adaptativo.py
```

Esses programas testam diferentes configurações e registram as métricas obtidas.

## Método sequencial: diferença entre frames consecutivos

A ideia: o que se move entre um frame e o seguinte produz uma diferença entre os dois. Como a câmera é fixa, os elementos estáticos da cena tendem a permanecer semelhantes. As mudanças de intensidade são classificadas como movimento.

Para cada frame, em ordem temporal:

1. **Leitura:** carrega o frame colorido.
2. **Cinza e desfoque Gaussiano 5x5:** utiliza `cvtColor` e `GaussianBlur`. A conversão para escala de cinza simplifica a comparação, enquanto o desfoque reduz ruídos.
3. **Diferença:** calcula `|frame atual − frame anterior|` pixel a pixel com `absdiff`. O primeiro frame é armazenado como referência.
4. **Limiarização:** diferenças maiores que o limiar selecionado (5) são classificadas como movimento, gerando uma máscara binária.
5. **Limpeza da máscara:** filtro da mediana 5x5 (`medianBlur`) e dilatação com duas iterações (`dilate`).
6. **Regiões:** `findContours` identifica as regiões brancas. `boundingRect` calcula suas caixas delimitadoras. Regiões com menos de 50 pixels de área de contorno são descartadas.
7. **Série temporal:** registra, por frame, o número de regiões detectadas e a quantidade de pixels brancos da máscara.
8. **Avaliação:** compara as máscaras previstas com as máscaras de referência nos frames 470 a 1700, considerando somente pixels válidos. Calcula TP, FP e FN e, a partir deles, precisão, recall e F1.
9. **Tempo:** mede o processamento do método, sem incluir a leitura dos arquivos do disco, e calcula a média em milissegundos por frame.

**Limitação:** como compara apenas dois frames consecutivos, o método tende a detectar principalmente as bordas dos objetos em movimento. O interior de um veículo com intensidade relativamente uniforme pode não ser detectado. Um veículo parado também deixa de produzir diferenças significativas.

## Método de fundo adaptativo (MOG2)

Em vez de comparar somente o frame atual com o anterior, o método mantém um modelo estatístico do fundo da cena e o atualiza progressivamente. Os pixels que apresentam diferenças significativas em relação ao modelo são classificados como foreground.

Foi utilizada a implementação `createBackgroundSubtractorMOG2` do OpenCV.

Para manter a comparação justa, o método utiliza:

- Mesmo pré-processamento: escala de cinza e desfoque Gaussiano 5x5.
- Mesmo pós-processamento: filtro da mediana 5x5 e dilatação com duas iterações.
- Mesma extração de regiões: contornos, caixas delimitadoras e área mínima de 50 pixels.
- Mesma avaliação: frames 470 a 1700 e exclusão dos rótulos 50, 170 e 85.
- Mesma metodologia de medição de tempo.

Parâmetros selecionados nos experimentos:

| Parâmetro | Valor |
|---|---:|
| `history` | 500 |
| `varThreshold` | 25 |
| `detectShadows` | False |

O modelo é atualizado desde o primeiro frame, inclusive antes do início do intervalo de avaliação.

## Experimentos e resultados

Foram testadas diferentes configurações para cada método, utilizando precisão, recall, F1 e tempo médio de processamento como critérios de comparação.

**Método sequencial — limiar**

Foram testados os limiares 3, 5, 8, 10, 15, 20, 25, 30, 40 e 50.

A configuração selecionada foi `limiar = 5`, que apresentou o maior F1 entre os valores testados.

**Método adaptativo — MOG2**

Foram testados os valores de `varThreshold`: 16, 20, 25, 30, 36 e 49.

A configuração selecionada foi `varThreshold = 25`, com `history = 500` e `detectShadows = False`.

### Comparação dos resultados

| Método | Precisão | Recall | F1 | ms/frame |
|---|---:|---:|---:|---:|
| Sequencial (threshold=5) | 0,760 | 0,946 | 0,843 | 0,44 |
| MOG2 (varThreshold=25) | 0,876 | 0,876 | 0,876 | 1,75 |

Os resultados exploratórios indicam que o método sequencial apresenta maior recall, mas menor precisão. O MOG2 apresenta melhor equilíbrio entre precisão e recall, com F1 superior, porém demanda aproximadamente quatro vezes mais tempo de processamento.

**Observação sobre a avaliação:** os experimentos de seleção de parâmetros e os resultados acima utilizaram o mesmo intervalo de ground truth (frames 470 a 1700). Portanto, esses resultados são exploratórios. Ainda é necessário separar os dados utilizados para ajuste dos parâmetros daqueles utilizados na avaliação final, conforme o requisito experimental do trabalho.

## Comparação das séries temporais

Os arquivos CSV permitem acompanhar, ao longo do vídeo:

- Quantidade de regiões detectadas por frame.
- Área total de foreground em pixels.

O programa `comparar_series.py` produz gráficos comparativos e identifica os frames com maiores divergências entre os métodos.

A análise inicial identificou divergências expressivas, especialmente nos frames 300 a 313. No frame 310, por exemplo, o método sequencial detectou 6.625 pixels de foreground, enquanto o MOG2 detectou 49.107.

Também foram identificadas diferenças na quantidade de regiões, como no frame 312, em que o sequencial detectou 3 regiões e o MOG2 detectou 33.

Essas divergências foram selecionadas para investigação visual. A diferença entre as máscaras não significa, por si só, que um método tenha produzido uma detecção incorreta: é necessário comparar as máscaras com o ground truth.

## Saídas (pasta `resultados/`)

| Diretório / arquivo | Conteúdo |
|---|---|
| `sequencial/diferenca_anotado.avi` | Vídeo do método sequencial com caixas delimitadoras |
| `sequencial/diferenca_serie.csv` | Série temporal do método sequencial |
| `adaptativo/adaptativo_anotado.avi` | Vídeo do MOG2 com caixas delimitadoras |
| `adaptativo/adaptativo_serie.csv` | Série temporal do MOG2 |
| `experimentos/sequencial/` | Relatórios, resultados individuais e gráfico dos limiares testados |
| `experimentos/adaptativo/` | Relatórios, resultados individuais e gráfico dos valores de `varThreshold` |
| `comparacao/` | Gráficos, CSV comparativo e screenshots dos vídeos |

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
├── requirements.txt
└── .gitignore
```

## Referências

- Wang et al., *CDnet 2014: An Expanded Change Detection Benchmark Dataset*, CVPRW 2014.
- Documentação OpenCV: https://docs.opencv.org/
- Documentação do BackgroundSubtractorMOG2: https://docs.opencv.org/4.x/d7/d7b/classcv_1_1BackgroundSubtractorMOG2.html
