import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  
  // Dockerの本番環境向けビルドを有効にするためにこの行を追加します。
  output: "standalone",

  // ★ ここから追記
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'picsum.photos',
        port: '',
        pathname: '/**',
      },
    ],
  },
  // ★ ここまで
};

export default nextConfig;