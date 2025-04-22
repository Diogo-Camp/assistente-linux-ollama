import os
import json
import requests
import subprocess
from datetime import datetime

OLLAMA_HOST = "http://localhost:11434"
HISTORICO_PATH = "./historico_conversas"
os.makedirs(HISTORICO_PATH, exist_ok=True)

LIMITE_MENSAGENS = 10

# Estado do shell para manter contexto entre comandos como cd, pwd, etc
estado_shell = {
    "cwd": os.getcwd()
}

# === PERSONALIDADE SYSADMIN ROBÔ ===
def carregar_personalidade():
    return {
        "role": "system",
        "content": (
            "Você é um sysadmin experiente, sarcástico e direto. "
            "Seu trabalho é auxiliar o usuário no uso do terminal Linux, explicando comandos como ls -la, chmod, ps aux, e analisando arquivos do sistema. "
            "O diretório atual do usuário será passado para você conforme ele navega pelo sistema. "
            "Quando receber 'cmd: <comando>', execute no shell e interprete a saída como um especialista faria. "
            "Use tags como [cmd], [resposta], [resumo], [erro], [leitura], [atalho] para organização."
        )
    }

# === FUNÇÃO SEGURA PARA JSON EM RESPOSTAS STREAMED ===
def safe_json_response(text):
    try:
        lines = text.strip().splitlines()
        for line in lines:
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    except Exception as e:
        print(f"[erro] Falha ao interpretar resposta JSON: {e}")
    return {}

# === UTILITÁRIOS ===
def listar_modelos():
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags")
        response.raise_for_status()
        return [model["name"] for model in response.json().get("models", [])]
    except Exception as e:
        print(f"[erro] Erro ao buscar modelos: {e}")
        exit()

def escolher_modelo(modelos):
    for idx, nome in enumerate(modelos, 1):
        print(f"[{idx}] {nome}")
    while True:
        try:
            idx = int(input("\nDigite o número do modelo: ")) - 1
            if 0 <= idx < len(modelos):
                return modelos[idx]
        except ValueError:
            pass
        print("[erro] Entrada inválida.")

def salvar_arquivo():
    caminho = input("\n[tag: salvar] Caminho completo do arquivo: ").strip()
    conteudo = input("Conteúdo do arquivo: ").strip()
    try:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"[resposta] Arquivo salvo em: {caminho}")
    except Exception as e:
        print(f"[erro] Falha ao salvar: {e}")

def salvar_historico(messages, modelo):
    base = f"chat_{modelo}_{datetime.now().strftime('%Y-%m-%d')}"
    n = 1
    while os.path.exists(f"{HISTORICO_PATH}/{base}_{n}.json"):
        n += 1
    nome_arquivo = f"{HISTORICO_PATH}/{base}_{n}.json"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    print(f"[resposta] Histórico salvo em {nome_arquivo}")

def resumir_conversa(messages, modelo):
    prompt = [carregar_personalidade()] + messages[-LIMITE_MENSAGENS:] + [{"role": "user", "content": "Resuma nossa conversa em 3 frases."}]
    try:
        response = requests.post(f"{OLLAMA_HOST}/api/chat", json={"model": modelo, "messages": prompt}, stream=False)
        resposta_json = safe_json_response(response.text)
        content = resposta_json.get("message", {}).get("content", "")
        print(f"\n[resumo]\n{content.strip()}")
        return [{"role": "system", "content": f"Resumo da conversa: {content.strip()}"}]
    except Exception as e:
        print(f"[erro] Erro ao resumir: {e}")
        return [carregar_personalidade()]

def interpretar_comando_personalizado(comando):
    if comando.startswith("nano ") or comando.startswith("cat "):
        arquivo = comando.split(" ", 1)[-1]
        try:
            with open(os.path.join(estado_shell["cwd"], arquivo), 'r', encoding='utf-8') as f:
                return f"[atalho] Conteúdo do arquivo {arquivo}:\n\n" + f.read()
        except Exception as e:
            return f"[erro] Não foi possível abrir {arquivo}: {e}"
    return None

