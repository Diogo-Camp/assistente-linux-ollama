import ollama

def test_connection():
    try:
        print("Testando conexão com Ollama...")
        print("Versão do cliente Python:", ollama.__version__)
        
        print("\nListando modelos:")
        models = ollama.list()
        print(models)
        
        print("\nTestando chat:")
        response = ollama.chat(
            model='mistral',
            messages=[{'role': 'user', 'content': 'teste'}],
            stream=False
        )
        print("Resposta:", response)
        
    except Exception as e:
        print("ERRO:", str(e))
        raise

if __name__ == "__main__":
    test_connection()