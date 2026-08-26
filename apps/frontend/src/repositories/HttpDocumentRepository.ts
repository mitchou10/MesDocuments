import type {
  DocumentFile,
  DocumentSummary,
  FileKind,
  FileVersion,
  QueryRequest,
  QueryResponse,
  TranscriptSegment,
} from '@/types'
import type { DocumentRepository } from './types'

const FILES_BASE_URL = '/api/v1'
const FOLDERS_BASE_URL = '/api/v1/folders'

interface FileDto {
  id: string
  name: string
  kind: FileKind
  mime_type: string
  size_bytes: number
  folder_id: string
  owner_id: string
  page_count: number | null
  duration_ms: number | null
  created_at: string
  updated_at: string
  deleted_at: string | null
}

interface FolderRefDto {
  id: string
  name: string
  parent_id: string | null
}

async function apiFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail ?? `Requête échouée (${response.status})`)
  }
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

// A document's "Emplacement" includes the folder it lives in (unlike a
// folder's own breadcrumb, which stops at its parent) - so this walks from
// the folder itself up to the root, inclusive.
async function computeFilePath(folderId: string): Promise<string[]> {
  const names: string[] = []
  let currentId: string | null = folderId
  while (currentId !== null) {
    const dto: FolderRefDto = await apiFetch<FolderRefDto>(`${FOLDERS_BASE_URL}/${currentId}`)
    names.unshift(dto.name)
    currentId = dto.parent_id
  }
  return ['Mes documents', ...names]
}

async function mapFile(dto: FileDto): Promise<DocumentFile> {
  return {
    id: dto.id,
    name: dto.name,
    kind: dto.kind,
    mimeType: dto.mime_type,
    sizeBytes: dto.size_bytes,
    folderId: dto.folder_id,
    path: await computeFilePath(dto.folder_id),
    createdAt: dto.created_at,
    updatedAt: dto.updated_at,
    isFavorite: false,
    ownerId: dto.owner_id,
    pageCount: dto.page_count ?? undefined,
    durationMs: dto.duration_ms ?? undefined,
  }
}

export class HttpDocumentRepository implements DocumentRepository {
  async getDocument(id: string): Promise<DocumentFile> {
    const dto = await apiFetch<FileDto>(`${FILES_BASE_URL}/files/${id}`)
    return mapFile(dto)
  }

  async getVersions(id: string): Promise<FileVersion[]> {
    // No version-history endpoint on the backend yet - only the current
    // version is ever visible, reconstructed from the file itself rather
    // than showing a fake, invented one.
    const file = await this.getDocument(id)
    return [
      {
        id: `${id}-current`,
        fileId: id,
        versionNumber: 1,
        createdAt: file.createdAt,
        authorId: file.ownerId,
        sizeBytes: file.sizeBytes,
      },
    ]
  }

  async getSummary(): Promise<DocumentSummary | null> {
    // No summarization backend yet.
    return null
  }

  async getTranscript(): Promise<TranscriptSegment[]> {
    // No transcription backend yet.
    return []
  }

  async rename(id: string, name: string): Promise<DocumentFile> {
    const dto = await apiFetch<FileDto>(`${FILES_BASE_URL}/files/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ name }),
    })
    return mapFile(dto)
  }

  async remove(id: string): Promise<void> {
    await apiFetch<void>(`${FILES_BASE_URL}/files/${id}`, { method: 'DELETE' })
  }

  async toggleFavorite(): Promise<DocumentFile> {
    throw new Error('Les favoris de documents ne sont pas encore disponibles côté backend.')
  }

  async askQuestion(_request: QueryRequest): Promise<QueryResponse> {
    throw new Error("L'assistant n'est pas encore disponible côté backend.")
  }

  getDownloadUrl(id: string): string {
    return `${FILES_BASE_URL}/files/${id}/download`
  }

  async upload(folderId: string, file: File): Promise<DocumentFile> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await fetch(`${FOLDERS_BASE_URL}/${folderId}/files`, {
      method: 'POST',
      credentials: 'same-origin',
      body: formData,
    })
    if (!response.ok) {
      const body = await response.json().catch(() => null)
      throw new Error(body?.detail ?? `Import échoué (${response.status})`)
    }
    return mapFile((await response.json()) as FileDto)
  }
}
