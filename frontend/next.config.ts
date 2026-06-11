import type { NextConfig } from "next";

// Avoid OneDrive sync conflicts with the default `.next` folder name
const nextConfig: NextConfig = {
  reactStrictMode: true,
  distDir: ".next-local",
};

export default nextConfig;