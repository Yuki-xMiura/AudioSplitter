import os
import time
import mimetypes
from dotenv import load_dotenv
from google import genai
import json
import re

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
    
    # 1. Identifica a extensão do arquivo
    ext = os.path.splitext(audio_path)[1].lower()
    
    # 2. Obtém o MIME type do dicionário ou usa a detecção do sistema operacional
    mime_type = AUDIO_MIME_MAP.get(ext) or mimetypes.guess_type(audio_path)[0]
    
    # Se ainda assim não encontrar, deixa o Gemini tentar inferir
    upload_kwargs = {"file": audio_path}
    if mime_type:
        upload_kwargs["config"] = {"mime_type": mime_type}
        print(f"Format detectado: {mime_type}")

    # Envia o arquivo
    audio_file = client.files.upload(**upload_kwargs)
    print(f"Arquivo enviado com ID: {audio_file.name}. Aguardando processamento...")

    # Loop de verificação (Polling)
    while audio_file.state.name == "PROCESSING":
        print(".", end="", flush=True)
        time.sleep(2)
        audio_file = client.files.get(name=audio_file.name)

    # Se o Gemini recusar o arquivo, mostra o erro retornado
    if audio_file.state.name == "FAILED":
        error_details = getattr(audio_file, "error", "Nenhum detalhe retornado pela API")
        print(f"\n❌ Erro detalhado da File API: {error_details}")
        raise ValueError(f"O processamento do arquivo falhou. Estado atual: {audio_file.state.name}")

    print("\nÁudio pronto e processado! Solicitando análise de tópicos ao Gemini...")

    prompt = f"""
    Analise o áudio a seguir e divida-o em capítulos lógicos com base nos tópicos abordados.
    Cada capítulo deve ter no mínimo {min_minutes} minutos e no máximo {max_minutes} minutos.
    Retorne estritamente um JSON no seguinte formato:
    [
        {{
            "title": "Nome do Capítulo",
            "start_time": "MM:SS",
            "end_time": "MM:SS"
        }}
    ]
    """

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=[audio_file, prompt]
    )
    

    # Remove blocos de código ```json ... ``` se o Gemini incluir
    raw_text = response.text.strip()
    clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text, flags=re.MULTILINE)
    
    # Converte a string limpa em uma estrutura de dados Python (list de dicts)
    return json.loads(clean_json)