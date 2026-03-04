import { defineMiddleware } from 'astro:middleware';

// Routes that require authentication and the required role
const protectedRoutes: { pattern: RegExp; role: string }[] = [
  { pattern: /^\/hackathons\/.+$/, role: 'participant' },  // individual hackathon pages require login
  { pattern: /^\/judge(\/.*)?$/, role: 'judge' },
  { pattern: /^\/admin(\/.*)?$/, role: 'admin' },
];

// Public routes — always allowed
const publicPaths = ['/', '/login', '/judge/login', '/admin/login', '/api/'];

export const onRequest = defineMiddleware(async (context, next) => {
  const { pathname } = context.url;

  // Always allow public paths and static assets
  if (
    publicPaths.some(p => pathname === p || pathname.startsWith(p)) ||
    pathname.startsWith('/_') ||
    pathname.match(/\.(ico|svg|png|jpg|css|js|woff2?)$/)
  ) {
    return next();
  }

  const token = context.cookies.get('forge_token')?.value;
  const role = context.cookies.get('forge_role')?.value;

  for (const route of protectedRoutes) {
    if (route.pattern.test(pathname)) {
      if (!token) {
        // Not logged in — redirect to appropriate login
        if (pathname.startsWith('/judge')) return context.redirect('/judge/login');
        if (pathname.startsWith('/admin')) return context.redirect('/admin/login');
        return context.redirect('/login');
      }

      if (route.role !== role) {
        // Wrong role — redirect to their home
        if (role === 'judge') return context.redirect('/judge');
        if (role === 'admin') return context.redirect('/admin');
        return context.redirect('/hackathons');
      }

      break;
    }
  }

  return next();
});
