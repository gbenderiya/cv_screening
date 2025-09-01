import React, { useState } from "react";

export default function UploadForms({ refreshCvs }) {
  const [file, setFile] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    await fetch("http://localhost:8000/upload-cv/", {
      method: "POST",
      body: formData,
    });

    setFile(null); 
    if (refreshCvs) refreshCvs(); // Auto-refresh
  };

  return (
    <div className="bg-white shadow rounded-xl p-4">
      <h3 className="text-lg font-semibold mb-3">Upload CV</h3>
      <form onSubmit={handleUpload} className="flex flex-col space-y-2">
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files[0])}
          className="flex-1 border rounded px-2 py-1 text-sm"
        />
        <button
          type="submit"
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Upload
        </button>
      </form>
    </div>
  );
}
