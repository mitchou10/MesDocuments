import { mockShares } from '@/mocks'
import type { Share } from '@/types'
import { randomDelay } from '@/utils/async'
import type { SharingRepository } from './types'

const shares: Record<string, Share[]> = Object.fromEntries(
  Object.entries(mockShares).map(([id, list]) => [id, list.map((s) => ({ ...s }))]),
)

let nextShareId = 1000

export class MockSharingRepository implements SharingRepository {
  async getShares(resourceId: string): Promise<Share[]> {
    await randomDelay()
    return shares[resourceId] ?? []
  }

  async addShare(share: Omit<Share, 'id' | 'createdAt'>): Promise<Share> {
    await randomDelay()
    nextShareId += 1
    const created: Share = { ...share, id: `sh-${nextShareId}`, createdAt: new Date().toISOString() }
    shares[share.resourceId] = [...(shares[share.resourceId] ?? []), created]
    return created
  }

  async removeShare(shareId: string): Promise<void> {
    await randomDelay()
    for (const resourceId of Object.keys(shares)) {
      shares[resourceId] = shares[resourceId].filter((s) => s.id !== shareId)
    }
  }
}
