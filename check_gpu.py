import subprocess
import torch

def check_ollama_gpu():
    try:
        # Verifica se o Ollama está usando GPU
        result = subprocess.run(['ollama', 'ps'], capture_output=True, text=True)
        print("Processos Ollama:")
        print(result.stdout)
        
        # Verifica CUDA
        print("\nVerificação PyTorch:")
        print(f"CUDA disponível: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"Dispositivo atual: {torch.cuda.current_device()}")
            print(f"Nome GPU: {torch.cuda.get_device_name(0)}")
        
        # Verifica variáveis de ambiente
        print("\nVariáveis de ambiente relevantes:")
        print(f"CUDA_VISIBLE_DEVICES: {os.environ.get('CUDA_VISIBLE_DEVICES', 'Não definido')}")
        print(f"OLLAMA_NO_CUDA: {os.environ.get('OLLAMA_NO_CUDA', 'Não definido')}")
        
    except Exception as e:
        print(f"Erro na verificação: {e}")

if __name__ == "__main__":
    check_ollama_gpu()
