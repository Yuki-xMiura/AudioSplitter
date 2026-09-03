import argparse
import os
import json
from dotenv import load_dotenv
from src.gemini_analyzer import analyze_audio
from src.audio_splitter import split_audio

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Segmente e fatie audiobooks com IA.")
    parser.add_argument("audio_path", type=str, help="Caminho do arquivo de áudio (MP3, M4A, etc.)")
    parser.add_argument("--min", type=int, default=1, help="Duração mínima de cada bloco em minutos (padrão: 10)")
    parser.add_argument("--max", type=int, default=10, help="Duração máxima de cada bloco em minutos (padrão: 10)")
    parser.add_argument("--out", type=str, default="capitulos", help="Pasta de saída para os MP3s")
    
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    
# 1. Faz a análise completa no Gemini
    analysis_result = analyze_audio(args.audio_path, min_minutes=args.min, max_minutes=args.max)
    
    chapters = analysis_result.get("chapters", [])
    youtube_desc = analysis_result.get("youtube_description", "")
    full_transcript = analysis_result.get("full_transcript", "")
    
    # 2. Salva os arquivos de texto TXT
    yt_file_path = os.path.join(args.out, "descricao_youtube.txt")
    with open(yt_file_path, "w", encoding="utf-8") as f:
        f.write(youtube_desc)
        
    # transcript_file_path = os.path.join(args.out, "transcricao_completa.txt")
    # with open(transcript_file_path, "w", encoding="utf-8") as f:
    #     f.write(full_transcript)
        
    print(f"\n📄 Descrição para YouTube salva em: {yt_file_path}")
    #print(f"📄 Transcrição completa salva em: {transcript_file_path}")
    
    # 3. Corta o áudio em faixas separadas normalmente usando a lista de capítulos
    print("\nIniciando o fatiamento físico do áudio...")
   0 split_audio(args.audio_path, chapters, output_dir=args.out)

if __name__ == "__main__":
    main()