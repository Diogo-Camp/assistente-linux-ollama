import subprocess

comando = "ls -la"
saida = subprocess.run(comando, shell=True, capture_output=True, text=True)
print(saida.stdout)
