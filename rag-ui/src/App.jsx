import UploadNotes from "./components/UploadNotes";
import Chat from "./components/Chat";

export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-800 px-6 py-4">
        <h1 className="text-xl font-semibold">RAG Mini</h1>
        <p className="text-sm text-slate-400">
          Ask questions grounded in your documents
        </p>
      </header>

      {/* Main */}
      <main className="max-w-5xl mx-auto px-6 py-6 space-y-6">
        <UploadNotes />
        <Chat />
      </main>
    </div>
  );
}
