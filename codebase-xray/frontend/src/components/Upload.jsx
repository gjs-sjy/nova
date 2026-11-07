import { useState } from "react";
import axios from "axios";

const API_URL = "http://localhost:8000";

// File picker that sends a .zip to the backend and hands the graph JSON back to App.
function Upload({ onUploaded }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleFileChange(event) {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file); // field name must be "file" to match main.py
      const response = await axios.post(`${API_URL}/upload`, formData);
      onUploaded(response.data);
    } catch (err) {
      if (err.response) {
        // The backend answered with an error, e.g. "Please upload a .zip file."
        setError(err.response.data.detail || "Upload failed.");
      } else {
        setError("Can't reach the backend. Is it running on port 8000?");
      }
    } finally {
      setLoading(false);
      event.target.value = ""; // so picking the same file again still triggers
    }
  }

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <input type="file" accept=".zip" onChange={handleFileChange} disabled={loading} />
      {loading && <span>Analyzing…</span>}
      {error && <span style={{ color: "#ef4444" }}>{error}</span>}
    </div>
  );
}

export default Upload;
