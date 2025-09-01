import os
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
from models import screener 
from utils import parser



# Folder for CVs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # api/
DATA_FOLDER = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_FOLDER, exist_ok=True)

app = FastAPI(title="CV Screening API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "CV API is running"}

@app.post("/upload-cv/")
async def upload_cv(file: UploadFile = File(...)):
    """Upload and save a CV to api/data folder"""
    if not file.filename.endswith(".pdf"):
        return JSONResponse(status_code=400, content={"error": "Only PDF files are allowed"})

    save_path = os.path.join(DATA_FOLDER, file.filename)

    with open(save_path, "wb") as f:
        f.write(await file.read())

    return {"message": f"Uploaded {file.filename} successfully"}


@app.get("/list-cvs/", response_model=List[str])
def list_cvs():
    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".pdf")]
    return files  # just a list


@app.get("/screen/")
def screen_cvs(job_url: str = Query(...), top_n: int = 3):
    """
    Just rank CVs by embeddings/structured similarity.
    Does NOT run LLM evaluation automatically.
    """
    try:
        cvs = parser.load_cvs(DATA_FOLDER)
        job_info = parser.fetch_job_url(job_url)
        ranked_results = screener.screen_cvs(job_info, cvs)

        output = []
        for name, score, _cv_text, cv_info in ranked_results[:top_n]:
            output.append({
                "cv_name": name,
                "score": score,
            })

        return {"top_results": output}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/evaluate/")
def evaluate_cv(cv_name: str = Query(...), job_url: str = Query(...)):
    """
    Evaluate a single CV with LLM when user clicks button.
    """
    try:
        cvs = parser.load_cvs(DATA_FOLDER)
        if cv_name not in cvs:
            return {"error": f"{cv_name} not found"}

        job_info = parser.fetch_job_url(job_url)
        cv_text = cvs[cv_name]
        cv_clean = parser.clean_cv(cv_text)
        cv_info = screener.parse_cv(cv_clean)

        evaluation = screener.evaluate_with_llm(job_info, cv_info, cv_name)
        return {"cv_name": cv_name, "evaluation": evaluation}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/generate-test/")
def generate_test(cv_name: str = Query(...), job_url: str = Query(...)):
    """
    Generate skill tests manually for a single CV.
    """
    try:
        cvs = parser.load_cvs(DATA_FOLDER)
        if cv_name not in cvs:
            return {"error": f"{cv_name} not found"}

        job_info = parser.fetch_job_url(job_url)
        cv_text = cvs[cv_name]
        cv_clean = parser.clean_cv(cv_text)
        cv_info = screener.parse_cv(cv_clean)

        tests = screener.generate_skill_tests_with_llm(cv_info, job_info)
        return {"cv_name": cv_name, "SkillTests": tests}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
