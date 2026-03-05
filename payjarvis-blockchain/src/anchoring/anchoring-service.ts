import { ethers } from "ethers";
import { buildMerkleTree, AuditEvent } from "./merkle-builder";
import { config } from "../config";

const ANCHORING_ABI = [
  "function anchorRoot(bytes32 merkleRoot, uint256 periodStart, uint256 periodEnd, uint256 eventCount, uint8 schemaVersion, string calldata issuerId) external returns (uint256 index)",
  "function getRecord(uint256 index) external view returns (tuple(bytes32 merkleRoot, uint256 periodStart, uint256 periodEnd, uint256 eventCount, uint8 schemaVersion, string issuerId, uint256 timestamp))",
  "function getLatestRecord() external view returns (tuple(bytes32 merkleRoot, uint256 periodStart, uint256 periodEnd, uint256 eventCount, uint8 schemaVersion, string issuerId, uint256 timestamp), uint256 index)",
  "function totalRecords() external view returns (uint256)",
];

export interface AnchorResult {
  txHash: string;
  recordIndex: number;
  merkleRoot: string;
  eventCount: number;
  periodStart: number;
  periodEnd: number;
}

export class AnchoringService {
  private contract: ethers.Contract;
  private signer: ethers.Wallet;

  constructor() {
    const rpcUrl = config.ANCHOR_CHAIN === "polygon"
      ? config.POLYGON_RPC_URL
      : config.AMOY_RPC_URL;

    const provider = new ethers.JsonRpcProvider(rpcUrl);
    this.signer = new ethers.Wallet(config.DEPLOYER_PRIVATE_KEY, provider);
    this.contract = new ethers.Contract(
      config.ANCHORING_CONTRACT_ADDRESS,
      ANCHORING_ABI,
      this.signer
    );
  }

  async anchorEvents(
    events: AuditEvent[],
    periodStart: number,
    periodEnd: number,
    schemaVersion: number = 1,
    issuerId: string = config.ISSUER_DID
  ): Promise<AnchorResult> {
    const { root } = buildMerkleTree(events);

    const tx = await this.contract.anchorRoot(
      root,
      periodStart,
      periodEnd,
      events.length,
      schemaVersion,
      issuerId
    );

    const receipt = await tx.wait();

    const event = receipt.logs.find(
      (log: ethers.Log) => log.topics[0] === ethers.id(
        "RootAnchored(uint256,bytes32,uint256,uint256,uint256,uint256)"
      )
    );

    const recordIndex = event
      ? parseInt(event.topics[1], 16)
      : (await this.contract.totalRecords()).toNumber() - 1;

    return {
      txHash: receipt.hash,
      recordIndex,
      merkleRoot: root,
      eventCount: events.length,
      periodStart,
      periodEnd,
    };
  }

  async getRecord(index: number) {
    return this.contract.getRecord(index);
  }

  async getLatestRecord() {
    return this.contract.getLatestRecord();
  }

  async totalRecords(): Promise<number> {
    const total = await this.contract.totalRecords();
    return Number(total);
  }
}
