import argparse
import json
from dotenv import load_dotenv
from src.gemini_analyzer import analyze_audio
from src.audio_splitter import split_audio

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Segmente e fatie audiobooks com IA.")
    parser.add_argument("audio_path", type=str, help="Caminho do arquivo de áudio (MP3, M4A, etc.)")
    parser.add_argument("--min", type=int, default=3, help="Duração mínima de cada bloco em minutos (padrão: 3)")
    parser.add_argument("--max", type=int, default=6, help="Duração máxima de cada bloco em minutos (padrão: 6)")
    parser.add_argument("--out", type=str, default="capitulos", help="Pasta de saída para os MP3s")
    
    args = parser.parse_args()
    
    # 1. Obter divisões via Gemini
    chapters = analyze_audio(args.audio_path, min_minutes=args.min, max_minutes=args.max)
    print("\nCapítulos identificados:")
    print(json.dumps(chapters, indent=2, ensure_ascii=False))
    
    # 2. Cortar áudio localmente
    split_audio(args.audio_path, chapters, output_dir=args.out)
    print(f"\nConcluído! Todos os trechos foram salvos em: '{args.out}'")

if __name__ == "__main__":
    main()