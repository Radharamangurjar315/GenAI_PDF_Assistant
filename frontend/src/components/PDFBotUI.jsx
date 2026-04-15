import { useState, useRef, useEffect, useCallback } from "react";

// ─── Design Tokens ───────────────────────────────────────────────────────────
const css = `
  @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Mono:wght@300;400;500&family=Geist:wght@300;400;500;600&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --ink: #0e0e0e;
    --paper: #f5f2ec;
    --cream: #ede9df;
    --muted: #a09d96;
    --accent: #c84b31;
    --accent-soft: #f0e8e4;
    --accent-mid: #e07055;
    --green: #2e7d5a;
    --green-soft: #e4f0ea;
    --border: rgba(14,14,14,0.12);
    --border-strong: rgba(14,14,14,0.22);
    --shadow-sm: 0 1px 3px rgba(14,14,14,0.08);
    --shadow-md: 0 4px 16px rgba(14,14,14,0.10);
    --shadow-lg: 0 12px 40px rgba(14,14,14,0.14);
    --ff-serif: 'Instrument Serif', Georgia, serif;
    --ff-sans: 'Geist', sans-serif;
    --ff-mono: 'DM Mono', monospace;
    --radius: 10px;
    --radius-lg: 16px;
  }

  body { background: var(--paper); color: var(--ink); font-family: var(--ff-sans); }

  .app {
    min-height: 100vh;
    display: grid;
    grid-template-columns: 280px 1fr;
    grid-template-rows: auto 1fr;
    background: var(--paper);
  }

  /* ─── Header ─── */
  .header {
    grid-column: 1 / -1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 28px;
    height: 58px;
    border-bottom: 1px solid var(--border);
    background: var(--paper);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .header-brand {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .header-logo {
    width: 28px; height: 28px;
    background: var(--ink);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
  }

  .header-logo svg { color: var(--paper); }

  .header-title {
    font-family: var(--ff-serif);
    font-size: 17px;
    font-style: italic;
    letter-spacing: 0.01em;
  }

  .header-badge {
    font-family: var(--ff-mono);
    font-size: 10px;
    font-weight: 400;
    letter-spacing: 0.08em;
    color: var(--muted);
    background: var(--cream);
    border: 1px solid var(--border);
    padding: 3px 8px;
    border-radius: 20px;
    text-transform: uppercase;
  }

  .header-status {
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: var(--ff-mono);
    font-size: 11px;
    color: var(--muted);
  }

  .status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--muted);
    transition: background 0.3s;
  }
  .status-dot.ready { background: var(--green); box-shadow: 0 0 0 2px var(--green-soft); }
  .status-dot.pulse {
    background: var(--accent);
    animation: pulse 1.2s ease-in-out infinite;
  }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.35} }

  /* ─── Sidebar ─── */
  .sidebar {
    border-right: 1px solid var(--border);
    background: var(--cream);
    display: flex;
    flex-direction: column;
    padding: 20px 16px;
    gap: 8px;
    overflow-y: auto;
  }

  .sidebar-section-label {
    font-family: var(--ff-mono);
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    padding: 0 8px;
    margin-top: 8px;
    margin-bottom: 2px;
  }

  /* ─── Upload zone ─── */
  .upload-zone {
    border: 1.5px dashed var(--border-strong);
    border-radius: var(--radius);
    padding: 20px 16px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    background: var(--paper);
    position: relative;
    overflow: hidden;
  }
  .upload-zone:hover, .upload-zone.dragging {
    border-color: var(--accent);
    background: var(--accent-soft);
  }
  .upload-zone input {
    position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%;
  }
  .upload-icon {
    width: 32px; height: 32px;
    background: var(--ink);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 8px;
    color: var(--paper);
  }
  .upload-label {
    font-size: 12.5px;
    font-weight: 500;
    color: var(--ink);
    margin-bottom: 3px;
  }
  .upload-sub {
    font-size: 11px;
    color: var(--muted);
    font-family: var(--ff-mono);
  }

  /* ─── Upload progress ─── */
  .upload-progress {
    border-radius: var(--radius);
    background: var(--paper);
    border: 1px solid var(--border);
    padding: 12px 14px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .upload-progress-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 500;
    color: var(--ink);
  }
  .spinner {
    width: 14px; height: 14px;
    border: 2px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    flex-shrink: 0;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .progress-bar-track {
    height: 3px;
    background: var(--border);
    border-radius: 99px;
    overflow: hidden;
  }
  .progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent), var(--accent-mid));
    border-radius: 99px;
    transition: width 0.3s ease;
  }

  /* ─── Document cards ─── */
  .doc-card {
    border-radius: var(--radius);
    background: var(--paper);
    border: 1px solid var(--border);
    padding: 10px 12px;
    display: flex;
    align-items: flex-start;
    gap: 10px;
    animation: slideIn 0.3s ease;
  }
  @keyframes slideIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .doc-icon {
    width: 30px; height: 30px; flex-shrink: 0;
    background: var(--accent-soft);
    border: 1px solid rgba(200,75,49,0.15);
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    color: var(--accent);
    font-family: var(--ff-mono);
    font-size: 8px;
    font-weight: 500;
    letter-spacing: 0.05em;
  }
  .doc-info { flex: 1; min-width: 0; }
  .doc-name {
    font-size: 12px;
    font-weight: 500;
    color: var(--ink);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 2px;
  }
  .doc-meta {
    font-family: var(--ff-mono);
    font-size: 10px;
    color: var(--muted);
  }
  .doc-meta span { color: var(--green); font-weight: 500; }

  /* ─── Session controls ─── */
  .session-input-row {
    display: flex;
    gap: 6px;
  }
  .session-input {
    flex: 1;
    font-family: var(--ff-mono);
    font-size: 11px;
    padding: 7px 10px;
    border: 1px solid var(--border);
    border-radius: 7px;
    background: var(--paper);
    color: var(--ink);
    outline: none;
    min-width: 0;
    transition: border-color 0.15s;
  }
  .session-input:focus { border-color: var(--ink); }
  .icon-btn {
    width: 30px; height: 30px;
    border: 1px solid var(--border);
    border-radius: 7px;
    background: var(--paper);
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    color: var(--muted);
    transition: all 0.15s;
    flex-shrink: 0;
  }
  .icon-btn:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }

  .stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
  }
  .stat-cell {
    background: var(--paper);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px;
    text-align: center;
  }
  .stat-value {
    font-family: var(--ff-serif);
    font-size: 20px;
    color: var(--ink);
    line-height: 1;
    margin-bottom: 3px;
  }
  .stat-label {
    font-family: var(--ff-mono);
    font-size: 9.5px;
    color: var(--muted);
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  /* ─── Main chat area ─── */
  .main {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 58px);
    overflow: hidden;
  }

  .chat-area {
    flex: 1;
    overflow-y: auto;
    padding: 28px 32px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    scroll-behavior: smooth;
  }
  .chat-area::-webkit-scrollbar { width: 4px; }
  .chat-area::-webkit-scrollbar-track { background: transparent; }
  .chat-area::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }

  /* ─── Empty state ─── */
  .empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
    padding: 48px;
    text-align: center;
  }
  .empty-glyph {
    width: 64px; height: 64px;
    border: 1.5px solid var(--border-strong);
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    color: var(--muted);
    font-family: var(--ff-serif);
    font-style: italic;
    font-size: 22px;
  }
  .empty-title {
    font-family: var(--ff-serif);
    font-size: 22px;
    font-style: italic;
    color: var(--ink);
    line-height: 1.3;
  }
  .empty-sub {
    font-size: 13px;
    color: var(--muted);
    max-width: 320px;
    line-height: 1.6;
  }
  .suggestion-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin-top: 4px;
  }
  .chip {
    font-size: 12px;
    padding: 7px 14px;
    border: 1px solid var(--border);
    border-radius: 20px;
    background: var(--paper);
    cursor: pointer;
    color: var(--ink);
    transition: all 0.15s;
    font-family: var(--ff-sans);
    white-space: nowrap;
  }
  .chip:hover { border-color: var(--ink); background: var(--ink); color: var(--paper); }

  /* ─── Messages ─── */
  .msg-row {
    display: flex;
    gap: 12px;
    animation: msgIn 0.28s ease;
  }
  @keyframes msgIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .msg-row.user { flex-direction: row-reverse; }

  .msg-avatar {
    width: 28px; height: 28px;
    border-radius: 8px;
    flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-family: var(--ff-mono);
    font-size: 10px;
    font-weight: 500;
    margin-top: 2px;
  }
  .msg-avatar.bot {
    background: var(--ink);
    color: var(--paper);
  }
  .msg-avatar.user {
    background: var(--accent-soft);
    color: var(--accent);
    border: 1px solid rgba(200,75,49,0.2);
  }

  .msg-bubble {
    max-width: 72%;
    padding: 12px 16px;
    border-radius: var(--radius);
    line-height: 1.65;
    font-size: 14px;
    position: relative;
  }
  .msg-row.bot .msg-bubble {
    background: var(--paper);
    border: 1px solid var(--border);
    color: var(--ink);
    border-radius: 4px var(--radius) var(--radius) var(--radius);
    box-shadow: var(--shadow-sm);
  }
  .msg-row.user .msg-bubble {
    background: var(--ink);
    color: var(--paper);
    border-radius: var(--radius) 4px var(--radius) var(--radius);
  }

  .msg-meta {
    font-family: var(--ff-mono);
    font-size: 10px;
    color: var(--muted);
    margin-top: 5px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .msg-row.user .msg-meta { justify-content: flex-end; }

  .sources-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: var(--green-soft);
    color: var(--green);
    border: 1px solid rgba(46,125,90,0.2);
    border-radius: 4px;
    padding: 2px 7px;
    font-family: var(--ff-mono);
    font-size: 10px;
    font-weight: 500;
  }

  /* ─── Typing indicator ─── */
  .typing-bubble {
    display: flex;
    gap: 4px;
    padding: 14px 16px;
    background: var(--paper);
    border: 1px solid var(--border);
    border-radius: 4px var(--radius) var(--radius) var(--radius);
    box-shadow: var(--shadow-sm);
    align-items: center;
  }
  .typing-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--muted);
    animation: typingBounce 1.2s ease-in-out infinite;
  }
  .typing-dot:nth-child(2) { animation-delay: 0.2s; }
  .typing-dot:nth-child(3) { animation-delay: 0.4s; }
  @keyframes typingBounce {
    0%,60%,100%{ transform: translateY(0); opacity: 0.5; }
    30%{ transform: translateY(-5px); opacity: 1; }
  }

  /* ─── Error message ─── */
  .msg-error {
    background: #fff5f4;
    border: 1px solid rgba(200,75,49,0.25);
    color: var(--accent);
    border-radius: 4px var(--radius) var(--radius) var(--radius);
    padding: 10px 14px;
    font-size: 13px;
    max-width: 72%;
  }

  /* ─── Input bar ─── */
  .input-bar {
    padding: 16px 24px 20px;
    border-top: 1px solid var(--border);
    background: var(--paper);
  }
  .input-form {
    display: flex;
    gap: 8px;
    align-items: flex-end;
    background: var(--cream);
    border: 1.5px solid var(--border-strong);
    border-radius: 14px;
    padding: 10px 10px 10px 16px;
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  .input-form:focus-within {
    border-color: var(--ink);
    box-shadow: 0 0 0 3px rgba(14,14,14,0.06);
  }
  .question-input {
    flex: 1;
    border: none;
    background: transparent;
    font-family: var(--ff-sans);
    font-size: 14px;
    color: var(--ink);
    outline: none;
    resize: none;
    line-height: 1.5;
    max-height: 120px;
    min-height: 22px;
  }
  .question-input::placeholder { color: var(--muted); }
  .send-btn {
    width: 36px; height: 36px;
    border-radius: 9px;
    background: var(--ink);
    border: none;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    color: var(--paper);
    flex-shrink: 0;
    transition: all 0.15s;
  }
  .send-btn:hover:not(:disabled) { background: var(--accent); transform: scale(1.04); }
  .send-btn:disabled { background: var(--border); color: var(--muted); cursor: not-allowed; transform: none; }
  .input-hint {
    font-family: var(--ff-mono);
    font-size: 10px;
    color: var(--muted);
    text-align: center;
    margin-top: 8px;
    letter-spacing: 0.03em;
  }

  /* ─── Toast ─── */
  .toast {
    position: fixed;
    bottom: 24px; right: 24px;
    padding: 12px 18px;
    border-radius: var(--radius);
    font-size: 13px;
    font-weight: 500;
    box-shadow: var(--shadow-lg);
    animation: toastIn 0.3s ease;
    z-index: 999;
    display: flex;
    align-items: center;
    gap: 8px;
    max-width: 320px;
  }
  .toast.success { background: var(--ink); color: var(--paper); }
  .toast.error { background: var(--accent); color: var(--paper); }
  @keyframes toastIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* ─── Responsive ─── */
  @media (max-width: 768px) {
    .app { grid-template-columns: 1fr; }
    .sidebar { display: none; }
    .chat-area { padding: 16px; }
    .input-bar { padding: 12px 16px 16px; }
  }
`;

