import { useRef, useState } from "react";
import { analyzeResume } from "./api";
import ScoreBar from "./components/ScoreBar";
import TagList from "./components/TagList";

const firstNameOf = (contact = {}) => {
  const n = (contact.name || "").trim();
  if (n) return n.split(/\s+/)[0];
  // fallback: infer from email local-part if possible
  const em = contact.email || "";
  const guess = em.includes("@") ? em.split("@")[0] : "";
  return guess ? guess.split(/[._-]/)[0] : "there";
};

const fmt = (label, value) =>
  value ? `${label}: ${value}` : `${label}: highly recommend adding`;

export default function App() {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer?.files?.[0];
    if (f && f.type === "application/pdf") setFile(f);
    else setError("Please drop a PDF file.");
  };

  const onFilePick = (e) => {
    const f = e.target.files?.[0];
    if (f && f.type === "application/pdf") setFile(f);
    else setError("Please choose a PDF file.");
  };

  const submit = async (e) => {
    e.preventDefault();
    setError(""); setData(null);
    if (!file) return setError("Upload your resume (PDF).");
    if (!jd.trim()) return setError("Paste a job description.");
    setLoading(true);
    try {
      const result = await analyzeResume({ file, jobText: jd });
      setData(result);
      setTimeout(() => {
        document.getElementById("results")?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (err) {
      setError(err.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  const overall = data?.scores?.overall ?? 0;

  return (
    <div className="page">
      {/* --- Header --- */}
      {/* <header className="header">
        <h1 className="logo">Resume Tailor</h1>
      </header> */}

      <main className="container">
        {/* --- Hero --- */}
        <section className="hero">
          <h2 className="hero-title">Resume Tailor</h2>
          <p className="hero-sub">
            Upload your resume and paste a job description. Get a private, instant match score and
            keyword insights.
          </p>

          <div className="upload-card">
            <div
              className={`dropzone ${dragOver ? "dropzone--over" : ""}`}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={onDrop}
              onClick={() => inputRef.current?.click()}
              role="button"
              tabIndex={0}
            >
              <div className="drop-graphic" aria-hidden>📄</div>
              <div className="drop-title">
                {file ? file.name : "Add your resume by dropping it here"}
              </div>
              <div className="drop-sub">
                Drag & drop a PDF resume or <span className="linklike">click to upload</span>
              </div>
              <input
                ref={inputRef}
                type="file"
                accept="application/pdf"
                onChange={onFilePick}
                className="hidden-input"
              />
            </div>

            <form onSubmit={submit} className="cta-row">
              <button type="submit" disabled={loading} className="cta-btn solid">
                {loading ? "Analyzing…" : "Get My Resume Match"}
              </button>
            </form>
            {error && <div className="error">{error}</div>}
          </div>
        </section>

        {/* --- JD Input --- */}
        <section className="jd-panel">
          <h3 className="panel-title">Paste the Job Description</h3>
          <textarea
            className="jd-textarea"
            rows={8}
            placeholder="Paste the job description here…"
            value={jd}
            onChange={(e) => setJd(e.target.value)}
          />
          <div className="panel-actions">
            <button onClick={submit} disabled={loading} className="cta-btn solid">
              {loading ? "Analyzing…" : "Analyze Resume"}
            </button>
            <a
              href={(import.meta.env.VITE_API_URL || "http://localhost:8000") + "/docs"}
              target="_blank"
              rel="noreferrer"
              className="link"
            >
              {/* API Docs */}
            </a>
          </div>
        </section>

        {/* --- Results --- */}
        {data && (
          <section id="results" className="results-grid">
            {/* Personalized greeting */}
            {data.contact?.name && (
              <div className="results-greeting">
                <h2 className="greeting-text">
                  Hi <span className="highlight">{data.contact.name.split(" ")[0]}</span>, here are your insights:
                </h2>
              </div>
            )}

            {/* Match score */}
            <div className="card span-3">
              <h3 className="card-title">Match Score: {overall}%</h3>
              <ScoreBar value={overall} />
              <p className="muted">Keywords considered: {data.meta?.num_keywords}</p>
            </div>

            {/* Keywords */}
            <div className="card span-3">
              <h3 className="card-title">Keywords Found</h3>
              <div className="chips">
                {data.keywords?.map((k, i) => (
                  <span key={i} className="chip">{k}</span>
                ))}
              </div>
            </div>

            {/* Categories */}
            <div className="card">
              <TagList title="In Skills" items={data.in_skills || []} />
            </div>
            <div className="card">
              <TagList
                title="In Text"
                items={data.in_text_not_skills || []}
                hint="Add these explicitly to your Skills section."
              />
            </div>
            <div className="card">
              <TagList title="Missing" items={data.missing || []} />
            </div>
          </section>
        )}


      </main>
    </div>
  );
}
