from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid, os
from processors.alcoa_processor import process_alcoa_pdf

app = Flask(__name__)

BASE = Path(__file__).parent.resolve()
UPLOAD_DIR = BASE / "uploads"
OUT_DIR = BASE / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)

ALLOWED_EXTS = {".pdf"}


# ---------- Pages ----------
@app.get("/")
def home():
    return render_template("index.html")

@app.get("/alcoa")
def alcoa_page():
    return render_template("alcoa.html")

@app.get("/extracted")
def extracted_page():
    # very lightweight page; the list is fetched via JS
    return render_template("extracted.html")

# ---------- API ----------
@app.post("/api/upload/alcoa")
def api_upload_alcoa():
    f = request.files.get("file")
    if not f or not f.filename:
        return jsonify(success=False, error="No file provided"), 400

    ext = Path(f.filename).suffix.lower()
    if ext not in ALLOWED_EXTS:
        return jsonify(success=False, error="PDF files only"), 400

    file_id = uuid.uuid4().hex[:12]
    safe_name = secure_filename(f.filename)
    pdf_path = UPLOAD_DIR / f"{file_id}_{safe_name}"
    f.save(pdf_path)

    try:
        # ✅ Call your parser EXACTLY as implemented: 1 arg, returns CSV path/filename
        csv_generated = process_alcoa_pdf(str(pdf_path))
        if not csv_generated:
            return jsonify(success=False, error="No valid data extracted"), 422

        # csv_generated may be a filename in the current working dir.
        # Move it into OUT_DIR with a name that starts with file_id so /download/<id> works.
        src = Path(csv_generated)
        if not src.is_absolute():
            src = Path.cwd() / src

        OUT_DIR.mkdir(exist_ok=True)
        dest = OUT_DIR / f"{file_id}_{src.name}"
        os.replace(src, dest)  # atomic move/rename

        return jsonify(
            success=True,
            file_id=file_id,
            filename=dest.name,
            csv=f"/download/{file_id}"   # your existing download route uses file_id
        )

    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.get("/api/list-files")
def api_list_files():
    files = []
    for p in OUT_DIR.glob("*.csv"):
        # Expect filename: <file_id>_something.csv  OR just source.pdf stem.csv
        fid = p.stem.split("_")[0]
        files.append({"file_id": fid, "filename": p.name})
    return jsonify(files=files)

@app.delete("/api/delete/<file_id>")
def api_delete(file_id):
    # remove csv and original pdf if present
    removed = False
    for p in list(OUT_DIR.glob(f"{file_id}_*.csv")) + list(OUT_DIR.glob(f"{file_id}.csv")):
        p.unlink(missing_ok=True)
        removed = True
    for p in UPLOAD_DIR.glob(f"{file_id}_*.pdf"):
        p.unlink(missing_ok=True)
    return jsonify(success=removed)

@app.get("/download/<file_id>")
def download(file_id):
    # Serve the csv whose name begins with file_id
    for p in OUT_DIR.glob(f"{file_id}_*.csv"):
        return send_file(p, as_attachment=True)
    # fallback: id.csv
    p = OUT_DIR / f"{file_id}.csv"
    if p.exists():
        return send_file(p, as_attachment=True)
    return "Not found", 404

if __name__ == "__main__":
    app.run(debug=True)