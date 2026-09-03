import os
import time
import mimetypes
import json
import re
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Mapeamento manual para garantir extensões comuns de áudio que o OS possa não reconhecer por padrão
AUDIO_MIME_MAP = {
    ".mp3": "audio/mp3",
    ".mpeg": "audio/mpeg",
    ".mp4": "audio/mp4",
    ".m4a": "audio/m4a",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    ".aac": "audio/aac"
}

def analyze_audio(audio_path: str, min_minutes: int = 3, max_minutes: int = 10):
    print(f"Uploading '{audio_path}' para o Gemini File API...")
    
    ext = os.path.splitext(audio_path)[1].lower()
    mime_type = AUDIO_MIME_MAP.get(ext) or mimetypes.guess_type(audio_path)[0]
    
    # 1. Cria um nome seguro para os cabeçalhos HTTP (sem acentos nem caracteres especiais)
    safe_display_name = re.sub(r'[^\w\s-]', '', os.path.basename(audio_path)).encode('ascii', 'ignore').decode('ascii')
    if not safe_display_name.strip():
        safe_display_name = "audiobook_input"

    # 2. Prepara as configurações de upload
    upload_config = {"display_name": safe_display_name}
    if mime_type:
        upload_config["mime_type"] = mime_type
        print(f"Formato detectado: {mime_type}")

    # 3. Envia o arquivo com a config tratada
    audio_file = client.files.upload(file=audio_path, config=upload_config)
    print(f"Arquivo enviado com ID: {audio_file.name}. Aguardando processamento...")

    # Loop de verificação (Polling)
    while audio_file.state.name == "PROCESSING":
        print(".", end="", flush=True)
        time.sleep(3)
        audio_file = client.files.get(name=audio_file.name)

    if audio_file.state.name == "FAILED":
        error_details = getattr(audio_file, "error", "Nenhum detalhe retornado pela API")
        print(f"\n❌ Erro detalhado da File API: {error_details}")
        raise ValueError(f"O processamento do arquivo falhou. Estado atual: {audio_file.state.name}")

    print("\nÁudio pronto e processado! Solicitando análise de tópicos ao Gemini...")

    prompt = f"""
    Analise o áudio enviado e realize duas tarefas:
    1. Identifique os capítulos lógicos do áudio com base no assunto tratado.
    2. Monte a lista de timestamps no padrão aceito pelo YouTube.
    

    Diretrizes de tempo:
    - O primeiro capítulo DEVE começar obrigatoriamente em "00:00".
    - Priorize o encerramento natural dos pensamentos (recomenda-se entre {min_minutes} e {max_minutes} minutos por capítulo, mas flexibilize se a troca de assunto exigir).

    Retorne estritamente um JSON no seguinte formato:
    {{
        "chapters": [
            {{
                "title": "Título do Capítulo",
                "start_time": "MM:SS",
                "end_time": "MM:SS"
            }}
        ],
        "youtube_description": "00:00 Título do Capítulo 1\\n04:15 Título do Capítulo 2"
    }}
    """
    # Tenta obter a resposta com até 3 re-tentativas em caso de oscilação do servidor (HTTP 503)
    max_retries = 3
    models_to_try = ["gemini-2.5-flash", "gemini-3.1-flash-lite", "gemini-flash-latest"]
    
    for attempt in range(max_retries):
        model_name = models_to_try[attempt % len(models_to_try)]
        try:
            print(f"Tentativa {attempt + 1}: Solicitando ao modelo {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=[audio_file, prompt]
            )
            
            raw_text = response.text.strip()
            clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text, flags=re.MULTILINE)
            return json.loads(clean_json)

        except errors.APIError as e:
            print(f"⚠️ Instabilidade na API do Google (Erro: {e}). Aguardando 5 segundos...")
            if attempt == max_retries - 1:
                raise e
            time.sleep(5)
        except Exception as e:
            print(f"⚠️ Erro inesperado: {e}")
            raise e
    
    raw_text = response.text.strip()
    clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text, flags=re.MULTILINE)
    
    return json.loads(clean_json)



"""
    Analise o áudio enviado e realize duas tarefas:
    1. Identifique os capítulos lógicos do áudio com base no assunto tratado.
    2. Monte a lista de timestamps no padrão aceito pelo YouTube.
    3. Faça a transcrição completa do texto falado, organizada por capítulos com timestamps.

    Diretrizes de tempo:
    - O primeiro capítulo DEVE começar obrigatoriamente em "00:00".
    - Priorize o encerramento natural dos pensamentos (recomenda-se entre {min_minutes} e {max_minutes} minutos por capítulo, mas flexibilize se a troca de assunto exigir).

    Retorne estritamente um JSON no seguinte formato:
    {{
        "chapters": [
            {{
                "title": "Título do Capítulo",
                "start_time": "MM:SS",
                "end_time": "MM:SS"
            }}
        ],
        "youtube_description": "00:00 Título do Capítulo 1\\n04:15 Título do Capítulo 2",
        "full_transcript": "[00:00] - Título do Capítulo 1\\nTexto transcrito aqui...\\n\\n[04:15] - Título do Capítulo 2\\nTexto transcrito aqui..."
    }}
    """