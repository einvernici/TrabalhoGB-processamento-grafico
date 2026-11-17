
from pathlib import Path
import cv2
import numpy as np

# Diretórios
base = Path("assets/highway")
saida = Path("resultados") / "sequencial"
saida.mkdir(parents=True, exist_ok=True)

# Parâmetro selecionado nos experimentos
limiar = 5

# Quantidade de frames
total = len(list((base / "input").glob("in*.jpg")))

if total == 0:
    raise FileNotFoundError("Nenhum frame encontrado na pasta input")

# Variáveis de processamento
frame_anterior = None
gravador = None
serie = []

for i in range(1, total + 1):
    frame = cv2.imread(
        str(base / "input" / f"in{i:06d}.jpg")
    )

    if frame is None:
        raise FileNotFoundError(f"Não foi possível abrir o frame {i}")

    # 1. Pré-processamento
    atual = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    atual = cv2.GaussianBlur(atual, (5, 5), 0)

    # O primeiro frame serve apenas como referência
    if frame_anterior is None:
        frame_anterior = atual
        continue

    # 2. Diferença entre frames consecutivos
    diferenca = cv2.absdiff(frame_anterior, atual)

    _, movimento = cv2.threshold(
        diferenca,
        limiar,
        255,
        cv2.THRESH_BINARY
    )

    # 3. Pós-processamento
    movimento = cv2.medianBlur(movimento, 5)
    movimento = cv2.dilate(movimento, None, iterations=2)

    # 4. Detecção de regiões
    contornos, _ = cv2.findContours(
        movimento,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    quantidade = 0

    for contorno in contornos:
        if cv2.contourArea(contorno) < 50:
            continue

        x, y, largura, altura = cv2.boundingRect(contorno)

        cv2.rectangle(
            frame,
            (x, y),
            (x + largura, y + altura),
            (0, 255, 0),
            1
        )

        quantidade += 1

    # 5. Área total de foreground
    area = np.count_nonzero(movimento)

    # 6. Atualização da referência temporal
    frame_anterior = atual

    # 7. Registro dos dados por frame
    serie.append((i, quantidade, area))

    # 8. Gravação do vídeo anotado
    if gravador is None:
        altura_video, largura_video = frame.shape[:2]
        codec = cv2.VideoWriter_fourcc(*"MJPG")

        gravador = cv2.VideoWriter(
            str(saida / "diferenca_anotado.avi"),
            codec,
            25,
            (largura_video, altura_video),
            isColor=True
        )

        if not gravador.isOpened():
            raise RuntimeError("Não foi possível criar o vídeo")

    gravador.write(frame)

# Liberação dos recursos
if gravador is not None:
    gravador.release()

# 9. Exportação da série temporal
arquivo_csv = saida / "diferenca_serie.csv"

with open(arquivo_csv, "w", encoding="utf-8") as arquivo:
    arquivo.write("frame,n_regioes,area_pixels\n")

    for frame_i, quantidade, area in serie:
        arquivo.write(f"{frame_i},{quantidade},{area}\n")

print("Processamento sequencial concluído.")
print(f"Frames processados: {len(serie)}")
print(f"Vídeo salvo em: {saida / 'diferenca_anotado.avi'}")
print(f"Série temporal salva em: {arquivo_csv}")
