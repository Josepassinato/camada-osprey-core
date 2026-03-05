import { createJWT, ES256KSigner } from "did-jwt";
import { config } from "../config";

export interface CredentialSubject {
  id: string;
  agentName: string;
  vendor: string;
  certificationLevel: string;
  registeredAt: string;
  capabilities: string[];
}

export interface VerifiableCredential {
  jwt: string;
  decoded: {
    iss: string;
    sub: string;
    vc: {
      "@context": string[];
      type: string[];
      credentialSubject: CredentialSubject;
      issuanceDate: string;
      expirationDate?: string;
    };
  };
}

export class VCIssuer {
  private signer: ReturnType<typeof ES256KSigner>;
  private issuerDid: string;

  constructor() {
    this.issuerDid = config.ISSUER_DID;
    const privateKeyBytes = Buffer.from(config.ISSUER_PRIVATE_KEY_HEX, "hex");
    this.signer = ES256KSigner(privateKeyBytes);
  }

  async issueAgentCredential(
    subject: CredentialSubject,
    expiresInDays: number = 365
  ): Promise<VerifiableCredential> {
    const now = new Date();
    const expiration = new Date(now.getTime() + expiresInDays * 24 * 60 * 60 * 1000);

    const vcPayload = {
      sub: subject.id,
      vc: {
        "@context": [
          "https://www.w3.org/2018/credentials/v1",
          "https://payjarvis.io/credentials/v1",
        ],
        type: ["VerifiableCredential", "PayJarvisAgentCertification"],
        credentialSubject: subject,
        issuanceDate: now.toISOString(),
        expirationDate: expiration.toISOString(),
      },
    };

    const jwt = await createJWT(vcPayload, {
      issuer: this.issuerDid,
      signer: this.signer,
    });

    return {
      jwt,
      decoded: {
        iss: this.issuerDid,
        sub: subject.id,
        vc: vcPayload.vc,
      },
    };
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
          chain: config.ANCHOR_CHAIN,
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
