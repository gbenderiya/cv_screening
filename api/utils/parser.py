import os, re, glob, requests
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()

def load_cvs(folder):
    cvs = {}
    for pdf_file in glob.glob(os.path.join(folder, "*.pdf")):
        cvs[os.path.basename(pdf_file)] = extract_text_from_pdf(pdf_file)
    return cvs

def clean_cv(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s*:\s*', ' : ', text)
    return text.strip()

def extract_job_id(url: str):
    match = re.search(r'/job/([^/?#]+)', url)
    return match.group(1) if match else None

def fetch_job_url(url):
    job_id = extract_job_id(url)
    api_url = f"https://new-api.zangia.mn/api/jobs/{job_id}"
    resp = requests.get(api_url)
    resp.raise_for_status()
    d = resp.json()
    return {
        "title": d.get("title", ""),
        "description": d.get("description", ""),
        "requirements": d.get("requirements", ""),
        "skills": [s.strip().lower() for s in d.get("skills", [])],
        "additional": d.get("additional", "")
    }
