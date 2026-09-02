import type { NextConfig } from "next";

// Server-side only: where the real FastAPI backend actually lives.
// Not exposed to the browser - the browser only ever calls this app's own
// origin at /api/*, which Next.js proxies to this URL. That keeps the
// httpOnly access_token cookie same-origin from the browser's point of
// view, which matters because the backend does not currently configure
// CORS for credentialed cross-origin requests.
const BACKEND_API_URL = process.env.BACKEND_API_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_API_URL}/:path*`,
      },
    ];
  },
};

export default nextConfig;
