import React, { useState } from "react";

export default function Results({ results, jobUrl }) {
  const [evaluations, setEvaluations] = useState({});
  const [loadingCv, setLoadingCv] = useState(null);
  const [testLoading, setTestLoading] = useState(null);
  const [tests, setTests] = useState({});

  const getMatchLabel = (score) => {
    if (score >= 0.8) return "Excellent match";
    if (score >= 0.6) return "Good match";
    if (score >= 0.4) return "Fair match";
    if (score >= 0.2) return "Weak match";
    return "Poor match";
  };

  const handleEvaluate = async (cvName) => {
    setLoadingCv(cvName);
    try {
      const res = await fetch(
        `http://localhost:8000/evaluate/?cv_name=${encodeURIComponent(
          cvName
        )}&job_url=${encodeURIComponent(jobUrl)}`
      );
      const data = await res.json();
      setEvaluations((prev) => ({
        ...prev,
        [cvName]: data.evaluation,
      }));
    } catch (err) {
      console.error("Error evaluating CV:", err);
    } finally {
      setLoadingCv(null);
    }
  };

  const handleGenerateTest = async (cvName) => {
    setTestLoading(cvName);
    try {
      const res = await fetch(
        `http://localhost:8000/generate-test/?cv_name=${encodeURIComponent(
          cvName
        )}&job_url=${encodeURIComponent(jobUrl)}`
      );
      const data = await res.json();
      setTests((prev) => ({
        ...prev,
        [cvName]: data.SkillTests || ["No test generated"],
      }));
    } catch (err) {
      console.error("Error generating test:", err);
    } finally {
      setTestLoading(null);
    }
  };

  return (
    <div className="bg-white shadow rounded-xl p-6">
      <h3 className="text-lg font-semibold mb-4">Screening Results</h3>
      {results.map((cv, i) => (
        <div
          key={i}
          className="p-3 border-b last:border-0 flex flex-col gap-2"
        >
          <div className="flex items-center justify-between">
            <span>
              <strong>{cv.cv_name}</strong> —{" "}
              {(cv.score * 100).toFixed(0)}% match ({getMatchLabel(cv.score)})
            </span>
            <button
              onClick={() => handleEvaluate(cv.cv_name)}
              disabled={loadingCv === cv.cv_name}
              className={`px-3 py-1 rounded ${
                loadingCv === cv.cv_name
                  ? "bg-gray-400 text-white"
                  : "bg-blue-600 text-white hover:bg-blue-700"
              }`}
            >
              {loadingCv === cv.cv_name ? "Evaluating..." : "Evaluate"}
            </button>
          </div>

          {/* Show evaluation if available */}
          {evaluations[cv.cv_name] && (
            <div className="mt-2 p-3 bg-gray-50 rounded text-sm text-gray-700">
              <p>
                <strong>Relevance:</strong>{" "}
                {evaluations[cv.cv_name].Relevance}%
              </p>
              <p><strong>Strengths:</strong></p>
              <ul className="list-disc list-inside ml-3">
                {evaluations[cv.cv_name].Strengths.map((s, idx) => (
                  <li key={idx}>{s}</li>
                ))}
              </ul>
              <p><strong>Weaknesses:</strong></p>
              <ul className="list-disc list-inside ml-3">
                {evaluations[cv.cv_name].Weaknesses.map((w, idx) => (
                  <li key={idx}>{w}</li>
                ))}
              </ul>
              <p>
                <strong>Recommendation:</strong>{" "}
                {evaluations[cv.cv_name].Recommendation}
              </p>

              {/* Generate test button */}
              <div className="mt-3">
                <button
                  onClick={() => handleGenerateTest(cv.cv_name)}
                  disabled={testLoading === cv.cv_name}
                  className={`px-3 py-1 rounded ${
                    testLoading === cv.cv_name
                      ? "bg-gray-400 text-white"
                      : "bg-green-600 text-white hover:bg-green-700"
                  }`}
                >
                  {testLoading === cv.cv_name ? "Generating Test..." : "Generate Test"}
                </button>
              </div>

              {/* Show generated skill tests */}
              {tests[cv.cv_name] && (
                <div className="mt-3 p-3 bg-green-50 rounded text-sm">
                  <p className="font-semibold">Generated Skill Tests:</p>
                  <ul className="list-decimal list-inside ml-3">
                    {tests[cv.cv_name].map((item, idx) => (
                      <li key={idx} className="mb-2">
                        <p>
                          <strong>Skill:</strong> {item.Skill}{" "}
                          {item.Confidence && `(Confidence: ${item.Confidence})`}
                        </p>
                        <p>
                          <strong>Test:</strong> {item.Test || "No test generated"}
                        </p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
