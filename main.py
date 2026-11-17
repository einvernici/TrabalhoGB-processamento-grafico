from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def executar(caminho_relativo):
    caminho = ROOT / caminho_relativo

    if not caminho.is_file():
        print(f"\nArquivo não encontrado: {caminho_relativo}")
        return

    print(f"\nExecutando {caminho_relativo}...\n")
    resultado = subprocess.run(
        [sys.executable, str(caminho)],
        cwd=ROOT
    )

    if resultado.returncode != 0:
        print(f"\nO programa terminou com código {resultado.returncode}.")


def menu():
    opcoes = {
        "1": ("Método sequencial", "src/metodo_sequencial.py"),
        "2": ("Método de fundo adaptativo (MOG2)", "src/metodo_fundo_adaptativo.py"),
        "3": ("Comparar séries temporais", "src/comparar_series.py"),
        "4": ("Abrir player de comparação", "src/visualizar_resultados.py"),
        "5": ("Experimentos do método sequencial", "experiments/metodo_sequencial.py"),
        "6": ("Experimentos do MOG2", "experiments/metodo_fundo_adaptativo.py"),
    }

    while True:
        print("\n=== Detecção de movimento em videomonitoramento ===")
        for numero, (descricao, _) in opcoes.items():
            print(f"{numero}. {descricao}")
        print("0. Sair")

        escolha = input("\nSelecione uma opção: ").strip()

        if escolha == "0":
            print("Encerrando.")
            break
        elif escolha in opcoes:
            descricao, caminho = opcoes[escolha]
            executar(caminho)
            input("\nPressione Enter para voltar ao menu...")
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")
