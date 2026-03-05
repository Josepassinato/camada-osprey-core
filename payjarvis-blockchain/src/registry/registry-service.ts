import { ethers } from "ethers";
import { config } from "../config";
import { CertificationCriteria, evaluateAgent } from "./certification-criteria";

const REGISTRY_ABI = [
  "function registerAgent(bytes32 agentPublicId, bytes32 metadataHash) external",
  "function revokeAgent(bytes32 agentPublicId, string calldata reasonCode) external",
  "function isAgentActive(bytes32 agentPublicId) external view returns (bool)",
  "function getAgent(bytes32 agentPublicId) external view returns (bool active, uint256 registeredAt, uint256 revokedAt, bytes32 metadataHash, string reasonCode)",
];

export interface AgentMetadata {
  name: string;
  version: string;
  vendor: string;
  capabilities: string[];
  certificationLevel: string;
}

export interface AgentRecord {
  active: boolean;
  registeredAt: Date;
  revokedAt: Date | null;
  metadataHash: string;
  reasonCode: string;
}

export class RegistryService {
  private contract: ethers.Contract;
  private signer: ethers.Wallet;

  constructor() {
    const rpcUrl = config.ANCHOR_CHAIN === "polygon"
      ? config.POLYGON_RPC_URL
      : config.AMOY_RPC_URL;

    const provider = new ethers.JsonRpcProvider(rpcUrl);
    this.signer = new ethers.Wallet(config.DEPLOYER_PRIVATE_KEY, provider);
    this.contract = new ethers.Contract(
      config.REGISTRY_CONTRACT_ADDRESS,
      REGISTRY_ABI,
      this.signer
    );
  }

  private computeAgentId(agentName: string, vendor: string): string {
    return ethers.keccak256(
      ethers.toUtf8Bytes(`${vendor}:${agentName}`)
    );
  }

  private computeMetadataHash(metadata: AgentMetadata): string {
    return ethers.keccak256(
      ethers.toUtf8Bytes(JSON.stringify(metadata))
    );
  }

  async registerAgent(metadata: AgentMetadata): Promise<{ txHash: string; agentId: string }> {
    const criteria = evaluateAgent(metadata);
    if (!criteria.eligible) {
      throw new Error(`Agent does not meet certification criteria: ${criteria.reason}`);
    }

    const agentId = this.computeAgentId(metadata.name, metadata.vendor);
    const metadataHash = this.computeMetadataHash(metadata);

    const tx = await this.contract.registerAgent(agentId, metadataHash);
    const receipt = await tx.wait();

    return { txHash: receipt.hash, agentId };
  }

  async revokeAgent(agentName: string, vendor: string, reasonCode: string): Promise<string> {
    const agentId = this.computeAgentId(agentName, vendor);
    const tx = await this.contract.revokeAgent(agentId, reasonCode);
    const receipt = await tx.wait();
    return receipt.hash;
  }

  async isAgentActive(agentName: string, vendor: string): Promise<boolean> {
    const agentId = this.computeAgentId(agentName, vendor);
    return this.contract.isAgentActive(agentId);
  }

  async getAgent(agentName: string, vendor: string): Promise<AgentRecord> {
    const agentId = this.computeAgentId(agentName, vendor);
    const [active, registeredAt, revokedAt, metadataHash, reasonCode] =
      await this.contract.getAgent(agentId);

    return {
      active,
      registeredAt: new Date(Number(registeredAt) * 1000),
      revokedAt: Number(revokedAt) > 0 ? new Date(Number(revokedAt) * 1000) : null,
      metadataHash,
      reasonCode,
    };
  }
}
