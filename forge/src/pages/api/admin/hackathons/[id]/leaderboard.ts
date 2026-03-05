import type { APIRoute } from 'astro';

const API = import.meta.env.API_URL ?? 'http://localhost:8000';

export const PATCH: APIRoute = async ({ cookies, params }) => {
  const token = cookies.get('forge_token')?.value;
  if (!token) return new Response(JSON.stringify({ detail: 'Unauthorized' }), { status: 401 });

  const res = await fetch(`${API}/api/admin/hackathons/${params.id}/leaderboard`, {
    method: 'PATCH',
    headers: { Authorization: `Bearer ${token}` },
  });
  const contentType = res.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    const data = await res.json();
    return new Response(JSON.stringify(data), { status: res.status, headers: { 'Content-Type': 'application/json' } });
  }
  return new Response(null, { status: res.status });
};
