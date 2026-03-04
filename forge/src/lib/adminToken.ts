const API = import.meta.env.API_URL ?? 'http://localhost:8000';
const ADMIN_USERNAME = import.meta.env.ADMIN_USERNAME;
const ADMIN_PASSWORD = import.meta.env.ADMIN_PASSWORD;

let cachedToken: string | null = null;
let tokenExpiresAt = 0;

export async function getAdminToken(): Promise<string | null> {
  if (!ADMIN_USERNAME || !ADMIN_PASSWORD) return null;

  // Return cached token if still valid (with 60s buffer)
  if (cachedToken && Date.now() < tokenExpiresAt - 60_000) {
    return cachedToken;
  }

  try {
    const res = await fetch(`${API}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: ADMIN_USERNAME, password: ADMIN_PASSWORD, role: 'admin' }),
    });
    if (!res.ok) return null;
    const data = await res.json();
    cachedToken = data.access_token;
    // Tokens last 12h; cache for 11h
    tokenExpiresAt = Date.now() + 11 * 60 * 60 * 1000;
    return cachedToken;
  } catch {
    return null;
  }
}
