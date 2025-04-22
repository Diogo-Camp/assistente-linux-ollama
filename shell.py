import subprocess
import shlex
import os

def main():
    print("Bem vindo ao mini shell")
    while True:
        try:
            #mostra o diretorio atual como prompt
            cwd = os.getcwd()
            command_input = input(f"{cwd} >> ")

            #se vazio, continua.
            if not command_input.strip():
                continue

            if command_input.strip() in ["exit", "sair", "quit"]:
                print("Saindo do minishell")
                break

            #tokeniza respeitando aspas e espacos
            tokens = shlex.split(command_input)

            if tokens[0] == "cd":
                if len(tokens) > 1:
                    try:
                        os.chdir(tokens[1])
                    except FileNotFoundError:
                        print("diretorio nao encontrado")
                else:
                    os.chdir(os.path.expanduser("~"))
                continue

            result = subprocess.run(tokens, capture_output=True, text=True)

            #executa comando interno
            if result.stdout:
                print(result.stdout, end='')
            if result.stderr:
                print(result.stderr, end='')
        except KeyboardInterrupt:
            print("\nInterrompido com ctrl c ctrl v")
        except EOFError:
            print("eof detectado (ctrl + d), saindo..")
        except Exception as e:
            print(f"Erro inesperado {e}")

if __name__ == "__main__":
        main()
