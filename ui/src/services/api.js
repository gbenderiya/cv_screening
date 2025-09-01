const BASE_URL = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function screenCVs(formData) {
  const res = await fetch(`${BASE_URL}/screen`, {
    method: "POST",
    body: formData
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`Backend error (${res.status}): ${txt}`);
  }
  return await res.json();
}
