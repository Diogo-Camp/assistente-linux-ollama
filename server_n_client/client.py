import requests
import json

class ChatClient:
    def __init__(self, base_url="http://192.168.0.36:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.conversation_id = None

    def send_message(self, message: str):
        try:
            data = {"message": message}
            if self.conversation_id:
                data["conversation_id"] = self.conversation_id
            
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=data,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            if not self.conversation_id and 'conversation_id' in result:
                self.conversation_id = result['conversation_id']
            
            return result
        
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            if hasattr(e, 'response') and e.response:
                print(f"Resposta do servidor: {e.response.text}")
            return None

def main():
    client = ChatClient()
    
    # Teste de conexão
    try:
        health = requests.get(f"{client.base_url}/api/health", timeout=2)
        print(f"Conectado ao servidor: {health.json()}")
    except:
        print("Não foi possível conectar ao servidor")
        return
    
    while True:
        try:
            message = input("\nVocê: ")
            if message.lower() in ['sair', 'exit', 'quit']:
                break
            
            result = client.send_message(message)
            if result:
                print(f"\nAssistente: {result.get('response')}")
                print(f"ID da Conversa: {result.get('conversation_id')}")
            else:
                print("Não foi possível obter resposta")
        
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break

if __name__ == "__main__":
    main()