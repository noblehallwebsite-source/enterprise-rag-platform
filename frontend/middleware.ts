import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
    // Only run this logic if the browser is hitting an /api/ route
    if (request.nextUrl.pathname.startsWith('/api/')) {

        // Clone the incoming browser headers
        const requestHeaders = new Headers(request.headers);

        // 🔒 SECURE SERVER-SIDE INJECTION:
        // Pulls BACKEND_API_KEY from your container's environment variables.
        // Make sure "X-API-Key" matches exactly what your FastAPI authorize_request checks for!
        requestHeaders.set('X-API-Key', process.env.BACKEND_API_KEY || '');

        // Forward the request to Nginx with the secret header safely pinned to it
        return NextResponse.next({
            request: {
                headers: requestHeaders,
            },
        });
    }
}

export const config = {
    // Tells Next.js to only run the middleware on API route requests
    matcher: '/api/:path*',
};