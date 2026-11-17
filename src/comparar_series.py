
from pathlib import Path
import csv
import matplotlib.pyplot as plt

# Diretórios
base = Path("resultados")
saida = base / "comparacao"
saida.mkdir(parents=True, exist_ok=True)


def carregar_serie(caminho):
    dados = {}

    with open(caminho, "r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            frame = int(linha["frame"])

            dados[frame] = {
                "n_regioes": int(linha["n_regioes"]),
                "area_pixels": int(linha["area_pixels"])
            }

    return dados


# Carregar séries temporais
sequencial = carregar_serie(
    base / "sequencial" / "diferenca_serie.csv"
)

adaptativo = carregar_serie(
    base / "adaptativo" / "adaptativo_serie.csv"
)

# Comparar apenas frames presentes nos dois arquivos
frames = sorted(set(sequencial) & set(adaptativo))

if not frames:
    raise ValueError("Não existem frames em comum entre as séries")

regioes_seq = [sequencial[f]["n_regioes"] for f in frames]
regioes_adap = [adaptativo[f]["n_regioes"] for f in frames]

area_seq = [sequencial[f]["area_pixels"] for f in frames]
area_adap = [adaptativo[f]["area_pixels"] for f in frames]

# Diferenças absolutas
dif_regioes = [
    abs(a - b) for a, b in zip(regioes_seq, regioes_adap)
]

dif_area = [
    abs(a - b) for a, b in zip(area_seq, area_adap)
]

# 1. Gráfico de quantidade de regiões
plt.figure(figsize=(14, 6))

plt.plot(
    frames,
    regioes_seq,
    label="Sequencial (threshold=5)",
    alpha=0.8
)

plt.plot(
    frames,
    regioes_adap,
    label="MOG2 (varThreshold=25)",
    alpha=0.8
)

plt.title("Comparação temporal - quantidade de regiões")
plt.xlabel("Frame")
plt.ylabel("Quantidade de regiões")
plt.legend()
plt.grid(True)
plt.tight_layout()

grafico_regioes = saida / "comparacao_regioes.png"
plt.savefig(grafico_regioes, dpi=150)
plt.close()

# 2. Gráfico de área de foreground
plt.figure(figsize=(14, 6))

plt.plot(
    frames,
    area_seq,
    label="Sequencial (threshold=5)",
    alpha=0.8
)

plt.plot(
    frames,
    area_adap,
    label="MOG2 (varThreshold=25)",
    alpha=0.8
)

plt.title("Comparação temporal - área de foreground")
plt.xlabel("Frame")
plt.ylabel("Área (pixels)")
plt.legend()
plt.grid(True)
plt.tight_layout()

grafico_area = saida / "comparacao_area.png"
plt.savefig(grafico_area, dpi=150)
plt.close()

# 3. Exportação das diferenças por frame
arquivo_csv = saida / "comparacao_series.csv"

with open(arquivo_csv, "w", newline="", encoding="utf-8") as arquivo:
    campos = [
        "frame",
        "regioes_sequencial",
        "regioes_adaptativo",
        "diferenca_regioes",
        "area_sequencial",
        "area_adaptativo",
        "diferenca_area"
    ]

    escritor = csv.DictWriter(arquivo, fieldnames=campos)
    escritor.writeheader()

    for i, frame in enumerate(frames):
        escritor.writerow({
            "frame": frame,
            "regioes_sequencial": regioes_seq[i],
            "regioes_adaptativo": regioes_adap[i],
            "diferenca_regioes": dif_regioes[i],
            "area_sequencial": area_seq[i],
            "area_adaptativo": area_adap[i],
            "diferenca_area": dif_area[i]
        })

# 4. Identificar maiores divergências
maiores_regioes = sorted(
    zip(dif_regioes, frames),
    reverse=True
)[:10]

maiores_area = sorted(
    zip(dif_area, frames),
    reverse=True
)[:10]

print("\nComparação das séries temporais")
print(f"Frames comparados: {len(frames)}")

print("\n10 maiores divergências na quantidade de regiões:")
for diferenca, frame in maiores_regioes:
    print(
        f"Frame {frame}: diferença={diferenca} "
        f"(sequencial={sequencial[frame]['n_regioes']}, "
        f"MOG2={adaptativo[frame]['n_regioes']})"
    )

print("\n10 maiores divergências na área de foreground:")
for diferenca, frame in maiores_area:
    print(
        f"Frame {frame}: diferença={diferenca} pixels "
        f"(sequencial={sequencial[frame]['area_pixels']}, "
        f"MOG2={adaptativo[frame]['area_pixels']})"
    )

print("\nArquivos gerados:")
print(grafico_regioes)
print(grafico_area)
print(arquivo_csv)
