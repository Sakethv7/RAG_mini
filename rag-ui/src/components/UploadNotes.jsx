import { useState } from "react";
import axios from "axios";

export default function UploadNotes() {
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState("");

  const upload = async () => {
    if (!file) {
      setMsg("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:8000/add_notes", formData);
      setMsg(`Indexed ${res.data.added} chunks`);
    } catch (err) {
      console.error(err);
      setMsg("Upload failed.");
    }
  };

  return (
    <div className="p-6 bg-gray-800 rounded-xl shadow-md">
      <h2 className="text-xl font-semibold mb-4">Upload Notes</h2>

      <input
        type="file"
        className="text-white"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button
        onClick={upload}
        className="bg-blue-600 text-white px-4 py-2 rounded ml-3"
      >
        Upload
      </button>

      <p className="mt-3 text-sm text-gray-300">{msg}</p>
    </div>
  );
}
