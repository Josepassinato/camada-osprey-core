import { MerkleTree } from "merkletreejs";
import { sha256 } from "@noble/hashes/sha256";
import { bytesToHex } from "@noble/hashes/utils";

export interface AuditEvent {
  eventId: string;
  agentId: string;
  action: string;
  timestamp: number;
  payload: string;
}

function hashEvent(event: AuditEvent): Buffer {
  const data = `${event.eventId}:${event.agentId}:${event.action}:${event.timestamp}:${event.payload}`;
  return Buffer.from(sha256(Buffer.from(data)));
}

export function buildMerkleTree(events: AuditEvent[]): {
  tree: MerkleTree;
  root: string;
  leaves: string[];
} {
  if (events.length === 0) {
    throw new Error("Cannot build Merkle tree from empty events");
  }

  const leaves = events.map(hashEvent);
  const tree = new MerkleTree(leaves, (data: Buffer) => Buffer.from(sha256(data)), {
    sortPairs: true,
  });

  const root = tree.getHexRoot();
  const leafHexes = leaves.map((l) => "0x" + bytesToHex(l));

  return { tree, root, leaves: leafHexes };
}

export function getProof(tree: MerkleTree, event: AuditEvent): string[] {
  const leaf = hashEvent(event);
  return tree.getHexProof(leaf);
}

export function verifyProof(
  tree: MerkleTree,
  event: AuditEvent,
  proof: string[],
  root: string
): boolean {
  const leaf = hashEvent(event);
  return tree.verify(proof, leaf, root);
}
