import { createJWT, ES256KSigner } from "did-jwt";
import { PrismaClient } from "@prisma/client";
import { randomUUID } from "crypto";

const prisma = new PrismaClient();

export interface AgentCredentialPayload {
  botId: string;
  agentPublicId: string;
  certifiedAt: string;
}

export class VCIssuer {
  private signer: ReturnType<typeof ES256KSigner>;
  private issuerDid: string;

  constructor() {
    this.issuerDid = process.env.ISSUER_DID!;
    const privateKeyBytes = Buffer.from(process.env.ISSUER_PRIVATE_KEY_HEX!, "hex");
    this.signer = ES256KSigner(privateKeyBytes);
  }

  async issueAgentCredential(
    payload: AgentCredentialPayload,
    expiresInDays: number = 365
  ): Promise<{ jwt: string; credentialId: string }> {
    const now = new Date();
    const expiresAt = new Date(now.getTime() + expiresInDays * 24 * 60 * 60 * 1000);
    const credentialId = randomUUID();

    const vcPayload = {
      sub: payload.botId,
      vc: {
        "@context": [
          "https://www.w3.org/2018/credentials/v1",
          "https://payjarvis.io/credentials/v1",
        ],
        type: ["VerifiableCredential", "PayJarvisAgentCertification"],
        credentialSubject: {
          id: payload.botId,
          agentPublicId: payload.agentPublicId,
          certifiedAt: payload.certifiedAt,
        },
        issuanceDate: now.toISOString(),
        expirationDate: expiresAt.toISOString(),
      },
    };

    const jwt = await createJWT(vcPayload, {
      issuer: this.issuerDid,
      signer: this.signer,
    });

    // Find the VerifiedAgent and link the credential
    const agent = await prisma.verifiedAgent.findUnique({
      where: { botId: payload.botId },
    });

    if (agent) {
      await prisma.agentCredential.create({
        data: {
          agentId: agent.id,
          credentialId,
          credential: vcPayload,
          expiresAt,
        },
      });
    }

    return { jwt, credentialId };
  }

  async issueAnchorProofCredential(
    txHash: string,
    merkleRoot: string,
    eventCount: number,
    periodStart: string,
    periodEnd: string
  ): Promise<string> {
    const vcPayload = {
      sub: txHash,
      vc: {
        "@context": [
          "https://www.w3.org/2018/credentials/v1",
          "https://payjarvis.io/credentials/v1",
        ],
        type: ["VerifiableCredential", "PayJarvisAnchorProof"],
        credentialSubject: {
          id: txHash,
          merkleRoot,
          eventCount,
          periodStart,
          periodEnd,
        },
        issuanceDate: new Date().toISOString(),
      },
    };

    return createJWT(vcPayload, {
      issuer: this.issuerDid,
      signer: this.signer,
    });
  }
}
