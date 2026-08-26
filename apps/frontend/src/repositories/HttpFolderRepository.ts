import type { DocumentFile, FileKind, Folder, FolderChildren } from '@/types'
import type { FolderRepository } from './types'

const BASE_URL = '/api/v1/folders'

interface FolderDto {
  id: string
  name: string
  parent_id: string | null
  owner_id: string
  created_at: string
  updated_at: string
  deleted_at: string | null
}

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

// The file's "Emplacement" is the folder it lives in, inclusive - unlike a
// folder's own breadcrumb, which stops at its parent (see mapFolderLight).
// The containing folder's path is already known here, so this needs no
// extra requests.
function mapFile(dto: FileDto, folderPath: string[]): DocumentFile {
  return {
    id: dto.id,
    name: dto.name,
    kind: dto.kind,
    mimeType: dto.mime_type,
    sizeBytes: dto.size_bytes,
    folderId: dto.folder_id,
    path: folderPath,
    createdAt: dto.created_at,
    updatedAt: dto.updated_at,
    isFavorite: false,
    ownerId: dto.owner_id,
    pageCount: dto.page_count ?? undefined,
    durationMs: dto.duration_ms ?? undefined,
  }
}

interface PageDto<T> {
  items: T[]
  total: number
  limit: number
  offset: number
  has_more: boolean
}

// No pagination UI exists yet for folder listings - a generously large page
// covers realistic folder sizes for now. Revisit once the UI grows one.
const LIST_LIMIT = 100

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
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

// List rows only ever render `folder.name` (see FileFolderTable), never
// `folder.path` - skip computing it there and pay that cost only for the
// single folder actually being viewed (see `mapFolderWithPath`).
function mapFolderLight(dto: FolderDto): Folder {
  return {
    id: dto.id,
    name: dto.name,
    parentId: dto.parent_id,
    path: [],
    createdAt: dto.created_at,
    updatedAt: dto.updated_at,
    isFavorite: false,
  }
}

export class HttpFolderRepository implements FolderRepository {
  async getFolder(id: string): Promise<Folder> {
    const dto = await apiFetch<FolderDto>(`/${id}`)
    return this.mapFolderWithPath(dto)
  }

  async getChildren(id: string | null): Promise<FolderChildren> {
    if (id === null) {
      const page = await apiFetch<PageDto<FolderDto>>(`?limit=${LIST_LIMIT}`)
      // No root-level files: every file belongs to a real folder on the
      // backend, so "Mes documents" only ever lists subfolders.
      return { folder: null, subfolders: page.items.map(mapFolderLight), files: [] }
    }

    const [folderDto, childrenPage, filesPage] = await Promise.all([
      apiFetch<FolderDto>(`/${id}`),
      apiFetch<PageDto<FolderDto>>(`/${id}/children?limit=${LIST_LIMIT}`),
      apiFetch<PageDto<FileDto>>(`/${id}/files?limit=${LIST_LIMIT}`),
    ])

    const folder = await this.mapFolderWithPath(folderDto)
    const filePath = [...folder.path, folder.name]

    return {
      folder,
      subfolders: childrenPage.items.map(mapFolderLight),
      files: filesPage.items.map((dto) => mapFile(dto, filePath)),
    }
  }

  async createFolder(parentId: string | null, name: string): Promise<Folder> {
    const dto = await apiFetch<FolderDto>('', {
      method: 'POST',
      body: JSON.stringify({ name, parent_id: parentId }),
    })
    return this.mapFolderWithPath(dto)
  }

  async rename(id: string, name: string): Promise<Folder> {
    const dto = await apiFetch<FolderDto>(`/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ name }),
    })
    return this.mapFolderWithPath(dto)
  }

  async remove(id: string): Promise<void> {
    await apiFetch<void>(`/${id}`, { method: 'DELETE' })
  }

  async toggleFavorite(): Promise<Folder> {
    throw new Error('Les favoris de dossiers ne sont pas encore disponibles côté backend.')
  }

  private async mapFolderWithPath(dto: FolderDto): Promise<Folder> {
    return {
      id: dto.id,
      name: dto.name,
      parentId: dto.parent_id,
      path: await this.computePath(dto.parent_id),
      createdAt: dto.created_at,
      updatedAt: dto.updated_at,
      isFavorite: false,
    }
  }

  // No dedicated breadcrumb endpoint on the backend: walk the parent chain
  // ourselves. Fine for the depths this app expects; revisit if folders end
  // up nested deep enough to make N sequential requests noticeable.
  private async computePath(parentId: string | null): Promise<string[]> {
    const names: string[] = []
    let currentId = parentId
    while (currentId !== null) {
      const dto = await apiFetch<FolderDto>(`/${currentId}`)
      names.unshift(dto.name)
      currentId = dto.parent_id
    }
    return ['Mes documents', ...names]
  }
}
