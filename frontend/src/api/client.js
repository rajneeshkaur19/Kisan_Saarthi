const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export function normalizeLang(language = 'en') {
  const code = String(language || 'en').slice(0, 2).toLowerCase();
  return ['en', 'hi', 'pa'].includes(code) ? code : 'en';
}

async function parseJson(res) {
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const message =
      data?.error?.message || `Request failed with status ${res.status}`;
    const err = new Error(message);
    err.status = res.status;
    err.payload = data;
    throw err;
  }
  return data;
}

export async function checkHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  return parseJson(res);
}

export async function diagnoseLeaf(file, language = 'en') {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('language', normalizeLang(language));

  const res = await fetch(`${API_BASE_URL}/diagnose`, {
    method: 'POST',
    body: formData,
  });
  return parseJson(res);
}

export async function getMandiPrices(crop = 'Wheat', mandi = 'ludhiana') {
  const params = new URLSearchParams();
  if (crop) params.append('crop', crop);
  if (mandi) params.append('mandi', mandi);

  const res = await fetch(`${API_BASE_URL}/prices?${params.toString()}`);
  return parseJson(res);
}

export async function checkEligibility(payload) {
  const body = {
    ...payload,
    language: normalizeLang(payload.language),
  };
  const res = await fetch(`${API_BASE_URL}/eligibility`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return parseJson(res);
}

export async function downloadChecklist(payload) {
  const body = {
    scheme_id: payload.scheme_id,
    language: normalizeLang(payload.language),
    farmer_name: payload.farmer_name || 'Farmer',
    include_pdf_base64: payload.include_pdf_base64 !== false,
  };
  const res = await fetch(`${API_BASE_URL}/checklist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return parseJson(res);
}

export async function sendChatMessage(message, language = 'en', history = []) {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      language: normalizeLang(language),
      history,
    }),
  });
  return parseJson(res);
}

export async function getWeather(district = 'ludhiana') {
  const res = await fetch(
    `${API_BASE_URL}/weather?district=${encodeURIComponent(district)}`
  );
  return parseJson(res);
}
