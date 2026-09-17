import type { NextConfig } from "next";

// Fail the build before a privileged database credential reaches browser bundles.
const publicKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
let publicKeyRole: string | undefined;
try {
  publicKeyRole = JSON.parse(Buffer.from(publicKey.split('.')[1] || '', 'base64url').toString()).role;
} catch { /* Publishable keys are not JWTs. */ }
if (publicKey.startsWith('sb_secret_') || (publicKeyRole && publicKeyRole !== 'anon')) {
  throw new Error('NEXT_PUBLIC_SUPABASE_ANON_KEY must be a publishable or anon key, never a server secret.');
}

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;
