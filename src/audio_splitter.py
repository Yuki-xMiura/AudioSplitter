import os
from pydub import AudioSegment

def parse_time_to_ms(time_str: str) -> int:
    """Converte strings no formato MM:SS ou HH:MM:SS para milissegundos."""
    parts = list(map(int, time_str.split(':'))) #ou [int(p) for p in time_str.split(':')]
    if len(parts) == 2:
        minutes, seconds = parts
        return (minutes * 60 + seconds) * 1000
    elif len(parts) == 3:
        hours, minutes, seconds = parts
        return (hours * 3600 + minutes * 60 + seconds) * 1000
    return 0

def split_audio(file_path: str, segments: list[dict], output_dir: str = "output"):
    """Corta o áudio de acordo com os timestamps e injeta tags ID3."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"Carregando arquivo de áudio local: {file_path}")
    audio = AudioSegment.from_file(file_path)
    
    for idx, seg in enumerate(segments, start=1):
        start_ms = parse_time_to_ms(seg["inicio"])
        end_ms = parse_time_to_ms(seg["fim"])
        
        # Garante que o fim não ultrapasse a duração total do áudio
        end_ms = min(end_ms, len(audio))
        
        chunk = audio[start_ms:end_ms]
        title = seg["titulo"].strip()
        
        # Nome do arquivo limpo para evitar caracteres inválidos no sistema de arquivos
        safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')]).rstrip()
        filename = f"{idx:02d} - {safe_title}.mp3"
        output_path = os.path.join(output_dir, filename)
        
        # Exporta com os metadados ID3 embutidos no MP3
        chunk.export(
            output_path, 
            format="mp3", 
            tags={
                "title": f"{idx:02d}. {title}",
                "track": str(idx),
                "album": "Audiobook AI Chapters"
            }
        )
        print(f" Faixa gerada: {filename}")