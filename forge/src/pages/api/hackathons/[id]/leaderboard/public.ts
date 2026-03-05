import type { APIRoute } from 'astro';

const API = import.meta.env.API_URL ?? 'http://localhost:8000';

export const GET: APIRoute = async ({ params }) => {
  const res = await fetch(`${API}/api/hackathons/${params.id}/leaderboard/public`);
  const contentType = res.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    const data = await res.json();
    return new Response(JSON.stringify(data), { status: res.status, headers: { 'Content-Type': 'application/json' } });
  }
  return new Response(JSON.stringify({ detail: 'Server error' }), { status: res.status, headers: { 'Content-Type': 'application/json' } });
};
