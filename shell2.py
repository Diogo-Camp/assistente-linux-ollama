import subprocess
import shlex
import os

def main():
    print("Bem vindo ao minishell v2")
    while True:
        try:
            #mostra o diretorio atual como prompt
            cwd = os.getcwd()
            command_input = input(f"{cwd} >> ")

            #se for vazio, continua
            if not command_input.strip():
                continue
            
            #comando p sair
            if command_input.strip() in ['exit', 'sair', 'quit']:
                print("Saindo do minishell v2")
                break

            #tokeniza respeitando aspas e espacos
            tokens = shlex.split(command_input)

            #comando interno: cd (precisa ser tratado fora do subprocess)
            if tokens[0] == "cd":
                if len(tokens) > 1:
                    try:
                        os.chdir(tokens[1])
                    except FileNotFoundError:
                        print("DIretorio nao encontrado")
                else:
                    os.chdir(os.path.expanduser("~")) #volta p home
                    continue

            #executa o comando externo
            result = subprocess.run(tokens, capture_output=True, text=True)
            
            #mostra stdout e stderr se houver
            if result.stdout:
                print(result.stdout, end='')

            if result.stderr:
                print(result.stderr, end='')
        except KeyboardInterrupt:
            print("\n INterrompido com ctrl + c")
        except EOFError:
            print("\n EOF detectado (ctrl + d), saindo..")
            break
        except Exception as e:
            print(f"Erro inesperado {e}")

if __name__ == "__main__":
    main()
            
