import type { APIRoute } from 'astro';

const API = import.meta.env.API_URL ?? 'http://localhost:8000';

export const POST: APIRoute = async ({ request, cookies, params }) => {
  const token = cookies.get('forge_token')?.value;
  if (!token) {
    return new Response(JSON.stringify({ detail: 'Unauthorized' }), { status: 401 });
  }

  const body = await request.json();

  const res = await fetch(`${API}/api/hackathons/${params.id}/unlock`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();
  return new Response(JSON.stringify(data), {
    status: res.status,
    headers: { 'Content-Type': 'application/json' },
  });
};
