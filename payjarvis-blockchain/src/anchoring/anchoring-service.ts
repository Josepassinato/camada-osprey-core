import { ethers } from 'ethers'
import { buildMerkleTree, DecisionLeaf } from './merkle-builder'
import { PrismaClient } from '@prisma/client'
import { randomBytes } from 'crypto'

const prisma = new PrismaClient()

export class AnchoringService {
  private provider: ethers.JsonRpcProvider
  private wallet: ethers.Wallet
  private contract: ethers.Contract

  constructor() {
    this.provider = new ethers.JsonRpcProvider(process.env.RPC_URL)
    this.wallet = new ethers.Wallet(process.env.PUBLISHER_PRIVATE_KEY!, this.provider)
    this.contract = new ethers.Contract(
      process.env.ANCHORING_CONTRACT_ADDRESS!,
      ANCHORING_ABI,
      this.wallet
    )
  }

  async anchorPeriod(periodStart: Date, periodEnd: Date): Promise<void> {
    // 1. Buscar decisões do período no PayJarvis core via API
    const decisions = await this.fetchDecisions(periodStart, periodEnd)
    if (decisions.length === 0) return

    // 2. Gerar salt único para o período
    const periodSalt = randomBytes(16).toString('hex')

    // 3. Construir Merkle tree
    const { tree, root } = buildMerkleTree(decisions, periodSalt)

    // 4. Salvar no DB antes de publicar
    const anchorRecord = await prisma.anchorRecord.create({
      data: {
        merkleRoot: root,
        periodStart,
        periodEnd,
        periodSalt,
        eventCount: decisions.length,
        chainId: parseInt(process.env.CHAIN_ID!),
        status: 'pending'
      }
    })

    // 5. Publicar on-chain com retry
    let attempts = 0
    while (attempts < 3) {
      try {
        const tx = await this.contract.anchorRoot(
          root,
          Math.floor(periodStart.getTime() / 1000),
          Math.floor(periodEnd.getTime() / 1000),
          decisions.length,
          1, // schemaVersion
          process.env.ISSUER_ID || 'payjarvis.com'
        )
        const receipt = await tx.wait()

        // 6. Atualizar DB com resultado
        await prisma.anchorRecord.update({
          where: { id: anchorRecord.id },
          data: {
            txHash: receipt.hash,
            blockNumber: receipt.blockNumber,
            status: 'confirmed'
          }
        })
        return
      } catch (err) {
        attempts++
        if (attempts === 3) {
          await prisma.anchorRecord.update({
            where: { id: anchorRecord.id },
            data: { status: 'failed' }
          })
          throw err
        }
        await new Promise(r => setTimeout(r, 5000 * attempts))
      }
    }
  }

  private async fetchDecisions(start: Date, end: Date): Promise<DecisionLeaf[]> {
    // Chamar a API do PayJarvis core para buscar decisões do período
    const res = await fetch(`${process.env.PAYJARVIS_API_URL}/internal/decisions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.INTERNAL_API_KEY}`
      },
      body: JSON.stringify({ start, end })
    })
    return res.json()
  }

  async getRecord(index: number) {
    return this.contract.getRecord(index)
  }

  async getLatestRecord() {
    return this.contract.getLatestRecord()
  }

  async totalRecords(): Promise<number> {
    const total = await this.contract.totalRecords()
    return Number(total)
  }
}

const ANCHORING_ABI = [
  "function anchorRoot(bytes32,uint256,uint256,uint256,uint8,string) returns (uint256)",
  "function getRecord(uint256) view returns (tuple(bytes32,uint256,uint256,uint256,uint8,string,uint256))",
  "function getLatestRecord() view returns (tuple(bytes32,uint256,uint256,uint256,uint8,string,uint256),uint256)",
  "function totalRecords() view returns (uint256)"
]
