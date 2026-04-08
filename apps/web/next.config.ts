import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Images from the API media server
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/media/**",
      },
    ],
  },
};

export default nextConfig;
