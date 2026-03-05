import cron from "node-cron";
import { AnchoringService } from "./anchoring-service";

const anchoringService = new AnchoringService();
const ANCHOR_CRON = process.env.ANCHOR_CRON || "0 */6 * * *";
const PERIOD_HOURS = parseInt(process.env.ANCHOR_PERIOD_HOURS || "6", 10);

async function runAnchoringCycle() {
  const now = new Date();
  const periodEnd = now;
  const periodStart = new Date(now.getTime() - PERIOD_HOURS * 60 * 60 * 1000);

  console.log(`[anchoring-job] Starting cycle at ${now.toISOString()}`);
  console.log(`[anchoring-job] Period: ${periodStart.toISOString()} → ${periodEnd.toISOString()}`);

  await anchoringService.anchorPeriod(periodStart, periodEnd);

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
  console.log(`[anchoring-job] Scheduling cron: ${ANCHOR_CRON}`);
  cron.schedule(ANCHOR_CRON, () => {
    runAnchoringCycle().catch((err) => {
      console.error("[anchoring-job] Cycle error:", err);
    });
  });
}
