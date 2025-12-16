import { useState } from "react";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "https://rag-mini.onrender.com";

export default function UploadNotes() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  async function upload() {
    if (!file) return;

    setStatus("Uploading…");

    const form = new FormData();
    form.append("file", file);

    try {
      await axios.post(`${API_BASE}/upload`, form);
      setStatus("✅ Document indexed successfully");
    } catch {
      setStatus("❌ Upload failed");
    }
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <h2 className="font-medium mb-3">Upload document</h2>

      <div className="flex items-center gap-3">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          className="block w-full text-sm text-slate-300
                     file:mr-4 file:rounded-md file:border-0
                     file:bg-slate-800 file:px-4 file:py-2
                     file:text-slate-200 hover:file:bg-slate-700"
        />

        <button
          onClick={upload}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium hover:bg-blue-500"
        >
          Upload
        </button>
      </div>

      <p className="mt-2 text-xs text-slate-400">
        Supported: PDF, TXT, MD
      </p>

      {status && (
        <p className="mt-2 text-sm text-slate-300">{status}</p>
      )}
    </div>
  );
}
