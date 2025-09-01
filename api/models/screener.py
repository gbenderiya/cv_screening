import os, json, math, re
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
from utils.parser import load_cvs, clean_cv, fetch_job_url
from openai import OpenAI
from dotenv import load_dotenv

device = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

# ---------- LLM Client ----------
load_dotenv()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ.get("HF_KEY"),  
)

def query_cv_model(prompt: str):
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0
    )
    return completion.choices[0].message.content

def cosine_to_unit(score: float) -> float:
    if score is None or math.isnan(score):
        return 0.0
    return max(0.0, min(1.0, (score + 1.0) / 2.0))

# ---------- parse CV with LLM ----------


def parse_cv(cvs_clean: str):
    prompt = f"""
Extract structured information from the CV text below.
Keep all Mongolian letters and accents exactly as in the text.

Return STRICT JSON only with these keys:
- PersonalInformation: {{FullName, FamilyName, FatherOrMother, RegistrationNumber, BirthDate, Gender, MaritalStatus, DriverLicense, AddressOrSurname}}
- ContactInformation: {{Phone, Email}}
- Education: list of {{Period, Degree, Major, Institution, GPA}}
- DesiredPosition (type of role the person wants to work in; extract all lines with {{"sector: title"}} exactly as in the CV; do not reuse occupation entries).
- Occupation (the person's primary/official profession and sector {{"sector: title"}})
- WorkExperience: list of {{Period, Duration, Position, Company}}
- Certificates: list of {{Name, Period, Institution}}
- Exams: list of {{Name, Date, Score}}
- Training: list of {{Date, Name, Training Center}} (if available). 
  Important: treat only concrete training course names as Training.
  If the text only shows generic section or labels, or placeholders, DO NOT extract them.
- Skills: list of actual technical or professional or soft skills mentioned (e.g. Photoshop, Excel, Project management).
- Languages: list
- SalaryExpectation: string (if available)
- OtherInformation: string (if relevant)

CV text:
\"\"\"{cvs_clean}\"\"\"
"""

    content = query_cv_model(prompt) 
    try:
        structured = json.loads(content)
    except Exception as e:
        # If the model output is malformed, return raw text for inspection
        structured = {"error": "Invalid JSON from model", "raw_output": content}
    return structured


# ---------- Screen CVs:  embeddings + structured ----------

def parse_duration(duration_text: str) -> float:
    """
    Compute experience years in years.
    """
    if not duration_text or not isinstance(duration_text, str):
        return 0.0

    years, months = 0, 0

    match_years = re.search(r"(\d+)\s*жил", duration_text)
    match_months = re.search(r"(\d+)\s*сар", duration_text)

    if match_years:
        years = int(match_years.group(1))
    if match_months:
        months = int(match_months.group(1))

    return years + months / 12.0

def compute_structured_match(cv_info, job_info):
    """
    Compute a structured match score between a CV and a job description.
    Base score (max = 1.0) is distributed across:
      - Experience (0.3)
      - Education (0.2)
      - Skills (0.3)
      - Training (0.1)
      - Exam/Certification (0.1)
    Bonus: +0.2 if >2 years relevant experience.
    Final score capped at 1.0.
    """
    score = 0.0

    # Weights
    weights = {
        "experience": 0.3,
        "education": 0.2,
        "skills": 0.3,
        "training": 0.1,
        "exam_cert": 0.1
    }

    # ---------- Experience ----------
    exp_score = 0.0
    for exp in cv_info.get("WorkExperience", []):
        exp_text = " ".join(str(v) for v in exp.values()).lower()
        if any(word.lower() in job_info['description'].lower() for word in exp_text.split()):
            exp_score += 1
            total_years = parse_duration(exp.get("Duration", 0))
            if total_years>= 2: # Bonus for >=2 years relevant experience
                score += 0.2
    if exp_score > 0:
        score += weights["experience"]

    # ---------- Education ----------
    edu_score = 0.0
    for edu in cv_info.get("Education", []):
        edu_text = " ".join(str(v) for v in edu.values()).lower()
        if any(word.lower() in job_info['description'].lower() for word in edu_text.split()):
            edu_score += 1
    if edu_score > 0:
        score += weights["education"]

    # ---------- Skills ----------
    job_skills = set(job_info.get("skills", []))
    cv_skills = set(cv_info.get("Skills", []))
    if set(job_skills):
        overlap = len(job_skills.intersection(cv_skills))
        if overlap > 0:
            score += weights["skills"] * (overlap / len(job_skills))

    # ---------- Training ----------
    training_score = 0.0
    for t in cv_info.get("Training", []):
        t_text = " ".join(str(v) for v in t.values()).lower()
        if any(word.lower() in job_info['description'].lower() for word in t_text.split()):
            training_score += 1
    if training_score > 0:
        score += weights["training"]

    # ---------- Exam + Certification ----------
    exam_cert_score = 0.0
    for e in cv_info.get("Exams", []) + cv_info.get("Certificates", []):
        e_text = " ".join(str(v) for v in e.values()).lower()
        if any(word.lower() in job_info['description'].lower() for word in e_text.split()):
            exam_cert_score += 1
    if exam_cert_score > 0:
        score += weights["exam_cert"]
    return min(score, 1.0)

    
