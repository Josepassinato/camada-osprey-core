import { FastifyInstance } from "fastify";
import { z } from "zod";
import { AnchoringService } from "../../anchoring/anchoring-service";
import { buildMerkleTree, getProof, verifyProof, AuditEvent } from "../../anchoring/merkle-builder";

const anchoringService = new AnchoringService();

const anchorRequestSchema = z.object({
  events: z.array(z.object({
    eventId: z.string(),
    agentId: z.string(),
    action: z.string(),
    timestamp: z.number(),
    payload: z.string(),
  })).min(1),
  periodStart: z.number(),
  periodEnd: z.number(),
  schemaVersion: z.number().default(1),
  issuerId: z.string().optional(),
});

const verifyRequestSchema = z.object({
  event: z.object({
    eventId: z.string(),
    agentId: z.string(),
    action: z.string(),
    timestamp: z.number(),
    payload: z.string(),
  }),
  proof: z.array(z.string()),
  merkleRoot: z.string(),
});

export async function proofsRoutes(app: FastifyInstance) {
  // Anchor events on-chain
  app.post("/anchor", async (request, reply) => {
    const body = anchorRequestSchema.parse(request.body);

    const result = await anchoringService.anchorEvents(
      body.events,
      body.periodStart,
      body.periodEnd,
      body.schemaVersion,
      body.issuerId
    );

    return reply.code(201).send(result);
  });

  // Build merkle tree and return root + proofs (off-chain)
  app.post("/merkle", async (request, reply) => {
    const body = z.object({
      events: z.array(z.object({
        eventId: z.string(),
        agentId: z.string(),
        action: z.string(),
        timestamp: z.number(),
        payload: z.string(),
      })).min(1),
    }).parse(request.body);

    const { tree, root, leaves } = buildMerkleTree(body.events);

    const proofs = body.events.map((event) => ({
      eventId: event.eventId,
      proof: getProof(tree, event),
    }));

    return { root, leaves, proofs };
  });

  // Verify a single event proof off-chain
  app.post("/verify", async (request, reply) => {
    const body = verifyRequestSchema.parse(request.body);
    const { tree } = buildMerkleTree([body.event]);
    const valid = verifyProof(tree, body.event, body.proof, body.merkleRoot);
    return { valid };
  });

  // Get on-chain record by index
  app.get<{ Params: { index: string } }>("/:index", async (request, reply) => {
    const index = parseInt(request.params.index, 10);
    if (isNaN(index)) return reply.code(400).send({ error: "Invalid index" });

    const record = await anchoringService.getRecord(index);
    return record;
  });

  // Get latest on-chain record
  app.get("/latest", async () => {
    return anchoringService.getLatestRecord();
  });

  // Get total records count
  app.get("/count", async () => {
    const total = await anchoringService.totalRecords();
    return { total };
  });
}
