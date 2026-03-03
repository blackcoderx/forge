import type { APIRoute } from 'astro';

export const GET: APIRoute = ({ cookies, redirect }) => {
  cookies.delete('forge_token', { path: '/' });
  cookies.delete('forge_role', { path: '/' });
  return redirect('/');
};
