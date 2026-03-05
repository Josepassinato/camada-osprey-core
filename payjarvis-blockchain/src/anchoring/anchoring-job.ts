import cron from "node-cron";
import { PrismaClient } from "@prisma/client";
import { AnchoringService } from "./anchoring-service";
import { AuditEvent } from "./merkle-builder";
import { config } from "../config";

const prisma = new PrismaClient();
const anchoringService = new AnchoringService();

async function fetchPendingEvents(): Promise<AuditEvent[]> {
  const rows = await prisma.auditEvent.findMany({
    where: { anchored: false },
    orderBy: { timestamp: "asc" },
    take: 10000,
  });

  return rows.map((row) => ({
    eventId: row.id,
    agentId: row.agentId,
    action: row.action,
    timestamp: row.timestamp.getTime(),
    payload: row.payloadHash,
  }));
}

async function markEventsAnchored(eventIds: string[], anchorTxHash: string) {
  await prisma.auditEvent.updateMany({
    where: { id: { in: eventIds } },
    data: { anchored: true, anchorTxHash },
  });
}

async function runAnchoringCycle() {
  console.log(`[anchoring-job] Starting cycle at ${new Date().toISOString()}`);

  const events = await fetchPendingEvents();
  if (events.length === 0) {
    console.log("[anchoring-job] No pending events, skipping.");
    return;
  }

  const periodStart = Math.min(...events.map((e) => e.timestamp));
  const periodEnd = Math.max(...events.map((e) => e.timestamp));

  console.log(`[anchoring-job] Anchoring ${events.length} events (period: ${periodStart}-${periodEnd})`);

  const result = await anchoringService.anchorEvents(events, periodStart, periodEnd);

  console.log(`[anchoring-job] Anchored! TX: ${result.txHash}, Record #${result.recordIndex}`);

  await markEventsAnchored(
    events.map((e) => e.eventId),
    result.txHash
  );

  await prisma.anchorRecord.create({
    data: {
      txHash: result.txHash,
      recordIndex: result.recordIndex,
      merkleRoot: result.merkleRoot,
      eventCount: result.eventCount,
      periodStart: new Date(result.periodStart),
      periodEnd: new Date(result.periodEnd),
    },
  });

  console.log("[anchoring-job] Cycle complete.");
}

// Run as cron job or one-shot
if (process.argv.includes("--once")) {
  runAnchoringCycle()
    .then(() => process.exit(0))
    .catch((err) => {
      console.error("[anchoring-job] Error:", err);
      process.exit(1);
    });
} else {
  console.log(`[anchoring-job] Scheduling cron: ${config.ANCHOR_CRON}`);
  cron.schedule(config.ANCHOR_CRON, () => {
    runAnchoringCycle().catch((err) => {
      console.error("[anchoring-job] Cycle error:", err);
    });
  });
}