def screen_cvs(job_info, cvs):
    """Compute a structured match score between a CV and a job description.
    Base score (max = 1.0) is distributed across:
      - Experience (0.3)
      - Education (0.2)
      - Skills (0.3)
      - Training (0.1)
      - Exam/Certification (0.1)
    Bonus: +0.2 if >2 years relevant experience.
    Final score capped at 1.0.
    """
    job_text = f"{job_info['title']}\n{job_info['description']}\n{job_info['requirements']}\n{' '.join(job_info['skills'])}"
    job_emb = embedding_model.encode([job_text])

    results = []
    for name, cv_text in cvs.items():
        cv_emb = embedding_model.encode([cv_text])
        emb_score_raw = cosine_similarity(job_emb, cv_emb)[0][0] 
        emb_score = cosine_to_unit(emb_score_raw)
        cv_clean = clean_cv(cv_text)
        cv_info = parse_cv(cv_clean)
        struct_score = compute_structured_match(cv_info, job_info)
        final_score = 0.6*emb_score + 0.4*struct_score

        results.append((name, final_score, cv_text, cv_info))

    results.sort(key=lambda x: x[1], reverse=True)
    print("Results:", results)
    return results

# ---------- Extract Candidate Skills to generate exams ----------

def extract_candidate_skills(cv_info: dict) -> list:
    """
    Extract candidate skills with source-based confidence:
      - Explicit skills: high confidence (80)
      - Certificates/Training/Exams: medium confidence (50)
    Deduplicate while keeping the highest confidence.
    """
    skills_list = []

    # Explicit skills
    for s in cv_info.get("Skills", []):
        skill_name = s.strip()
        if skill_name:
            skills_list.append({"Skill": skill_name, "Confidence": 80, "Source": "explicit"})

    # Certificates (only include if not already in explicit skills)
    explicit_names = {s["Skill"] for s in skills_list}
    for c in cv_info.get("Certificates", []):
        name = c.get("Name", "").strip()
        if name and name not in explicit_names:
            skills_list.append({"Skill": name, "Confidence": 50, "Source": "certificate"})

    # Training
    for t in cv_info.get("Training", []):
        name = t.get("Name", "").strip()
        if name and name not in explicit_names:
            skills_list.append({"Skill": name, "Confidence": 50, "Source": "training"})

    # Exams
    for e in cv_info.get("Exams", []):
        name = e.get("Name", "").strip()
        if name and name not in explicit_names:
            skills_list.append({"Skill": name, "Confidence": 50, "Source": "exam"})

    # Deduplicate by skill name and keep max confidence
    skill_dict = {}
    for s in skills_list:
        skill_name = s["Skill"]
        if skill_name in skill_dict:
            skill_dict[skill_name] = max(skill_dict[skill_name], s["Confidence"])
        else:
            skill_dict[skill_name] = s["Confidence"]

    deduped_skills = [{"Skill": k, "Confidence": v} for k, v in skill_dict.items()]
    return deduped_skills


def generate_skill_tests_with_llm(cv_info: dict, job_info: dict) -> list:
    """
    Generate dynamic, job-specific SkillTests for candidate skills using an LLM.
    Only include skills extracted from explicit candidate skills.
    """
    candidate_skills = extract_candidate_skills(cv_info)
    candidate_skills = [s for s in candidate_skills if s["Confidence"] >= 50] # Filter out low-confidence or non-explicit skills if desired
    
    if not candidate_skills:
        return []

    prompt = f"""
    You are an HR assistant generating practical SkillTests for a candidate.

    Job Description:
    Title: {job_info.get('title', '')}
    Description: {job_info.get('description', '')}
    Skills required: {', '.join(job_info.get('skills', []))}

    Candidate Skills:
    {json.dumps(candidate_skills, ensure_ascii=False)}

    Task:
    For each skill above, generate a practical SkillTest.
    Return a JSON array of objects with:
    {{
      "Skill": "<skill name>",
      "Confidence": "<0-100>",
      "Test": "<practical task or question>"
    }}
    Do not invent skills not present in candidate profile.
    Deduplicate skills.
    """

    content = query_cv_model(prompt)
    try:
        skill_tests = json.loads(content)
    except Exception:
        skill_tests = [{"error": "Invalid JSON from model", "raw_output": content}]

    return skill_tests

# ---------- LLM Evaluation ----------

def normalize_structured_score(score: float) -> float:
    """
    Simple bias-aware normalization to reduce extreme values.
    """
    return max(0.0, min(1.0, score * 0.9 + 0.05))

def evaluate_with_llm(job_info, cv_info, cv_name):
    """
    Enhanced CV evaluation:
    - Strengths, Weaknesses, Relevance
    """
    prompt = f"""
You are a CV screening assistant.
Job Posting:
Title: {job_info['title']}
Description: {job_info['description']}
Skills: {', '.join(job_info['skills'])}

Candidate CV ({cv_name}):
{cv_info}

Output JSON only:
{{
  "Relevance": "<0-100>",
  "Strengths": ["max 5 skills/experience matching job"],
  "Weaknesses": ["max 3 gaps/missing requirements"],
  "Recommendation": "<Shortlist/Reject>"
}}
"""
    content =  query_cv_model(prompt) 
    try:
        structured = json.loads(content)
    except Exception as e:
        # If the model output is malformed, return raw text for inspection
        structured = {"error": "Invalid JSON from model", "content": content}
    return structured
    

