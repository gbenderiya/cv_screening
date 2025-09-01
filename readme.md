# CV Шалгах Платформ 
## Техникийн Баримт бичиг
Энэхүү төсөл нь AI-д суурилсан CV шалгах платформ бөгөөд ажил горилогчдыг ажлын байрны шаардлагатай нийцүүлэх процессыг автоматжуулах, сайжруулахад зориулагдсан. Систем нь дараах гол боломжуудыг агуулна:
- CV болон ажлын байрны текстийг семантик embeddings ашиглан харьцуулж дүн шинжилгээ хийх
- Туршлага, боловсрол, ур чадвар, сургалт болон сертификат зэрэг бүтэцтэй онцлог шинж чанарт суурилсан дүн шинжилгээ хийх
- LLM (жишээ нь OpenAI GPT) ашиглан кандидат тус бүрийг ажлын байрны тодорхойлолттой харьцуулан татгалзах эсвэл дараагийн шатанд оруулах шалгаруулалтыг автоматаар хийж, ажил олгогчийн ажлыг хөнгөвчлөх
- Хэрвээ ажил олгогч кандидатын ур чадварыг баталгаажуулах шаардлагатай гэж үзвэл LLM ашиглан кандидат тус бүрт зориулсан ур чадварын тест үүсгэх
- Хэрэглэгчдэд ээлтэй вэб интерфэйсээр CV оруулах, ажлын байр сонгох, үр дүнг харах

Системийн дизайн болон CV шинжилгээний аргачлал нь ([arXiv:2504.02870v1](https://arxiv.org/abs/2504.02870)) судалгаанаас санаа авсан бөгөөд дараах гол ойлголтуудыг хэрэгжүүлсэн:
- CV болон ажлын байрны семантик төстэй байдлыг хэмжих embedding
- Бүтэцтэй онцлог шинж чанарын олборлолт (structured feature extraction)
- Холимог дүн шинжилгээ (hybrid scoring) .

## Системийн архитектур
Систем нь 3 үндсэн хэсэг-тэй:
** 1.Frontend (React) **
- CV оруулах форм
- Ажлын байр сонгох интерфэйс
- Kандидатуудаа жагсаалт болон графикаар харах боломж
- Шилдэг kандидатт-уудын LLM-ийн санал болгосон дараагийн шат/татгалзах шийдвэр харах

**  2.Backend (FastAPI) ** 
CV хариуцсан эндпоинтүүд:
- /upload_cv – CV-г серверт хадгалах
- /screen – CV болон ажлын байрны similarity оноо тооцох
- /generate_test – Kандидат зориулсан ур чадварын тест үүсгэх
- /evaluate - Сонгосон CV-г LLM ашиглан үнэлэх
LLM интеграц: CV үнэлгээ, тест үүсгэх, автомат шийдвэр гаргах
Structured scoring: Туршлага, боловсрол, ур чадвар, сургалт, сертификат зэрэгт суурилан оноо өгөх

**  3.Database / Storage **  
CV файлууд хадгалах

## CV Шинжилгээний аргачлал
- ** Text Embedding ** – CV болон job description-ийг semantic embedding-д хөрвүүлж similarity оноо гаргах
- ** LLM-д суурилсан CV Parse ** – CV-г LLM ашиглан бүтцээр нь задлах, туршлага, боловсрол, ур чадвар, сургалт, сертификат зэрэг талбаруудыг автоматаар олборлох. LLM (жишээ нь OpenAI GPT- gpt-oss-120b) ашиглан дараах мэдээллийг гаргаж авна:
    -  Нэр, холбоо барих мэдээлэл
    -  Ажлын туршлага (компани, албан тушаал, хугацаа)
    -  Боловсрол (сургуулийн нэр, зэрэг, он)
    -  Ур чадвар, мэргэжлийн чадварууд
    -  Сургалт, сертификат
      Гаргаж авсан өгөгдөл нь дараагийн evaluation, auto decision, test generation процессыг дэмжинэ
- ** Structured Feature Scoring ** – Туршлага, боловсрол, ур чадвар, сургалт, сертификат дээр суурилсан оноо
- ** Hybrid Scoring ** – Semantic similarity + Structured scoring = нийт оноо
- **LLM-д суурилсан үнэлгээ ** – Candidate-ийн хүчтэй, сул талууд, нийцэл, дараагийн шат эсвэл татгалзах санал
- **LLM-д суурилсан тест үүсгэх  **– Candidate тус бүрт domain-specific ур чадварын тест үүсгэх
Database / Storage

CV файлууд, дүн шинжилгээний үр дүн, туршилтын тестүүдийг хадгалах
![alt text](images/image.png)

![alt text](images/image_workflow.png)

![alt text](images/CV%20matching%20workflow.png)
---

## System Architecture of the System
<img width="707" height="524" alt="image" src="https://github.com/user-attachments/assets/39b7da2c-6705-4dad-90a7-c6dbc1727c65" />


## Features

- Upload and store CVs in PDF format.
- List all uploaded CVs.
- Screen CVs against a job posting URL using:
  - Semantic similarity (embedding-based)
  - Structured data matching (experience, skills, education, certifications)
- Evaluate individual CVs with LLMs:
  - Relevance score
  - Strengths & weaknesses
  - Shortlist/reject recommendation
- Generate skill tests for candidates based on extracted skills.
- Web UI for uploading CVs, entering job URLs, and viewing results.

---

## Tech Stack

- **Backend:** Python, FastAPI, PyPDF2, Sentence Transformers, OpenAI API
- **Frontend:** React, Tailwind CSS
- **Database:** None (CVs stored locally in `api/data`)
- **LLM:** OpenAI GPT or HF-hosted LLM for parsing CVs and generating evaluations/tests

---

## Setup Instructions
### Clone repository:
```
git clone <repo-url>
cd CV-Screening-Platform
```
### Setup Python environment:
```
python -m venv env
source env/bin/activate   # Linux/macOS
source .venv/Scripts/activate     # Windows
pip install -r requirements.txt
```

Configure .env with HF_KEY for LLM access.

## Run backend:
```
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Run frontend:
```
cd ui
npm install
npm run dev
```

Upload CVs, enter job URL, and evaluate candidates.


## Screenshots
Here are some screenshots of the application:

<img width="901" height="660" alt="image" src="https://github.com/user-attachments/assets/72bcbba1-9fa0-4f2b-be4c-4dc490c93a96" />

**Main Dashboard Screen**


<img width="924" height="629" alt="image" src="https://github.com/user-attachments/assets/25de5f7b-4260-4296-91d6-afb3e742dd70" />
**Screenshot of Screening**


<img width="946" height="642" alt="image" src="https://github.com/user-attachments/assets/d978798a-9d7b-4b24-bc27-93d26610aef2" />
**Screenshot of Evaluation**



<img width="536" height="590" alt="image" src="https://github.com/user-attachments/assets/acb96553-5033-4ff2-b561-e81b24dcb84b" />
**Screenshot of generated mini exam**

## Demo Video
Watch the demonstration of the project to understand its workflow and functionality:

https://github.com/user-attachments/assets/69244871-33ac-4fa1-b53f-23c7cec8d174










