import os
import io
import csv
import requests

from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
from werkzeug.utils import secure_filename

from nlp_utils import (
    extract_text_from_pdf,
    extract_text_from_txt,
    extract_clauses
)

# ─── CONFIG ────────────────────────────────────────────────────────────────────
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "txt"}

#  API key from Google AI Studio
GEMINI_API_KEY = "Secret-ADK0017"

app = Flask(__name__)
app.secret_key = "ADK0017"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            return redirect(url_for("extract", filename=filename))
        else:
            flash("Only .pdf and .txt files are allowed.")
            return redirect(request.url)
    return render_template("upload.html")


@app.route("/extract/<filename>")
def extract(filename):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file_ext = filename.rsplit(".", 1)[1].lower()

    try:
        if file_ext == "pdf":
            raw_text = extract_text_from_pdf(filepath)
        else:
            raw_text = extract_text_from_txt(filepath)
    except RuntimeError as e:
        flash(str(e))
        return redirect(url_for("upload_file"))

    clauses = extract_clauses(raw_text)
    return render_template("results.html", clauses=clauses, filename=filename)


@app.route("/download_txt/<filename>")
def download_txt(filename):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file_ext = filename.rsplit(".", 1)[1].lower()

    if file_ext == "pdf":
        raw_text = extract_text_from_pdf(filepath)
    else:
        raw_text = extract_text_from_txt(filepath)

    clauses = extract_clauses(raw_text)

    output_text = ""
    for title, body in clauses.items():
        output_text += f"=== {title} ===\n"
        output_text += body + "\n\n"

    mem = io.BytesIO()
    mem.write(output_text.encode("utf-8"))
    mem.seek(0)

    return send_file(
        mem,
        as_attachment=True,
        download_name=f"{filename}_clauses.txt",
        mimetype="text/plain"
    )


@app.route("/download_csv/<filename>")
def download_csv(filename):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file_ext = filename.rsplit(".", 1)[1].lower()

    if file_ext == "pdf":
        raw_text = extract_text_from_pdf(filepath)
    else:
        raw_text = extract_text_from_txt(filepath)

    clauses = extract_clauses(raw_text)

    mem = io.StringIO()
    writer = csv.writer(mem)
    writer.writerow(["Heading", "Clause Text"])
    for title, body in clauses.items():
        cleaned_body = " ".join(body.splitlines())
        writer.writerow([title, cleaned_body])
    mem.seek(0)

    return send_file(
        io.BytesIO(mem.getvalue().encode("utf-8")),
        as_attachment=True,
        download_name=f"{filename}_clauses.csv",
        mimetype="text/csv"
    )


@app.route("/ask_ai", methods=["POST"])
def ask_ai():
    """
    Receives a JSON payload: { "message": "user’s question" }.
    Relays it to Gemini Pro API, then returns JSON: { "reply": "AI’s answer" }.
    """
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "Please provide a valid question."})

    # Construct a prompt tailored for simple legal explanations
    prompt = f"You are a knowledgeable legal assistant. Explain in simple terms: {user_message}"

    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    body = {
    "contents": [
        {
        "parts": [
            {"text": prompt}
        ]
        }
    ]
    }

    try:
        resp = requests.post(api_url, headers=headers, params=params, json=body, timeout=10)
        print("Response Text:", resp.text) 
        resp.raise_for_status()
        result = resp.json()

        # Extract the generated text
        ai_reply = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        if not ai_reply:
            ai_reply = "I'm sorry, I couldn't generate a response at this moment."
    except Exception as e:
        ai_reply = "Sorry, something went wrong while connecting to the AI service."

    return jsonify({"reply": ai_reply})


if __name__ == "__main__":
    app.run(debug=True)
