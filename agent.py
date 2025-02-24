import json
import os
import requests
import importlib.util

# Inicialmente essa função inicia o processo do arquivo k8s.py que é responsável por extrair os endpoints da API e deixa ele no estado de execução durante a execução do código principal, para que possamos acessar os endpoints da API do AKS, logo após a execução do codigo principal, o arquivo k8s.py é finalizado.


# Define os prompts

ENDPOINT = "https://ai-ricardolima3473ai595268058602.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
API_KEY="6CDfkgnJBT5KU9VggwZEk29wX14X5auOgE76Jc2FP5wMgIa39u8lJQQJ99BBACHYHv6XJ3w3AAAAACOGXxyB"

# Carrega dinamicamente o módulo k8s.py para extrair os endpoints da API
def get_k8s_endpoints():
    k8s_path = os.path.join(os.path.dirname(__file__), 'discovery', 'k8s.py') # Caminho do módulo k8s.py
    spec = importlib.util.spec_from_file_location("k8s", k8s_path) # Especifica o local do módulo k8s.py
    k8s_module = importlib.util.module_from_spec(spec) # Carrega o módulo k8s.py a partir do caminho especificado
    spec.loader.exec_module(k8s_module) # Executa o módulo k8s.py para que as rotas sejam registradas
    # Extrai apenas as rotas que começam com /api/
    endpoints = [rule.rule for rule in k8s_module.app.url_map.iter_rules() if rule.rule.startswith('/api/')] # Lista de endpoints da API do AKS (rotas)
    return endpoints # Retorna a lista de endpoints da API do AKS

def fetch_k8s_data(): # Função para buscar os dados de todos os endpoints 
    base_url = "http://127.0.0.1:5000" # URL base da API do AKS
    endpoints = get_k8s_endpoints()  # Consulta os endpoints dinamicamente
    k8s_data = {} # Dicionário para armazenar os dados de cada endpoint da API do AKS
    os.makedirs("data", exist_ok=True) # Cria o diretório data se ele não existir

    for endpoint in endpoints: # Itera sobre cada endpoint da API do AKS
        url = f"{base_url}{endpoint}" # URL completa do endpoint atual
        try:
            response = requests.get(url) # Faz uma requisição GET para o endpoint atual da API do AKS
            response.raise_for_status() # Verifica se a requisição foi bem-sucedida (status code 200)
            k8s_data[endpoint] = response.json() # Armazena os dados do endpoint atual no dicionário k8s_data
            # Cria um arquivo JSON com os dados do endpoint atual para fins de depuração
            with open(f"data/{endpoint.replace('/', '_')}.json", 'w') as f:
                json.dump(k8s_data[endpoint], f, indent=2)
        except requests.exceptions.HTTPError as http_err: # Trata erros de HTTP
            msg = f"HTTP error: {http_err}"
            print(f"HTTP error occurred while fetching data from {endpoint}: {http_err}")
            k8s_data[endpoint] = {"error": msg}
        except requests.exceptions.ConnectionError as conn_err:
            msg = f"Connection error: {conn_err}"
            print(f"Connection error occurred while fetching data from {endpoint}: {conn_err}")
            k8s_data[endpoint] = {"error": msg}
        except requests.exceptions.Timeout as timeout_err:
            msg = f"Timeout error: {timeout_err}"
            print(f"Timeout error occurred while fetching data from {endpoint}: {timeout_err}")
            k8s_data[endpoint] = {"error": msg}
        except requests.exceptions.RequestException as req_err:
            msg = f"Request error: {req_err}"
            print(f"An error occurred while fetching data from {endpoint}: {req_err}")
            k8s_data[endpoint] = {"error": msg} # Armazena a mensagem de erro no dicionário k8s_data
        except requests.HTTPError as http_err: # Trata erros de HTTP
            msg = f"HTTP error: {http_err}" # Mensagem de erro
            print(f"HTTP error occurred while fetching data from {endpoint}: {http_err}")
            k8s_data[endpoint] = {"error": msg} # Armazena a mensagem de erro no dicionário k8s_data
        except requests.ConnectionError as conn_err: # Trata erros de conexão
            msg = f"Connection error: {conn_err}" # Mensagem de erro
            print(f"Connection error occurred while fetching data from {endpoint}: {conn_err}") # Imprime a mensagem de erro
            k8s_data[endpoint] = {"error": msg} # Armazena a mensagem de erro no dicionário k8s_data
        except requests.Timeout as timeout_err: # Trata erros de timeout
            msg = f"Timeout error: {timeout_err}" # Mensagem de erro de timeout
            print(f"Timeout error occurred while fetching data from {endpoint}: {timeout_err}") # Imprime a mensagem de erro de timeout
            k8s_data[endpoint] = {"error": msg} # Armazena a mensagem de erro no dicionário k8s_data
        except requests.RequestException as req_err: # Trata erros de requisição em geral
            msg = f"Request error: {req_err}" # Mensagem de erro de requisição em geral
            print(f"An error occurred while fetching data from {endpoint}: {req_err}") # Imprime a mensagem de erro de requisição em geral
            k8s_data[endpoint] = {"error": msg} # Armazena a mensagem de erro no dicionário k8s_data
  
    return k8s_data

