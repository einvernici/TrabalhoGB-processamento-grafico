
from pathlib import Path
import base64
import tkinter as tk
from tkinter import ttk
import cv2


# Diretórios
base = Path("resultados")
saida = base / "comparacao"
saida.mkdir(parents=True, exist_ok=True)

# Abrir vídeos
video_sequencial = cv2.VideoCapture(
    str(base / "sequencial" / "diferenca_anotado.avi")
)

video_adaptativo = cv2.VideoCapture(
    str(base / "adaptativo" / "adaptativo_anotado.avi")
)

if not video_sequencial.isOpened():
    raise RuntimeError("Não foi possível abrir o vídeo sequencial")

if not video_adaptativo.isOpened():
    raise RuntimeError("Não foi possível abrir o vídeo adaptativo")

# Quantidade de frames
total_sequencial = int(
    video_sequencial.get(cv2.CAP_PROP_FRAME_COUNT)
)

total_adaptativo = int(
    video_adaptativo.get(cv2.CAP_PROP_FRAME_COUNT)
)

# O vídeo sequencial começa no frame original 2.
# O vídeo adaptativo começa no frame original 1.
primeiro_frame = 2
ultimo_frame = min(
    total_sequencial + 1,
    total_adaptativo
)

if ultimo_frame < primeiro_frame:
    raise RuntimeError("Os vídeos não possuem frames suficientes")

# Estado do player
frame_atual = primeiro_frame
reproduzindo = False
intervalo_ms = 40  # Aproximadamente 25 FPS

imagem_sequencial = None
imagem_adaptativa = None


# Interface
janela = tk.Tk()
janela.title("Comparação de métodos - Highway")
janela.geometry("1100x650")

titulo = ttk.Label(
    janela,
    text="Comparação: Método Sequencial x MOG2",
    font=("Arial", 16, "bold")
)
titulo.pack(pady=10)

# Área dos vídeos
painel_videos = ttk.Frame(janela)
painel_videos.pack(pady=10)

painel_sequencial = ttk.Frame(painel_videos)
painel_sequencial.grid(row=0, column=0, padx=10)

painel_adaptativo = ttk.Frame(painel_videos)
painel_adaptativo.grid(row=0, column=1, padx=10)

ttk.Label(
    painel_sequencial,
    text="Método Sequencial (threshold=5)",
    font=("Arial", 11, "bold")
).pack()

ttk.Label(
    painel_adaptativo,
    text="MOG2 (varThreshold=25)",
    font=("Arial", 11, "bold")
).pack()

label_sequencial = ttk.Label(painel_sequencial)
label_sequencial.pack()

label_adaptativo = ttk.Label(painel_adaptativo)
label_adaptativo.pack()

# Número do frame
label_frame = ttk.Label(
    janela,
    text="Frame: 2",
    font=("Arial", 12, "bold")
)
label_frame.pack(pady=5)


def carregar_frame(numero):
    """Carrega o mesmo frame original nos dois vídeos."""

    global imagem_sequencial, imagem_adaptativa

    # Índice do vídeo sequencial:
    # frame original 2 corresponde ao índice 0.
    indice_sequencial = numero - 2

    # Índice do vídeo adaptativo:
    # frame original 1 corresponde ao índice 0.
    indice_adaptativo = numero - 1

    video_sequencial.set(
        cv2.CAP_PROP_POS_FRAMES,
        indice_sequencial
    )

    video_adaptativo.set(
        cv2.CAP_PROP_POS_FRAMES,
        indice_adaptativo
    )

    sucesso_seq, frame_seq = video_sequencial.read()
    sucesso_adap, frame_adap = video_adaptativo.read()

    if not sucesso_seq or not sucesso_adap:
        return None, None

    return frame_seq, frame_adap


def converter_imagem(frame):
    """Converte uma imagem OpenCV para exibição no Tkinter."""

    _, buffer = cv2.imencode(".png", frame)
    dados = base64.b64encode(buffer).decode("ascii")

    return tk.PhotoImage(data=dados)