// ─── Icons ───────────────────────────────────────────────────────────────────
const Icons = {
  Upload: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
    </svg>
  ),
  Send: () => (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
    </svg>
  ),
  Trash: () => (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/>
    </svg>
  ),
  File: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
    </svg>
  ),
  Bot: () => (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/>
    </svg>
  ),
  BookOpen: () => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
    </svg>
  ),
  CheckCircle: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
    </svg>
  ),
  AlertCircle: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12" y2="16"/>
    </svg>
  ),
};

// ─── API helpers ─────────────────────────────────────────────────────────────
const API = "http://localhost:8000/api/v1";

async function uploadPDF(file, onProgress) {
  const form = new FormData();
  form.append("file", file);
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) onProgress(Math.round((e.loaded / e.total) * 90));
    };
    xhr.onload = () => {
      onProgress(100);
      if (xhr.status === 201) resolve(JSON.parse(xhr.responseText));
      else {
        try { reject(new Error(JSON.parse(xhr.responseText).detail || "Upload failed")); }
        catch { reject(new Error("Upload failed")); }
      }
    };
    xhr.onerror = () => reject(new Error("Network error"));
    xhr.open("POST", `${API}/upload`);
    xhr.send(form);
  });
}

async function askQuestion(question, sessionId) {
  const res = await fetch(`${API}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, session_id: sessionId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Error ${res.status}`);
  }
  return res.json();
}

