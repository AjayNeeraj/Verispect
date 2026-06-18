/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",            // static export → drag web/out to Netlify (no server needed)
  images: { unoptimized: true },
  trailingSlash: true,
};
export default nextConfig;
