
from pathlib import Path
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt

base = Path("assets/highway")
saida = Path("resultados")
saida.mkdir(exist_ok=True)

limiares = [3, 5, 8, 10, 15, 20, 25, 30, 40, 50]

pasta_experimentos = saida / "experimentos" / "sequencial"
pasta_experimentos.mkdir(parents=True, exist_ok=True)

with open(base / "temporalROI.txt") as arquivo:
    inicio_aval, fim_aval = arquivo.read().split()

inicio_aval = int(inicio_aval)
fim_aval = int(fim_aval)

roi = cv2.imread(str(base / "ROI.bmp"), cv2.IMREAD_GRAYSCALE)
if roi is None:
    raise FileNotFoundError("Não foi possível abrir a ROI")

total = len(list((base / "input").glob("in*.jpg")))


def executar_experimento(limiar):
    print(f"Executando experimento com limiar={limiar}...")

    frame_anterior = None

    tp = 0
    fp = 0
    fn = 0

    tempo_total = 0.0
    quantidade_frames = 0

    for i in range(1, total + 1):
        frame = cv2.imread(str(base / "input" / f"in{i:06d}.jpg"))
        if frame is None:
            raise FileNotFoundError(f"Não foi possível abrir o frame {i}")

        inicio = time.perf_counter()

        atual = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        atual = cv2.GaussianBlur(atual, (5, 5), 0)

        if frame_anterior is None:
            frame_anterior = atual
            continue

        diferenca = cv2.absdiff(frame_anterior, atual)

        _, movimento = cv2.threshold(
            diferenca, limiar, 255, cv2.THRESH_BINARY
        )

        movimento = cv2.medianBlur(movimento, 5)
        movimento = cv2.dilate(movimento, None, iterations=2)

        contornos, _ = cv2.findContours(
            movimento, cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        quantidade = 0
        for contorno in contornos:
            if cv2.contourArea(contorno) < 50:
                continue
            quantidade += 1

        area = np.count_nonzero(movimento)

        frame_anterior = atual

        tempo_total += time.perf_counter() - inicio
        quantidade_frames += 1

        if inicio_aval <= i <= fim_aval:
            gt = cv2.imread(
                str(base / "groundtruth" / f"gt{i:06d}.png"),
                cv2.IMREAD_GRAYSCALE
            )
            if gt is None:
                raise FileNotFoundError(f"Não foi possível abrir o GT {i}")

            validos = (roi > 0) & (gt != 50) & (gt != 170) & (gt != 85)

            real = gt == 255
            previsto = movimento > 0

            tp += np.count_nonzero(previsto & real & validos)
            fp += np.count_nonzero(previsto & ~real & validos)
            fn += np.count_nonzero(~previsto & real & validos)

    precisao = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    f1 = (
        2 * precisao * recall / (precisao + recall)
        if (precisao + recall) > 0 else 0
    )

    tempo_medio = (
        tempo_total / quantidade_frames * 1000
        if quantidade_frames > 0 else 0
    )

    texto = (
        "Investigação - método sequencial (diferença de frames)\n"
        f"Parâmetros: limiar={limiar}\n\n"
        f"Resultados quantitativos (frames {inicio_aval}-{fim_aval}):\n"
        f"  Precisão = {precisao:.3f}\n"
        f"  Recall   = {recall:.3f}\n"
        f"  F1       = {f1:.3f}\n\n"
        f"Tempo de processamento: {tempo_medio:.2f} ms/frame\n"
    )

    print(texto)

    arquivo_txt = pasta_experimentos / f"threshold_{limiar}.txt"
    with open(arquivo_txt, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)

    return {
        "limiar": limiar,
        "precisao": precisao,
        "recall": recall,
        "f1": f1,
        "tempo": tempo_medio
    }


# Executa todos os experimentos
resultados = []

for limiar in limiares:
    resultado = executar_experimento(limiar)
    resultados.append(resultado)


# Gera o gráfico de comparação
valores_limiares = [r["limiar"] for r in resultados]
precisoes = [r["precisao"] for r in resultados]
recalls = [r["recall"] for r in resultados]
f1_scores = [r["f1"] for r in resultados]

plt.figure(figsize=(10, 6))

plt.plot(valores_limiares, precisoes, marker="o", label="Precisão")
plt.plot(valores_limiares, recalls, marker="o", label="Recall")
plt.plot(valores_limiares, f1_scores, marker="o", label="F1-score")

plt.title("Método sequencial - influência do limiar")
plt.xlabel("Limiar")
plt.ylabel("Métrica")
plt.ylim(0, 1)
plt.xticks(valores_limiares)
plt.grid(True)
plt.legend()
plt.tight_layout()

grafico = pasta_experimentos / "comparacao_thresholds.png"
plt.savefig(grafico, dpi=150)
plt.close()

print(f"Gráfico salvo em: {grafico}")
print("Todos os experimentos foram concluídos.")
