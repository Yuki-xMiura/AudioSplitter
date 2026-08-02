import json
import os
import time
from google import genai
from google.genai import types

def analyze_audio(file_path: str, max_minutes: int = 6, min_minutes: int = 3) -> list[dict]:
    """Sobe o áudio para o Gemini e retorna a lista de timestamps com títulos."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    print(f"Uploading '{file_path}' para o Gemini File API...")
    audio_file = client.files.upload(file=file_path)

# Define o mime_type correto para áudio MP3/MPEG
    # Para arquivos de áudio .mp3 ou .mpeg, use 'audio/mp3' ou 'audio/mpeg'
    mime_type = "audio/mp3" if audio_path.lower().endswith((".mp3", ".mpeg")) else None

    # Upload especificando o tipo MIME explícito
    if mime_type:
        audio_file = client.files.upload(file=audio_path, config={"mime_type": mime_type})
    else:
        audio_file = client.files.upload(file=audio_path)

    print(f"Arquivo enviado com ID: {audio_file.name}. Aguardando processamento...")

    while audio_file.state.name == "PROCESSING":
        print(".", end="", flush=True)
        time.sleep(2)
        # Atualiza o status do arquivo na API
        audio_file = client.files.get(name=audio_file.name)

    if audio_file.state.name == "FAILED":
        raise ValueError("O processamento do arquivo de áudio falhou no Gemini File API.")

    print("\nÁudio pronto! Processando análise de tópicos com Gemini...")
    
    prompt = f"""
    Analise este arquivo de áudio e divida-o em blocos entre aproximadamente {min_minutes} e {max_minutes} minutos.
    Para cada bloco, identifique o tempo de início, tempo de fim e crie um título curto e descritivo do assunto.

    Retorne estritamente no seguinte formato JSON:
    [
      {{"inicio": "00:00", "fim": "05:00", "titulo": "Introdução ao Assunto"}},
      {{"inicio": "05:00", "fim": "10:15", "titulo": "Desenvolvimento do Conceito"}}
    ]
    """
    
    print("Processando análise de tópicos com Gemini...")
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=[audio_file, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    
    # Deleta o arquivo temporário da nuvem após o processamento
    client.files.delete(name=audio_file.name)
    
    return json.loads(response.text)