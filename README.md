# 📄 Contract Clause Extraction Tool (with Gemini AI Assistant)


An NLP-powered web app to automatically extract key legal clauses from contracts (`.pdf` or `.txt`) and explain them using **Gemini AI**. Built with **Flask, spaCy, PyMuPDF**, and a beautiful responsive UI.

---

## 🚀 Features

- ✅ Upload PDF or TXT contracts
- 🔍 Extract legal clauses like:
  - Termination
  - Confidentiality
  - Governing Law
  - Payment Terms
  - Dispute Resolution
- 🧠 Ask **Gemini AI** to explain complex clauses
- 📤 Download extracted clauses as `.txt` or `.csv`
- ⚡ Fully responsive interface with modern design

---

## 🧰 Tech Stack

| Layer        | Tech Used                   |
|--------------|-----------------------------|
| Backend      | Flask, Python, spaCy        |
| PDF Parsing  | PyMuPDF (`fitz`)            |
| Frontend     | HTML, Bootstrap, Custom CSS |
| AI Assistant | Gemini Pro API (Free)       |

---

## 🧠 Gemini AI API Setup (Free)

This project uses **Google Gemini Pro API** via [AI Studio](https://makersuite.google.com/), which is **100% free** (no billing required).

### ✅ How to Get Your Gemini API Key

1. Go to 👉 [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account.
3. Click **“Get API Key”**
4. Copy the generated key (looks like `AIzaSyD...`)
5. In `app.py`, paste it here:

## Python
```GEMINI_API_KEY = "your_real_api_key_here"```


## Installation
``` git clone https://github.com/yourusername/contract-clause-extractor
cd contract-clause-extractor
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