def executar_comando(comando):
    atalho = interpretar_comando_personalizado(comando)
    if atalho:
        return atalho

    # Simula cd/pwd para controle de estado
    global estado_shell
    if comando.startswith("cd "):
        destino = comando[3:].strip()
        novo_path = os.path.abspath(os.path.join(estado_shell["cwd"], destino))
        if os.path.isdir(novo_path):
            estado_shell["cwd"] = novo_path
            return f"[cmd] cd para {novo_path}"
        else:
            return f"[erro] Pasta não encontrada: {novo_path}"

    if comando.strip() == "pwd":
        return estado_shell["cwd"]

    try:
        output = subprocess.check_output(
            comando, shell=True, stderr=subprocess.STDOUT, text=True, cwd=estado_shell["cwd"]
        )
        if comando.startswith("ls"):
            return output + "\n[explicacao] Saída do ls: arquivos listados com permissões, tamanho, data de modificação, etc."
        return output
    except subprocess.CalledProcessError as e:
        return f"[erro ao executar]: {e.output}"

def comandos_internos(user_input):
    comandos = {
        "!ajuda": (
            "[comandos internos]\n"
            "- cmd: <comando> — executa comandos no terminal\n"
            "- ler: <arquivo> — lê conteúdo de arquivos\n"
            "- salvar — cria um arquivo\n"
            "- resumir — resume a conversa atual\n"
            "- !tarefa: <ação> — executa uma tarefa interpretada pela IA\n"
            "- !ajuda — mostra este menu"
        )
    }
    return comandos.get(user_input.strip(), None)

def interpretar_tarefa(user_input, modelo, messages):
    tarefa = user_input.replace("!tarefa:", "").strip()
    prompt = [carregar_personalidade()] + messages[-LIMITE_MENSAGENS:] + [
        {"role": "user", "content": f"Diretório atual do usuário: {estado_shell['cwd']}\nTarefa solicitada: {tarefa}\nExplique e indique quais comandos devo rodar para resolver."}
    ]
    try:
        response = requests.post(f"{OLLAMA_HOST}/api/chat", json={"model": modelo, "messages": prompt}, stream=False)
        content = response.json().get("message", {}).get("content", "")
        print(f"\n[tarefa interpretada]\n{content.strip()}")
        return content
    except Exception as e:
        print(f"[erro] Falha ao interpretar tarefa: {e}")
        return "[erro] Tarefa não interpretada."

def chat_loop(modelo):
    print(f"\nIniciando com o modelo: {modelo}\nDigite 'sair' para encerrar.")
    messages = [carregar_personalidade()]

    while True:
        user_input = input("\nVocê: ").strip()

        if user_input.lower() in ["sair", "exit"]:
            salvar_historico(messages, modelo)
            break
        elif user_input.lower() == "salvar":
            salvar_arquivo()
            continue
        elif user_input.lower() in ["resumir", "limpar"]:
            messages = resumir_conversa(messages, modelo)
            continue

        resposta_comando = comandos_internos(user_input)
        if resposta_comando:
            print(resposta_comando)
            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": resposta_comando})
            continue

        if user_input.startswith("cmd:"):
            comando = user_input[4:].strip()
            resultado = executar_comando(comando)
            print(f"\n[cmd]: {comando}\n[resposta]:\n{resultado}")
            messages.append({"role": "user", "content": f"cmd: {comando}"})
            messages.append({"role": "assistant", "content": f"[cmd] {comando}\n[resposta]\n{resultado}"})
        elif user_input.startswith("ler:"):
            caminho = user_input[4:].strip()
            conteudo = ler_arquivo(caminho)
            print(f"\n[leitura do arquivo]\n{conteudo}")
            messages.append({"role": "user", "content": f"ler: {caminho}"})
            messages.append({"role": "assistant", "content": f"[leitura]\n{conteudo}"})
        elif user_input.startswith("!tarefa:"):
            interpretada = interpretar_tarefa(user_input, modelo, messages)
            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": interpretada})
        else:
            messages.append({"role": "user", "content": user_input})

            # Atualiza a IA com o caminho atual do sistema
            messages.append({
                "role": "system",
                "content": f"O diretório atual do usuário é: {estado_shell['cwd']}."
            })

            try:
                response = requests.post(f"{OLLAMA_HOST}/api/chat", json={"model": modelo, "messages": messages, "stream": True}, stream=True)
                print("[assistente]: ", end="", flush=True)
                full_content = ""
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode('utf-8').replace("data: ", ""))
                        content = chunk.get("message", {}).get("content", "")
                        print(content, end="", flush=True)
                        full_content += content
                messages.append({"role": "assistant", "content": full_content})
            except Exception as e:
                print(f"[erro] Erro na requisição: {e}")

        if len(messages) > LIMITE_MENSAGENS * 2:
            print("\n[alerta] Histórico longo. Use 'resumir' para otimizar o contexto.")

if __name__ == "__main__":
    modelos = listar_modelos()
    escolhido = escolher_modelo(modelos)
    chat_loop(escolhido)
