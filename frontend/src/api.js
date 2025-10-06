export async function analyzeResume({ file, jobText, maxK = 10 }) {
    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
    const form = new FormData();
    form.append("resume_file", file);
    form.append("job_text", jobText);
    form.append("max_k", 10);
  
    const res = await fetch(`${API_URL}/analyze`, { method: "POST", body: form });
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`API ${res.status}${text ? `: ${text}` : ""}`);
    }
    return res.json();
  }
  