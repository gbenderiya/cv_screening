import React, { useState, useEffect } from "react";
import UploadForms from "./components/UploadForm";
import Results from "./components/Results";

export default function App() {
  const [cvs, setCvs] = useState([]);
  const [jobUrl, setJobUrl] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch available CVs from backend
  const fetchCvs = async () => {
    try {
      const res = await fetch("http://localhost:8000/list-cvs/");
      const data = await res.json();
      setCvs(data || []);
    } catch (err) {
      console.error("Error fetching CVs:", err);
    }
  };

  useEffect(() => {
    fetchCvs();
  }, []);

  // Run screening API call
  const runScreening = async () => {
    if (!jobUrl) {
      alert("Please enter a Job URL");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(
        `http://localhost:8000/screen/?job_url=${encodeURIComponent(jobUrl)}&top_n=3`
      );
      const data = await res.json();
      console.log("Screening API response:", data);
      // fallback if backend key differs
      setResults(data.top_results || data.results || data || []);
    } catch (err) {
      console.error("Error running screening:", err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Top Nav */}
      <header className="bg-white shadow">
        <div className="max-w-6xl mx-auto flex items-center justify-between px-6 py-3">
          <div className="flex items-center space-x-3">
            <img
              src="https://www.zangia.mn/_next/image?url=%2Fimages%2Flogos%2Flogo.png&w=256&q=75"
              alt="Logo"
              className="h-10 w-auto"
            />
            <h1 className="absolute left-1/2 transform -translate-x-1/2 text-xl font-bold text-blue-700">
              AI CV Screening
            </h1>
          </div>
          <nav className="space-x-6 text-sm text-gray-700">
            <a href="#" className="hover:text-blue-600">Ажлын зар</a>
            <a href="#" className="hover:text-blue-600">Компани</a>
            <a href="#" className="hover:text-blue-600">MLMS</a>
            <a href="#" className="hover:text-blue-600">Зөвлөгөө</a>
          </nav>
        </div>
      </header>

      {/* Banner */}
      <div className="bg-gradient-to-r from-blue-700 via-purple-600 to-pink-500 text-white text-center py-8">
        <h2 className="text-2xl font-semibold">Advanced AI Screening Platform</h2>
        <p className="text-sm mt-2 opacity-90">Шийдэлтэй ажлын байрны үндсэн платформ</p>
      </div>

      {/* CVs */}
      <section className="max-w-6xl mx-auto px-6 py-6">
        <div className="bg-white shadow rounded-xl p-4 mb-6">
          <h3 className="text-lg font-semibold mb-3 text-center">Онцлох CV-нүүд</h3>
          {cvs.length === 0 ? (
            <p className="text-gray-500 text-center">No CVs available.</p>
          ) : (
            <div className="flex gap-4 justify-center overflow-x-auto">
              {cvs.map((cv, index) => {
                const displayName = cv.replace(/\.pdf$/, "").replace(/\s*\(\d+\)$/, "");
                return (
                  <div
                    key={index}
                    className="p-2 bg-gray-50 rounded hover:bg-blue-50 text-center transition min-w-[150px]"
                  >
                    {displayName}
                  </div>
                );
              })}
            </div>
          )}
          <div className="flex justify-center mt-4 mb-4">
            <img
              src="https://cdn.zangia.mn/b/viber_image_2025-08-22_16-02-07-694.png"
              alt="Illustration"
              className="max-w-full h-auto rounded-lg shadow"
            />
          </div>
        </div>

        {/* Main grid */}
        <main className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-1 space-y-6">
            <div className="bg-white shadow rounded-xl p-4">
              <h3 className="text-lg font-semibold mb-3">Job Posting</h3>
              <input
                type="text"
                placeholder="Enter job posting URL..."
                value={jobUrl}
                onChange={(e) => setJobUrl(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 mb-3"
              />
              <button
                onClick={runScreening}
                className={`w-full px-4 py-2 rounded-lg text-white ${
                  loading ? "bg-gray-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
                }`}
                disabled={loading}
              >
                {loading ? "Running..." : "Run Screening"}
              </button>
            </div>

            <UploadForms refreshCvs={fetchCvs} />
          </div>

          <div className="md:col-span-2 space-y-6">
            {results && results.length > 0 ? (
              <Results results={results} jobUrl={jobUrl} />
            ) : (
              <div className="bg-white shadow rounded-xl p-6 text-gray-500 text-center">
                Screening results will appear here after you run analysis.
              </div>
            )}
          </div>
        </main>
      </section>
    </div>
  );
}
