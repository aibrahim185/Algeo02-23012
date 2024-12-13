/** @type {import('next').NextConfig} */

const nextConfig = {
  reactStrictMode: false,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
      {
        source: "/docs",
        destination: `${process.env.NEXT_PUBLIC_API_URL}/docs`,
      },
      {
        source: "/redoc",
        destination: `${process.env.NEXT_PUBLIC_API_URL}/redoc`,
      },
      {
        source: "/openapi.json",
        destination: `${process.env.NEXT_PUBLIC_API_URL}/openapi.json`,
      },
    ];
  },
};

module.exports = nextConfig;
