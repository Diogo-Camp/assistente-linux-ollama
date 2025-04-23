import requests
import time

class ChatbotClient:
    def __init__(self, base_url="http://192.168.0.36:5000"):
        self.base_url = base_url
        self.conversation_id = None
    
    def start_conversation(self, title="Nova Conversa"):
        response = requests.post(
            f"{self.base_url}/api/start",
            json={'title': title}
        )
        self.conversation_id = response.json()['conversation_id']
        print(f"Conversa iniciada: {self.conversation_id}")
    
    def send_message(self, message):
        if not self.conversation_id:
            self.start_conversation()
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                'conversation_id': self.conversation_id,
                'message': message
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nAssistente: {data['response']}")
            print(f"(Modelo: {data['metadata']['model']}, Tokens: {data['metadata']['tokens_used']})")
        else:
            print(f"Erro: {response.text}")

def main():
    client = ChatbotClient()
    
    # Testa conexão
    try:
        health = requests.get(f"{client.base_url}/api/health", timeout=2)
        print(f"Conectado ao servidor: {health.json()}")
    except:
        print("Não foi possível conectar ao servidor. Verifique se está rodando.")
        return
    
    client.start_conversation()
    
    while True:
        try:
            message = input("\nVocê: ")
            if message.lower() in ['sair', 'exit', 'quit']:
                break
            client.send_message(message)
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break

if __name__ == "__main__":
    main()