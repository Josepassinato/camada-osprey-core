import { FastifyInstance } from "fastify";
import { z } from "zod";
import { RegistryService } from "../../registry/registry-service";

const registryService = new RegistryService();

const registerAgentSchema = z.object({
  name: z.string().min(1),
  version: z.string().regex(/^\d+\.\d+\.\d+/),
  vendor: z.string().min(1),
  capabilities: z.array(z.string()).min(1),
  certificationLevel: z.string().default("basic"),
});

const revokeAgentSchema = z.object({
  name: z.string().min(1),
  vendor: z.string().min(1),
  reasonCode: z.string().min(1),
});

export async function agentsRoutes(app: FastifyInstance) {
  // Register a new agent on-chain
  app.post("/register", async (request, reply) => {
    const body = registerAgentSchema.parse(request.body);

    const result = await registryService.registerAgent(body);
    return reply.code(201).send(result);
  });

  // Revoke an agent
  app.post("/revoke", async (request, reply) => {
    const body = revokeAgentSchema.parse(request.body);

    const txHash = await registryService.revokeAgent(
      body.name,
      body.vendor,
      body.reasonCode
    );

    return { txHash, revoked: true };
  });

  // Check if agent is active
  app.get<{ Querystring: { name: string; vendor: string } }>(
    "/active",
    async (request, reply) => {
      const { name, vendor } = request.query;
      if (!name || !vendor) {
        return reply.code(400).send({ error: "name and vendor are required" });
      }

      const active = await registryService.isAgentActive(name, vendor);
      return { active };
    }
  );

  // Get agent details
  app.get<{ Querystring: { name: string; vendor: string } }>(
    "/details",
    async (request, reply) => {
      const { name, vendor } = request.query;
      if (!name || !vendor) {
        return reply.code(400).send({ error: "name and vendor are required" });
      }

      const agent = await registryService.getAgent(name, vendor);
      return agent;
    }
  );
}
