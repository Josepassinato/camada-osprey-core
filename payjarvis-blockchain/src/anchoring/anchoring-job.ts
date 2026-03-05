import cron from "node-cron";
import { randomBytes } from "crypto";
import { PrismaClient } from "@prisma/client";
import { AnchoringService } from "./anchoring-service";
import { DecisionLeaf } from "./merkle-builder";
import { config } from "../config";

const prisma = new PrismaClient();
const anchoringService = new AnchoringService();

async function fetchPendingDecisions(): Promise<DecisionLeaf[]> {
  const rows = await prisma.decisionEvent.findMany({
    where: { anchored: false },
    orderBy: { timestamp: "asc" },
    take: 10000,
  });

  return rows.map((row) => ({
    decisionId: row.id,
    botId: row.botId,
    merchantId: row.merchantId,
    amount: row.amount.toNumber(),
    currency: row.currency,
    decision: row.decision as DecisionLeaf["decision"],
    timestamp: row.timestamp.getTime(),
    policyId: row.policyId ?? undefined,
  }));
}

async function markDecisionsAnchored(decisionIds: string[], anchorTxHash: string) {
  await prisma.decisionEvent.updateMany({
    where: { id: { in: decisionIds } },
    data: { anchored: true, anchorTxHash },
  });
}

function generatePeriodSalt(): string {
  return randomBytes(32).toString("hex");
}

async function runAnchoringCycle() {
  console.log(`[anchoring-job] Starting cycle at ${new Date().toISOString()}`);

  const decisions = await fetchPendingDecisions();
  if (decisions.length === 0) {
    console.log("[anchoring-job] No pending decisions, skipping.");
    return;
  }

  const periodStart = Math.min(...decisions.map((d) => d.timestamp));
  const periodEnd = Math.max(...decisions.map((d) => d.timestamp));
  const periodSalt = config.PERIOD_SALT || generatePeriodSalt();

  console.log(`[anchoring-job] Anchoring ${decisions.length} decisions (period: ${periodStart}-${periodEnd})`);

  const result = await anchoringService.anchorDecisions(
    decisions,
    periodStart,
    periodEnd,
    periodSalt
  );

  console.log(`[anchoring-job] Anchored! TX: ${result.txHash}, Record #${result.recordIndex}`);

  await markDecisionsAnchored(
    decisions.map((d) => d.decisionId),
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
      periodSalt,
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
