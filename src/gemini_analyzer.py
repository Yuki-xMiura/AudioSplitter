import json
import os
from google import genai
from google.genai import types

def analyze_audio(file_path: str, max_minutes: int = 6, min_minutes: int = 3) -> list[dict]:
    """Sobe o áudio para o Gemini e retorna a lista de timestamps com títulos."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    print(f"Uploading '{file_path}' para o Gemini File API...")
    audio_file = client.files.upload(file=file_path)
    
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
        model="gemini-2.5-flash",
        contents=[audio_file, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    
    # Deleta o arquivo temporário da nuvem após o processamento
    client.files.delete(name=audio_file.name)
    
    return json.loads(response.text)