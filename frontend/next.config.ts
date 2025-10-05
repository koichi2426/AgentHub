import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  
  // Dockerの本番環境向けビルドを有効にするためにこの行を追加します。
  output: "standalone",
};

export default nextConfig;