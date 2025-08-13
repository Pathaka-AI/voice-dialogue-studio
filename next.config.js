/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable audio file handling
  webpack: (config) => {
    config.module.rules.push({
      test: /\.(wav|mp3|m4a)$/,
      use: {
        loader: 'file-loader',
        options: {
          publicPath: '/_next/static/audio/',
          outputPath: 'static/audio/',
        },
      },
    });
    return config;
  },
  // Production optimizations
  poweredByHeader: false,
  reactStrictMode: true,
  images: {
    formats: ['image/webp', 'image/avif'],
  },
  // API configuration for backend integration
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: 'http://localhost:8000/:path*',
      },
    ];
  },
};

module.exports = nextConfig; 