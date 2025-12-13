import { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API_BASE = "http://127.0.0.1:8000";

export default function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]); 
  const [loading, setLoading] = useState(false);

  async function send() {
    const q = input.trim();
    if (!q || loading) return;

    const nextMessages = [...messages, { role: "user", content: q }];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(`${API_BASE}/ask`, { question: q });

      setMessages([
        ...nextMessages,
        {
          role: "assistant",
          content: res.data.answer ?? "(no answer)",
          chunks: res.data.chunks || [],
        },
      ]);
    } catch (e) {
      const msg =
        e?.response?.data?.detail ||
        e?.message ||
        "Request failed. Check backend logs.";

      setMessages([
        ...nextMessages,
        { role: "assistant", content: `❌ ${msg}`, chunks: [] },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ marginTop: 24 }}>
      <h2>Chat</h2>

      <div
        style={{
          marginTop: 12,
          padding: 12,
          borderRadius: 12,
          border: "1px solid rgba(255,255,255,0.1)",
          minHeight: 260,
        }}
      >
        {messages.length === 0 ? (
          <div style={{ opacity: 0.7 }}>
            Ask something about the uploaded document…
          </div>
        ) : (
          messages.map((m, idx) => (
            <div
              key={idx}
              style={{
                display: "flex",
                justifyContent: m.role === "user" ? "flex-end" : "flex-start",
                marginBottom: 12,
              }}
            >
              <div
                style={{
                  maxWidth: "78%",
                  padding: "10px 12px",
                  borderRadius: 14,
                  background:
                    m.role === "user"
                      ? "#2563eb"
                      : "rgba(255,255,255,0.08)",
                  whiteSpace: "pre-wrap",
                }}
              >
                {m.role === "assistant" ? (
                  <>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {m.content}
                    </ReactMarkdown>

                    {m.chunks.length > 0 && (
                      <details style={{ marginTop: 8, opacity: 0.85 }}>
                        <summary style={{ cursor: "pointer" }}>
                          Sources ({m.chunks.length})
                        </summary>

                        <div style={{ marginTop: 8 }}>
                          {m.chunks.map((c, i) => (
                            <div
                              key={i}
                              style={{
                                fontSize: 12,
                                marginBottom: 8,
                                padding: 8,
                                borderRadius: 8,
                                background: "rgba(255,255,255,0.05)",
                              }}
                            >
                              <strong>{c.source}</strong> — chunk {c.chunk_id}
                              <div style={{ marginTop: 4 }}>
                                {c.text.slice(0, 240)}…
                              </div>
                            </div>
                          ))}
                        </div>
                      </details>
                    )}
                  </>
                ) : (
                  m.content
                )}
              </div>
            </div>
          ))
        )}
      </div>

      <div style={{ display: "flex", gap: 10, marginTop: 12 }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something..."
          style={{ flex: 1, padding: 10, borderRadius: 10 }}
          onKeyDown={(e) => {
            if (e.key === "Enter") send();
          }}
        />
        <button onClick={send} disabled={loading}>
          {loading ? "Thinking..." : "Send"}
        </button>
      </div>
    </div>
  );
}
