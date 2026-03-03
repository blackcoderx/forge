import type { APIRoute } from 'astro';

const API = import.meta.env.API_URL ?? 'http://localhost:8000';

export const DELETE: APIRoute = async ({ cookies, params }) => {
  const token = cookies.get('forge_token')?.value;
  if (!token) return new Response(JSON.stringify({ detail: 'Unauthorized' }), { status: 401 });

  const res = await fetch(`${API}/api/admin/judges/${params.id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  });
  return new Response(null, { status: res.status });
};
