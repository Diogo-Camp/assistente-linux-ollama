import requests

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
headers = {
    "Authorization": f"Bearer {'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'}"
}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

resultado = query({
    "inputs": "Me diga como posso ganhar dinheiro online de forma inteligente. fale em portugues do brasil por favor.",
    "parameters": {
        "temperature": 0.7,
        "max_new_tokens": 150
    }
})

print(resultado)