def send_prompt(payload): # Função para enviar um prompt para o modelo GPT-4 OpenAI ou outro modelo
    headers = { # Cabeçalhos da requisição HTTP
        "Content-Type": "application/json", # Tipo de conteúdo da requisição
        "api-key": API_KEY, # Chave da API para autenticação
    } # Cabeçalhos da requisição HTTP para enviar um prompt ao modelo GPT-4 OpenAI ou outro modelo
    try: # Tenta fazer a requisição HTTP POST
        response = requests.post(ENDPOINT, headers=headers, json=payload) # Faz uma requisição POST para o endpoint do modelo GPT-4 OpenAI ou outro modelo com o payload especificado
        response.raise_for_status() # Verifica se a requisição foi bem-sucedida (status code 200) ou lança uma exceção HTTPError se não for bem-sucedida
        return response.json()
    except requests.RequestException as e: # Trata erros de requisição em geral (RequestException)
        # Retorna o erro sem interromper o fluxo
        return {"error": f"Failed to make the request. Error: {e}"}

def generate_insights(contentaks, prompts, systemprompt): # Função para gerar insights com base nos dados do cluster AKS e nos prompts definidos
    insights = [] # Lista para armazenar os insights gerados com base nos prompts e nos dados do cluster AKS
    os.makedirs("insights", exist_ok=True) # Cria o diretório insights se ele não existir
    for i, prompt in enumerate(prompts): # Itera sobre cada prompt definido para gerar insights com base nos dados do cluster AKS
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": systemprompt
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nInformações do cluster: {json.dumps(contentaks, indent=2)}"
                }
            ],
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": 8000
        }

        data = send_prompt(payload)
        # Se houver um erro na resposta, armazena a mensagem de erro
        if "error" in data:
            error_msg = data["error"]
            print(f"Failed to send prompt: {error_msg}")
            insights.append(f"Error: {error_msg}")
        else:
            try:
                message_content = data["choices"][0]["message"]["content"]
                insights.append(message_content)
                contentaks = message_content  # Usa a resposta como entrada para o próximo prompt
                with open(f"insights/insight_{i+1}.md", 'w') as f: # Cria um arquivo .md para cada insight gerado
                    f.write(f"# Insight {i+1}\n\n") # Escreve o título do insight no arquivo .md
                    f.write(f"## Prompt\n\n{prompt}\n\n") # Escreve o prompt no arquivo .md
                    f.write(f"## Resposta\n\n{message_content}\n\n")
            except (KeyError, IndexError) as parse_err: # Trata erros de análise da resposta JSON
                error_msg = f"Erro ao interpretar a resposta: {parse_err}" # Mensagem de erro
                print(error_msg)
                insights.append(f"Error: {error_msg}")

    return insights

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"An error occurred while reading the file: {e}"

# Busca os dados de todos os endpoints
contentaks = fetch_k8s_data()

# Define os caminhos dos prompts
USER_PROMPT_PATH = os.path.join(os.path.dirname(__file__), 'prompts/user_config', 'user_agent.pro')
SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), 'prompts/system_config', 'system.pro')


# Lê os conteúdos dos prompts
user_prompt_content = read_file_content(USER_PROMPT_PATH)
system_prompt_content = read_file_content(SYSTEM_PROMPT_PATH)

# Define os prompts
prompts = user_prompt_content.split('\n') # Separa os prompts por quebra de linha e armazena em uma lista

# Gera os insights
insights = generate_insights(contentaks, prompts, system_prompt_content)

# Imprime os insights
for i, insight in enumerate(insights):
    print(f"Insight {i+1}: {insight}")
