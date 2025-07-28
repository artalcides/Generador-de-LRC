from flask import Flask, render_template, request, send_file, redirect, url_for
import whisper
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
TRANSCRIPTS_FOLDER = 'transcripts'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPTS_FOLDER, exist_ok=True)

history_file = 'transcripts/history.txt'
history = []

if os.path.exists(history_file):
    with open(history_file, 'r', encoding='utf-8') as f:
        for line in f:
            titulo, filename = line.strip().split('|')
            path = os.path.join(TRANSCRIPTS_FOLDER, filename)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as lf:
                    contenido = lf.read()
                    history.append({'titulo': titulo, 'filename': filename, 'contenido': contenido})

def segundos_a_timestamp(segundos):
    minutos = int(segundos // 60)
    seg = int(segundos % 60)
    cent = int((segundos % 1) * 100)
    return f"[{minutos:02d}:{seg:02d}.{cent:02d}]"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('audio')
        letra_manual = request.form.get('letra')
        if file:
            filename = secure_filename(file.filename)
            audio_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(audio_path)

            model = whisper.load_model("base")
            result = model.transcribe(audio_path)

            titulo = os.path.splitext(filename)[0]
            artista = "Desconocido"
            lrc_filename = f"{titulo}.lrc"
            lrc_path = os.path.join(TRANSCRIPTS_FOLDER, lrc_filename)

            with open(lrc_path, "w", encoding="utf-8") as f:
                f.write(f"[ti:{titulo}]
[ar:{artista}]
")
                if letra_manual.strip():
                    bloques = letra_manual.strip().split('\n\n')
                    for i, bloque in enumerate(bloques):
                        if i < len(result["segments"]):
                            timestamp = segundos_a_timestamp(result["segments"][i]["start"])
                            f.write(f"{timestamp}{bloque.replace('\n', ' ')}
")
                else:
                    for segmento in result["segments"]:
                        timestamp = segundos_a_timestamp(segmento["start"])
                        texto = segmento["text"].strip()
                        f.write(f"{timestamp}{texto}
")

            with open(history_file, 'a', encoding='utf-8') as hf:
                hf.write(f"{titulo}|{lrc_filename}
")

            with open(lrc_path, 'r', encoding='utf-8') as lf:
                contenido = lf.read()
                history.append({'titulo': titulo, 'filename': lrc_filename, 'contenido': contenido})

            return redirect(url_for('index'))

    return render_template("index.html", history=history)

@app.route('/descargar/<filename>')
def descargar(filename):
    path = os.path.join(TRANSCRIPTS_FOLDER, filename)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
