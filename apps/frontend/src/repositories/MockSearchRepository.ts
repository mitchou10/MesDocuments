import { mockChunks, mockFiles } from '@/mocks'
import type { SearchRequest, SearchResponse, SearchResult, SearchResultKind } from '@/types'
import { randomDelay } from '@/utils/async'
import type { SearchRepository } from './types'

function kindForIndex(index: number): SearchResultKind {
  const kinds: SearchResultKind[] = ['hybrid', 'keyword', 'semantic']
  return kinds[index % kinds.length]
}

export class MockSearchRepository implements SearchRepository {
  async search(request: SearchRequest): Promise<SearchResponse> {
    await randomDelay(300, 700)
    const query = request.query.trim().toLowerCase()

    const results: SearchResult[] = mockChunks
      .filter((chunk) => {
        if (query.length > 0 && !chunk.text.toLowerCase().includes(extractKeyword(query))) return false
        if (request.scope.type === 'file') return chunk.fileId === request.scope.id
        if (request.scope.type === 'folder') {
          const file = mockFiles.find((f) => f.id === chunk.fileId)
          if (!file) return false
          return request.scope.recursive
            ? file.path.includes(folderNameFor(request.scope.id))
            : file.folderId === request.scope.id
        }
        return true
      })
      .filter((chunk) => {
        if (!request.filters?.fileKind) return true
        const file = mockFiles.find((f) => f.id === chunk.fileId)
        return file?.kind === request.filters?.fileKind
      })
      .map((chunk, index) => {
        const file = mockFiles.find((f) => f.id === chunk.fileId)
        return {
          fileId: chunk.fileId,
          fileName: file?.name ?? chunk.fileId,
          chunkId: chunk.id,
          excerpt: chunk.text,
          score: Number((0.95 - index * 0.07).toFixed(2)),
          kind: kindForIndex(index),
          source: chunk.source,
        }
      })

    return { query: request.query, scope: request.scope, results, tookMs: 42 }
  }
}

function extractKeyword(query: string): string {
  if (query.includes('résiliation') || query.includes('resiliation')) return 'résiliation'
  if (query.includes('renouvellement')) return 'renouvellement'
  if (query.includes('durée') || query.includes('duree')) return 'durée'
  return query
}

function folderNameFor(folderId: string): string {
  const names: Record<string, string> = {
    acme: 'ACME',
    'acme-contrats': 'Contrats',
    clients: 'Clients',
    total: 'Total',
  }
  return names[folderId] ?? folderId
}
