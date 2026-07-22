import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  turbopack: {
    root: __dirname
  },
  async rewrites() {
    if (process.env.NEXT_PUBLIC_USE_MOCK_DATA !== "false") return [];
    const internalApiBaseUrl = process.env.INTERNAL_API_BASE_URL || "http://127.0.0.1:8010";
    return {
      beforeFiles: [
        {
          source: "/api/v1/:path*",
          destination: `${internalApiBaseUrl}/api/v1/:path*`
        }
      ]
    };
  }
};

export default nextConfig;
