import type { APIRoute } from 'astro';

const API = import.meta.env.API_URL ?? 'http://localhost:8000';

async function proxyRequest(method: string, url: string, token: string, body?: string) {
  const headers: Record<string, string> = { Authorization: `Bearer ${token}` };
  if (body) headers['Content-Type'] = 'application/json';
  const res = await fetch(url, { method, headers, body });
  if (res.status === 204 || res.headers.get('content-length') === '0') {
    return new Response(null, { status: res.status });
  }
  const contentType = res.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    const data = await res.json();
    return new Response(JSON.stringify(data), { status: res.status, headers: { 'Content-Type': 'application/json' } });
  }
  const text = await res.text();
  if (!text) return new Response(null, { status: res.status });
  return new Response(JSON.stringify({ detail: text }), {
    status: res.status,
    headers: { 'Content-Type': 'application/json' },
  });
}

export const PUT: APIRoute = async ({ request, cookies, params }) => {
  const token = cookies.get('forge_token')?.value;
  if (!token) return new Response(JSON.stringify({ detail: 'Unauthorized' }), { status: 401 });
  return proxyRequest('PUT', `${API}/api/admin/instances/${params.id}`, token, await request.text());
};

export const DELETE: APIRoute = async ({ cookies, params }) => {
  const token = cookies.get('forge_token')?.value;
  if (!token) return new Response(JSON.stringify({ detail: 'Unauthorized' }), { status: 401 });
  return proxyRequest('DELETE', `${API}/api/admin/instances/${params.id}`, token);
};
