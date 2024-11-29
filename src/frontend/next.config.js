/** @type {import('next').NextConfig} */

const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination:
          process.env.NODE_ENV === "development"
            ? `${process.env.NEXT_PUBLIC_API_URL}/:path*`
            : "/api/:path*",
      },
      {
        source: "/docs",
        destination:
          process.env.NODE_ENV === "development"
            ? `${process.env.NEXT_PUBLIC_API_URL}/docs`
            : "/api/docs",
      },
      {
        source: "/redoc",
        destination:
          process.env.NODE_ENV === "development"
            ? `${process.env.NEXT_PUBLIC_API_URL}/redoc`
            : "/api/docs",
      },
      {
        source: "/openapi.json",
        destination:
          process.env.NODE_ENV === "development"
            ? `${process.env.NEXT_PUBLIC_API_URL}/openapi.json`
            : "/api/openapi.json",
      },
    ];
  },
};

module.exports = nextConfig;
