## Resume Tailor

**Live demo:** [https://resume-tailor-at9k.onrender.com](https://resume-tailor-at9k.onrender.com)

Resume Tailor is an AI-powered web app that helps job seekers **optimize their resumes for specific job descriptions**.  
It parses your resume, extracts your skills, compares them to keywords from a job description, and gives tailored feedback, so you know exactly what to improve before applying.

---

## Features

- **Smart resume parsing:** Automatically extracts your contact info, skills, and experience from PDF resumes.  
- **Job description analysis:** Detects key technologies and terms in the posting.  
- **Instant scoring:** Calculates how closely your resume aligns with the job.  
- **Targeted insights:** Shows what skills are missing and what to add to your skills section.  
- **Clean, responsive UI:** Built with React + Vite and styled for clarity.  

---

## Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | React (Vite) |
| **Backend** | FastAPI (Python 3.12) |
| **Parsing** | PyPDF2, Regular Expressions |
| **Infra / DevOps** | Docker, Render |
| **Language Models** | Simple keyword extraction via regex + scoring logic |

---

## 🗂️ Project Structure
```
resume-tailor/
├── backend/
│ ├── main.py # FastAPI entrypoint
│ ├── parser.py # Extracts info from resume PDFs
│ ├── keywords.py # Extracts keywords from job description
│ ├── matcher.py # Compares resume vs. job description
│ ├── requirements.txt
│ └── Dockerfile
│
├── frontend/
│ ├── src/
│ │ ├── App.jsx
│ │ ├── api.js
│ │ ├── components/
│ ├── .env # Dev API URL (localhost)
│ ├── .env.production # Prod API URL (Render backend)
│ └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

## Future Enhancements

- Use AI models (OpenAI / Hugging Face) for deeper semantic keyword matching.
  
- Support DOCX resumes and multiple file formats.

- Store past analyses and feedback history.

- Add authentication for returning users.

- Improve keyword weighting and recommendations.

