import { FastifyInstance } from "fastify";
import { z } from "zod";
import { VCIssuer } from "../../credentials/vc-issuer";

const vcIssuer = new VCIssuer();

const issueCredentialSchema = z.object({
  id: z.string(),
  agentName: z.string(),
  vendor: z.string(),
  certificationLevel: z.string(),
  registeredAt: z.string(),
  capabilities: z.array(z.string()),
  expiresInDays: z.number().default(365),
});

const issueAnchorProofSchema = z.object({
  txHash: z.string(),
  merkleRoot: z.string(),
  eventCount: z.number(),
  periodStart: z.string(),
  periodEnd: z.string(),
});

export async function credentialsRoutes(app: FastifyInstance) {
  // Issue a Verifiable Credential for an agent
  app.post("/issue/agent", async (request, reply) => {
    const body = issueCredentialSchema.parse(request.body);
    const { expiresInDays, ...subject } = body;

    const vc = await vcIssuer.issueAgentCredential(subject, expiresInDays);
    return reply.code(201).send(vc);
  });

  // Issue an Anchor Proof VC
  app.post("/issue/anchor-proof", async (request, reply) => {
    const body = issueAnchorProofSchema.parse(request.body);

    const jwt = await vcIssuer.issueAnchorProofCredential(
      body.txHash,
      body.merkleRoot,
      body.eventCount,
      body.periodStart,
      body.periodEnd
    );

    return reply.code(201).send({ jwt });
  });
}