def atualizar_tela():
    global imagem_sequencial, imagem_adaptativa

    frame_seq, frame_adap = carregar_frame(frame_atual)

    if frame_seq is None or frame_adap is None:
        return

    imagem_sequencial = converter_imagem(frame_seq)
    imagem_adaptativa = converter_imagem(frame_adap)

    label_sequencial.configure(image=imagem_sequencial)
    label_adaptativo.configure(image=imagem_adaptativa)

    label_frame.configure(
        text=f"Frame original: {frame_atual} / {ultimo_frame}"
    )

    escala.set(frame_atual)


def selecionar_frame(valor):
    global frame_atual

    frame_atual = int(float(valor))
    atualizar_tela()


def pausar():
    global reproduzindo

    reproduzindo = False
    botao_play.configure(text="Play")


def reproduzir():
    global reproduzindo

    if not reproduzindo:
        reproduzindo = True
        botao_play.configure(text="Pause")
        avancar_video()


def alternar_reproducao():
    if reproduzindo:
        pausar()
    else:
        reproduzir()


def avancar_video():
    global frame_atual

    if not reproduzindo:
        return

    if frame_atual >= ultimo_frame:
        pausar()
        return

    frame_atual += 1
    atualizar_tela()

    janela.after(intervalo_ms, avancar_video)


def frame_anterior():
    global frame_atual

    pausar()

    if frame_atual > primeiro_frame:
        frame_atual -= 1
        atualizar_tela()


def proximo_frame():
    global frame_atual

    pausar()

    if frame_atual < ultimo_frame:
        frame_atual += 1
        atualizar_tela()


def salvar_screenshot():
    frame_seq, frame_adap = carregar_frame(frame_atual)

    if frame_seq is None or frame_adap is None:
        return

    # Identificação dos métodos
    cv2.putText(
        frame_seq,
        "Sequencial - threshold=5",
        (5, 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (0, 255, 255),
        1
    )

    cv2.putText(
        frame_adap,
        "MOG2 - varThreshold=25",
        (5, 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (0, 255, 255),
        1
    )

    comparacao = cv2.hconcat([frame_seq, frame_adap])

    caminho = saida / f"frame_{frame_atual:06d}.png"

    sucesso = cv2.imwrite(str(caminho), comparacao)

    if sucesso:
        label_status.configure(
            text=f"Screenshot salvo: {caminho.name}"
        )
    else:
        label_status.configure(
            text="Erro ao salvar screenshot"
        )


# Controles
controles = ttk.Frame(janela)
controles.pack(pady=10)

ttk.Button(
    controles,
    text="Anterior",
    command=frame_anterior
).grid(row=0, column=0, padx=5)

botao_play = ttk.Button(
    controles,
    text="Play",
    command=alternar_reproducao
)
botao_play.grid(row=0, column=1, padx=5)

ttk.Button(
    controles,
    text="Próximo",
    command=proximo_frame
).grid(row=0, column=2, padx=5)

ttk.Button(
    controles,
    text="Salvar screenshot",
    command=salvar_screenshot
).grid(row=0, column=3, padx=5)

# Barra de navegação
escala = tk.Scale(
    janela,
    from_=primeiro_frame,
    to=ultimo_frame,
    orient=tk.HORIZONTAL,
    length=850,
    command=selecionar_frame
)
escala.pack(pady=5)

label_status = ttk.Label(janela, text="")
label_status.pack(pady=5)

# Teclas de atalho
janela.bind("<Left>", lambda event: frame_anterior())
janela.bind("<Right>", lambda event: proximo_frame())
janela.bind("<space>", lambda event: alternar_reproducao())

# Exibição inicial
atualizar_tela()

# Encerramento
def encerrar():
    global reproduzindo

    reproduzindo = False
    video_sequencial.release()
    video_adaptativo.release()
    janela.destroy()


janela.protocol("WM_DELETE_WINDOW", encerrar)

janela.mainloop()
