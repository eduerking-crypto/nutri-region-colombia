import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // cacheComponents desactivado deliberadamente: la app es intensivamente
  // client-side (hooks de navegacion en paginas cliente) y esta fase prioriza
  // simplicidad sobre el caching granular de Next 16.
  cacheComponents: false,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8400/api/:path*",
      },
    ];
  },
};

export default nextConfig;
