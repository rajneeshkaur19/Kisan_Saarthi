const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/* Basic health‑check endpoint */
export async function checkHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error(`Health check failed with status ${res.status}`);
  return res.json();
}

/* Leaf‑diagnosis (file upload) */
export async function diagnoseLeaf(file, language = 'en') {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('language', language);

  const res = await fetch(`${API_BASE_URL}/diagnose`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

/* Mandi price lookup */
export async function getMandiPrices(crop = '', mandi = '') {
  const params = new URLSearchParams();
  if (crop) params.append('crop', crop);
  if (mandi) params.append('mandi', mandi);

  const res = await fetch(`${API_BASE_URL}/prices?${params.toString()}`);
  if (!res.ok) throw new Error(`Prices failed with status ${res.status}`);
  return res.json();
}

/* Government‑scheme eligibility check */
export async function checkEligibility(payload) {
  const res = await fetch(`${API_BASE_URL}/eligibility`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Eligibility check failed with status ${res.status}`);
  return res.json();
}

/* Download eligibility checklist (PDF) */
export async function downloadChecklist(payload) {
  const res = await fetch(`${API_BASE_URL}/checklist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Checklist download failed with status ${res.status}`);
  return res.json();
}

/* Chatbot message */
export async function sendChatMessage(message, language = 'en', history = []) {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, language, history }),
  });
  if (!res.ok) throw new Error(`Chat request failed with status ${res.status}`);
  return res.json();
}

/* Weather for a district */
export async function getWeather(district = 'ludhiana') {
  const res = await fetch(`${API_BASE_URL}/weather?district=${encodeURIComponent(district)}`);
  if (!res.ok) throw new Error(`Weather request failed with status ${res.status}`);
  return res.json();
}