import { mockAudioTranscripts, mockSummaries, mockVideoTranscripts } from '@/mocks'
import type { DocumentFile, DocumentSummary, FileVersion, QueryRequest, QueryResponse, TranscriptSegment } from '@/types'
import { randomDelay } from '@/utils/async'
import { db } from './mockDb'
import type { DocumentRepository } from './types'

const genericAnswers: Record<string, QueryResponse> = {
  'f-contrat-2024': {
    answer: 'Le contrat est conclu pour une durée initiale de trois ans, avec une clause de résiliation moyennant un préavis de trois mois.',
    sources: [{ type: 'pdf', fileId: 'f-contrat-2024', page: 4, bbox: [72, 120, 520, 160] }],
  },
  'f-avenant-2025': {
    answer: "L'avenant porte le préavis de résiliation à six mois.",
    sources: [{ type: 'pdf', fileId: 'f-avenant-2025', page: 4, bbox: [72, 200, 520, 240] }],
  },
}

export class MockDocumentRepository implements DocumentRepository {
  async getDocument(id: string): Promise<DocumentFile> {
    await randomDelay()
    const file = db.files.find((f) => f.id === id)
    if (!file) throw new Error(`File ${id} not found`)
    return file
  }

  async getVersions(id: string): Promise<FileVersion[]> {
    await randomDelay()
    const file = await this.getDocument(id)
    return [
      {
        id: `${id}-v2`,
        fileId: id,
        versionNumber: 2,
        createdAt: file.updatedAt,
        authorId: file.ownerId,
        sizeBytes: file.sizeBytes,
        note: 'Dernière version',
      },
      {
        id: `${id}-v1`,
        fileId: id,
        versionNumber: 1,
        createdAt: file.createdAt,
        authorId: file.ownerId,
        sizeBytes: Math.round(file.sizeBytes * 0.9),
        note: 'Version initiale',
      },
    ]
  }

  async getSummary(id: string): Promise<DocumentSummary | null> {
    await randomDelay()
    return mockSummaries[id] ?? null
  }

  async getTranscript(id: string): Promise<TranscriptSegment[]> {
    await randomDelay()
    return mockAudioTranscripts[id] ?? mockVideoTranscripts[id] ?? []
  }

  async rename(id: string, name: string): Promise<DocumentFile> {
    await randomDelay()
    const file = await this.getDocument(id)
    file.name = name
    file.updatedAt = new Date().toISOString()
    return file
  }

  async remove(id: string): Promise<void> {
    await randomDelay()
    db.files = db.files.filter((f) => f.id !== id)
  }

  async toggleFavorite(id: string): Promise<DocumentFile> {
    await randomDelay()
    const file = await this.getDocument(id)
    file.isFavorite = !file.isFavorite
    return file
  }

  async askQuestion(request: QueryRequest): Promise<QueryResponse> {
    await randomDelay(500, 1200)
    if (request.scope.type === 'file' && genericAnswers[request.scope.id]) {
      return genericAnswers[request.scope.id]
    }
    return {
      answer: "Je n'ai pas trouvé d'information précise pour répondre à cette question dans ce document.",
      sources: [],
    }
  }
}
