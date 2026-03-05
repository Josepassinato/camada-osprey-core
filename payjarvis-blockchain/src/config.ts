import { z } from "zod";
import "dotenv/config";

const envSchema = z.object({
  // Database
  DATABASE_URL: z.string().url(),

  // Blockchain
  DEPLOYER_PRIVATE_KEY: z.string().min(64),
  POLYGON_RPC_URL: z.string().url().default("https://polygon-rpc.com"),
  AMOY_RPC_URL: z.string().url().default("https://rpc-amoy.polygon.technology"),
  REGISTRY_CONTRACT_ADDRESS: z.string().startsWith("0x"),
  ANCHORING_CONTRACT_ADDRESS: z.string().startsWith("0x"),

  // API
  API_PORT: z.coerce.number().default(3100),
  API_HOST: z.string().default("0.0.0.0"),

  // Anchoring
  ANCHOR_CRON: z.string().default("0 */6 * * *"), // every 6 hours
  ANCHOR_CHAIN: z.enum(["polygon", "amoy"]).default("amoy"),
  PERIOD_SALT: z.string().min(16),

  // Credentials
  ISSUER_DID: z.string().startsWith("did:"),
  ISSUER_PRIVATE_KEY_HEX: z.string().min(64),

  // Security
  API_KEY: z.string().min(32),

  // Environment
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
});

export type Env = z.infer<typeof envSchema>;

function loadConfig(): Env {
  const result = envSchema.safeParse(process.env);
  if (!result.success) {
    console.error("Invalid environment configuration:");
    console.error(result.error.format());
    process.exit(1);
  }
  return result.data;
}

export const config = loadConfig();
