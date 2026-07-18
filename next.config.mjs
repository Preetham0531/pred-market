import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

/** @type {import('next').NextConfig} */
const nextConfig = {
  turbopack: {
    root: __dirname
  },
  async rewrites() {
    if (process.env.NEXT_PUBLIC_USE_MOCK_DATA !== "false") return [];
    return {
      beforeFiles: [
        {
          source: "/api/v1/:path*",
          destination: "http://127.0.0.1:8010/api/v1/:path*"
        }
      ]
    };
  }
};

export default nextConfig;
