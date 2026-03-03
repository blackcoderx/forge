import type { APIRoute } from 'astro';

const API = import.meta.env.API_URL ?? 'http://localhost:8000';

async function proxyToBackend(request: Request, cookies: any, params: any, method: string) {
  const token = cookies.get('forge_token')?.value;
  if (!token) {
    return new Response(JSON.stringify({ detail: 'Unauthorized' }), { status: 401 });
  }

  const url = new URL(request.url);
  const backendUrl = `${API}/api/scores/${params.team_id}${url.search}`;

  const options: RequestInit = {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  };

  if (method !== 'GET') {
    options.body = await request.text();
  }

  const res = await fetch(backendUrl, options);
  const data = await res.json();
  return new Response(JSON.stringify(data), {
    status: res.status,
    headers: { 'Content-Type': 'application/json' },
  });
}

export const GET: APIRoute = ({ request, cookies, params }) =>
  proxyToBackend(request, cookies, params, 'GET');

export const POST: APIRoute = ({ request, cookies, params }) =>
  proxyToBackend(request, cookies, params, 'POST');

export const PUT: APIRoute = ({ request, cookies, params }) =>
  proxyToBackend(request, cookies, params, 'PUT');
