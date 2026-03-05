import type { APIRoute } from 'astro';

const API = import.meta.env.API_URL ?? 'http://localhost:8000';

export const GET: APIRoute = async ({ cookies }) => {
  const token = cookies.get('forge_token')?.value;
  if (!token) return new Response(JSON.stringify({ detail: 'Unauthorized' }), { status: 401 });

  const res = await fetch(`${API}/api/admin/instances`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const contentType = res.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    const data = await res.json();
    return new Response(JSON.stringify(data), { status: res.status, headers: { 'Content-Type': 'application/json' } });
  }
  const text = await res.text();
  return new Response(JSON.stringify({ detail: text || 'Server error' }), {
    status: res.status,
    headers: { 'Content-Type': 'application/json' },
  });
};

export const POST: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get('forge_token')?.value;
  if (!token) return new Response(JSON.stringify({ detail: 'Unauthorized' }), { status: 401 });

  const body = await request.text();
  const res = await fetch(`${API}/api/admin/instances`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body,
  });
  const contentType = res.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    const data = await res.json();
    return new Response(JSON.stringify(data), { status: res.status, headers: { 'Content-Type': 'application/json' } });
  }
  const text = await res.text();
  return new Response(JSON.stringify({ detail: text || 'Server error' }), {
    status: res.status,
    headers: { 'Content-Type': 'application/json' },
  });
};
