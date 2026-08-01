# Audiobook AI Segmenter & Splitter

Ferramenta em linha de comando (CLI) escrita em Python para segmentação temática e fatiamento automático de arquivos de áudio e audiobooks. 

O projeto utiliza a API do **Google Gemini** para escutar o áudio, identificar mudanças de tópicos e gerar marcações de tempo (timestamps) com títulos. Em seguida, fatiamos o áudio original em capítulos menores no formato MP3 com **tags ID3** embutidas (título, número da faixa e álbum).

---

## Funcionalidades

- **Análise Inteligente por IA:** Transcrição e identificação temática de tópicos a cada intervalo configurável (padrão: 5 minutos).
- **Tags ID3 Nativas:** Injeção de metadados de mídia em cada capítulo gerado para exibição do título em qualquer player de áudio/carro.
- **Structured Output JSON:** Comunicação precisa e sem ambiguidades com a API do Gemini.
- **Autolimpeza:** Remoção automática do arquivo temporário enviado para a API após o processamento.
- **Suporte Multiformato:** Aceita MP3, M4A, WAV, FLAC e AAC através do FFmpeg.

---

## Estrutura do Repositório

```text
audiobook-ai-segmenter/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── main.py
└── src/
    ├── __init__.py
    ├── gemini_analyzer.py
    └── audio_splitter.py