# Generador de Letras LRC 🎵

Esta aplicación web utiliza el modelo `whisper` de OpenAI para transcribir archivos de audio y generar archivos `.lrc` sincronizados automáticamente.

## Cómo usar

1. Sube un archivo de audio `.mp3`, `.wav`, etc.
2. La app lo transcribe usando Whisper.
3. Descarga el archivo `.lrc` generado.

## Instalación local

```bash
pip install -r requirements.txt
python app.py
```

## Requisitos

- Python 3.10+
- ffmpeg instalado en el sistema
