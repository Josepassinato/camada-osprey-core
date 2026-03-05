import { AgentMetadata } from "./registry-service";

export interface CertificationResult {
  eligible: boolean;
  level: "basic" | "standard" | "premium";
  reason: string;
  checks: CriteriaCheck[];
}

export interface CriteriaCheck {
  name: string;
  passed: boolean;
  detail: string;
}

const REQUIRED_FIELDS: (keyof AgentMetadata)[] = ["name", "version", "vendor", "capabilities"];

export function evaluateAgent(metadata: AgentMetadata): CertificationResult {
  const checks: CriteriaCheck[] = [];

  // Check required fields
  for (const field of REQUIRED_FIELDS) {
    const value = metadata[field];
    const passed = value !== undefined && value !== null && value !== "";
    checks.push({
      name: `field_${field}`,
      passed,
      detail: passed ? `${field} is present` : `${field} is missing or empty`,
    });
  }

  // Check capabilities
  const hasCaps = Array.isArray(metadata.capabilities) && metadata.capabilities.length > 0;
  checks.push({
    name: "has_capabilities",
    passed: hasCaps,
    detail: hasCaps
      ? `${metadata.capabilities.length} capabilities declared`
      : "No capabilities declared",
  });

  // Check version format (semver-like)
  const semverRegex = /^\d+\.\d+\.\d+/;
  const validVersion = semverRegex.test(metadata.version || "");
  checks.push({
    name: "valid_version",
    passed: validVersion,
    detail: validVersion ? "Version follows semver" : "Version does not follow semver format",
  });

  // Determine eligibility
  const allPassed = checks.every((c) => c.passed);
  if (!allPassed) {
    const failed = checks.filter((c) => !c.passed).map((c) => c.name);
    return {
      eligible: false,
      level: "basic",
      reason: `Failed checks: ${failed.join(", ")}`,
      checks,
    };
  }

  // Determine level based on capabilities count
  const capCount = metadata.capabilities.length;
  let level: CertificationResult["level"] = "basic";
  if (capCount >= 10) level = "premium";
  else if (capCount >= 5) level = "standard";

  return {
    eligible: true,
    level,
    reason: `Agent meets ${level} certification criteria`,
    checks,
  };
}
