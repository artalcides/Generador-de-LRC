from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import whisper
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'clave-segura'

UPLOAD_FOLDER = 'uploads'
TRANSCRIPTS_FOLDER = 'transcripts'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPTS_FOLDER, exist_ok=True)

history = []

def segundos_a_timestamp(segundos):
    minutos = int(segundos // 60)
    seg = int(segundos % 60)
    cent = int((segundos % 1) * 100)
    return f"[{minutos:02d}:{seg:02d}.{cent:02d}]"

@app.route('/', methods=['GET', 'POST'])
def index():
    global history
    if request.method == 'POST':
        file = request.files.get('audio')
        if not file:
            flash("No se ha seleccionado ningún archivo.")
            return redirect(request.url)

        try:
            filename = secure_filename(file.filename)
            if not filename:
                flash("Nombre de archivo no válido.")
                return redirect(request.url)

            audio_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(audio_path)

            model = whisper.load_model("base")
            result = model.transcribe(audio_path)

            if "segments" not in result or not result["segments"]:
                flash("No se pudo transcribir el audio.")
                return redirect(request.url)

            titulo = os.path.splitext(filename)[0]
            artista = "Desconocido"
            lrc_filename = f"{titulo}.lrc"
            lrc_path = os.path.join(TRANSCRIPTS_FOLDER, lrc_filename)

            lrc_lines = [f"[ti:{titulo}]
[ar:{artista}]
"]
            for segmento in result["segments"]:
                timestamp = segundos_a_timestamp(segmento["start"])
                texto = segmento["text"].strip()
                lrc_lines.append(f"{timestamp}{texto}")

            with open(lrc_path, "w", encoding="utf-8") as f:
                f.write("
".join(lrc_lines))

            history.insert(0, {
                "titulo": titulo,
                "filename": lrc_filename,
                "contenido": "
".join(lrc_lines)
            })

            flash("Archivo procesado correctamente.")
            return redirect(url_for('index'))

        except Exception as e:
            flash(f"Ocurrió un error: {str(e)}")
            return redirect(request.url)

    return render_template("index.html", history=history)

@app.route('/descargar/<filename>')
def descargar(filename):
    path = os.path.join(TRANSCRIPTS_FOLDER, filename)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