async function clearMemory(sessionId) {
  const res = await fetch(`${API}/memory/clear`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
  return res.ok;
}

async function getHealth() {
  const res = await fetch(`${API}/health`);
  return res.ok ? res.json() : null;
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function PDFBotUI() {
  const [docs, setDocs] = useState([]);
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadingName, setUploadingName] = useState("");
  const [asking, setAsking] = useState(false);
  const [sessionId, setSessionId] = useState(() => `session-${Date.now()}`);
  const [dragging, setDragging] = useState(false);
  const [health, setHealth] = useState(null);
  const [toast, setToast] = useState(null);
  const chatEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => {});
    const interval = setInterval(() => getHealth().then(setHealth).catch(() => {}), 15000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, asking]);

  const showToast = useCallback((msg, type = "success") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3500);
  }, []);

  const handleUpload = async (file) => {
    if (!file || !file.name.toLowerCase().endsWith(".pdf")) {
      showToast("Only PDF files are accepted", "error");
      return;
    }
    setUploading(true);
    setUploadProgress(0);
    setUploadingName(file.name);
    try {
      const result = await uploadPDF(file, setUploadProgress);
      setDocs((d) => [...d, { ...result, id: Date.now() }]);
      showToast(`"${result.filename}" indexed — ${result.chunks_created} chunks`);
      getHealth().then(setHealth).catch(() => {});
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setTimeout(() => { setUploading(false); setUploadProgress(0); setUploadingName(""); }, 600);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault(); setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  const handleAsk = async (q) => {
    const text = (q || question).trim();
    if (!text || asking) return;
    setQuestion("");
    setMessages((m) => [...m, { role: "user", content: text, ts: Date.now() }]);
    setAsking(true);
    try {
      const res = await askQuestion(text, sessionId);
      setMessages((m) => [...m, {
        role: "bot",
        content: res.answer,
        sources: res.sources_used,
        ts: Date.now(),
      }]);
    } catch (err) {
      setMessages((m) => [...m, { role: "error", content: err.message, ts: Date.now() }]);
    } finally {
      setAsking(false);
    }
  };

  const handleClear = async () => {
    await clearMemory(sessionId);
    setMessages([]);
    showToast("Conversation cleared");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleAsk(); }
  };

  const autoResize = (e) => {
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
  };

  const statusLabel = health
    ? health.vector_store_ready ? "ready" : "no docs"
    : "connecting";
  const dotClass = health
    ? health.vector_store_ready ? "ready" : ""
    : "pulse";

  const suggestions = [
    "Summarize this document",
    "What are the key findings?",
    "List the main topics covered",
    "What conclusions are drawn?",
  ];

  return (
    <>
      <style>{css}</style>
      <div className="app">

        {/* ─── Header ─── */}
        <header className="header">
          <div className="header-brand">
            <div className="header-logo">
              <Icons.BookOpen />
            </div>
            <span className="header-title">PDF Bot</span>
            <span className="header-badge">RAG · v1.0</span>
          </div>
          <div className="header-status">
            <div className={`status-dot ${dotClass}`} />
            {statusLabel}
            {health && <span style={{ color: "var(--border-strong)" }}>·</span>}
            {health && <span>{health.total_vectors} vectors</span>}
          </div>
        </header>

        {/* ─── Sidebar ─── */}
        <aside className="sidebar">

          <div className="sidebar-section-label">Upload</div>
          {uploading ? (
            <div className="upload-progress">
              <div className="upload-progress-header">
                <div className="spinner" />
                <span style={{ fontSize: 12, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {uploadingName}
                </span>
              </div>
              <div className="progress-bar-track">
                <div className="progress-bar-fill" style={{ width: `${uploadProgress}%` }} />
              </div>
              <span style={{ fontFamily: "var(--ff-mono)", fontSize: 10, color: "var(--muted)" }}>
                {uploadProgress}% · processing
              </span>
            </div>
          ) : (
            <div
              className={`upload-zone ${dragging ? "dragging" : ""}`}
              onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
            >
              <input type="file" accept=".pdf" onChange={(e) => e.target.files[0] && handleUpload(e.target.files[0])} />
              <div className="upload-icon"><Icons.Upload /></div>
              <div className="upload-label">Drop PDF here</div>
              <div className="upload-sub">or click to browse · max 20MB</div>
            </div>
          )}

          {docs.length > 0 && (
            <>
              <div className="sidebar-section-label" style={{ marginTop: 8 }}>Indexed ({docs.length})</div>
              {docs.map((d) => (
                <div className="doc-card" key={d.id}>
                  <div className="doc-icon">PDF</div>
                  <div className="doc-info">
                    <div className="doc-name" title={d.filename}>{d.filename}</div>
                    <div className="doc-meta">
                      <span>{d.chunks_created}</span> chunks · {d.pages_extracted} pages
                    </div>
                  </div>
                </div>
              ))}
            </>
          )}

          <div className="sidebar-section-label" style={{ marginTop: 12 }}>Session</div>
          <div className="session-input-row">
            <input
              className="session-input"
              value={sessionId}
              onChange={(e) => setSessionId(e.target.value)}
              placeholder="session-id"
              spellCheck={false}
            />
            <button className="icon-btn" onClick={handleClear} title="Clear memory">
              <Icons.Trash />
            </button>
          </div>

          {health && (
            <>
              <div className="sidebar-section-label" style={{ marginTop: 12 }}>Stats</div>
              <div className="stats-grid">
                <div className="stat-cell">
                  <div className="stat-value">{health.total_vectors}</div>
                  <div className="stat-label">Vectors</div>
                </div>
                <div className="stat-cell">
                  <div className="stat-value">{health.active_sessions}</div>
                  <div className="stat-label">Sessions</div>
                </div>
              </div>
            </>
          )}
        </aside>

        {/* ─── Main ─── */}
        <main className="main">
          <div className="chat-area">
            {messages.length === 0 && !asking ? (
              <div className="empty-state">
                <div className="empty-glyph">?</div>
                <div className="empty-title">Ask your documents anything</div>
                <div className="empty-sub">
                  Upload a PDF in the sidebar, then start a conversation. The assistant will find relevant sections and answer precisely.
                </div>
                <div className="suggestion-chips">
                  {suggestions.map((s) => (
                    <button key={s} className="chip" onClick={() => handleAsk(s)}>{s}</button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((msg) => (
                  <div key={msg.ts} className={`msg-row ${msg.role === "user" ? "user" : "bot"}`}>
                    {msg.role !== "error" && (
                      <div className={`msg-avatar ${msg.role}`}>
                        {msg.role === "user" ? "U" : <Icons.Bot />}
                      </div>
                    )}
                    {msg.role === "error" ? (
                      <div className="msg-error">{msg.content}</div>
                    ) : (
                      <div>
                        <div className="msg-bubble">{msg.content}</div>
                        <div className="msg-meta">
                          {new Date(msg.ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                          {msg.sources > 0 && (
                            <span className="sources-tag">
                              <Icons.CheckCircle /> {msg.sources} sources
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                {asking && (
                  <div className="msg-row bot">
                    <div className="msg-avatar bot"><Icons.Bot /></div>
                    <div className="typing-bubble">
                      <div className="typing-dot" />
                      <div className="typing-dot" />
                      <div className="typing-dot" />
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </>
            )}
          </div>

          <div className="input-bar">
            <div className="input-form">
              <textarea
                ref={textareaRef}
                className="question-input"
                value={question}
                onChange={(e) => { setQuestion(e.target.value); autoResize(e); }}
                onKeyDown={handleKeyDown}
                placeholder="Ask a question about your documents…"
                rows={1}
                disabled={asking}
              />
              <button
                className="send-btn"
                onClick={() => handleAsk()}
                disabled={!question.trim() || asking}
                title="Send (Enter)"
              >
                {asking ? (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                    <line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/>
                    <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
                    <line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/>
                    <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
                  </svg>
                ) : <Icons.Send />}
              </button>
            </div>
            <div className="input-hint">
              Enter to send · Shift+Enter for new line · Session: {sessionId}
            </div>
          </div>
        </main>

        {/* ─── Toast ─── */}
        {toast && (
          <div className={`toast ${toast.type}`}>
            {toast.type === "success" ? <Icons.CheckCircle /> : <Icons.AlertCircle />}
            {toast.msg}
          </div>
        )}
      </div>
    </>
  );
}
