import type { APIRoute } from 'astro';

const API = import.meta.env.API_URL ?? 'http://localhost:8000';

export const POST: APIRoute = async ({ request, cookies, redirect }) => {
  const formData = await request.formData();
  const username = formData.get('username')?.toString().trim() ?? '';
  const password = formData.get('password')?.toString() ?? '';
  const role = formData.get('role')?.toString() ?? 'participant';

  try {
    const res = await fetch(`${API}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, role }),
    });

    if (!res.ok) {
      const loginPage = role === 'judge' ? '/judge/login' : role === 'admin' ? '/admin/login' : '/login';
      return redirect(`${loginPage}?error=invalid`);
    }

    const data = await res.json();

    cookies.set('forge_token', data.access_token, {
      path: '/',
      httpOnly: true,
      secure: import.meta.env.PROD,
      sameSite: 'lax',
      maxAge: 60 * 60 * 12, // 12 hours
    });

    cookies.set('forge_role', data.role, {
      path: '/',
      httpOnly: false,
      secure: import.meta.env.PROD,
      sameSite: 'lax',
      maxAge: 60 * 60 * 12,
    });

    // Redirect based on role
    if (data.role === 'judge') return redirect('/judge');
    if (data.role === 'admin') return redirect('/admin');
    return redirect('/hackathons');

  } catch {
    const loginPage = role === 'judge' ? '/judge/login' : '/login';
    return redirect(`${loginPage}?error=invalid`);
  }
};
