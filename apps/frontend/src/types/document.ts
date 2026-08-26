export type FileKind = 'pdf' | 'audio' | 'video' | 'image' | 'other'

export interface Folder {
  id: string
  name: string
  parentId: string | null
  path: string[]
  createdAt: string
  updatedAt: string
  isFavorite: boolean
}

export interface FolderChildren {
  // null at the root: there is no single "root folder" resource on the
  // backend, only folders with parentId === null.
  folder: Folder | null
  subfolders: Folder[]
  files: DocumentFile[]
}

export interface DocumentFile {
  id: string
  name: string
  kind: FileKind
  mimeType: string
  sizeBytes: number
  folderId: string
  path: string[]
  createdAt: string
  updatedAt: string
  isFavorite: boolean
  ownerId: string
  pageCount?: number
  durationMs?: number
}

export interface FileVersion {
  id: string
  fileId: string
  versionNumber: number
  createdAt: string
  authorId: string
  sizeBytes: number
  note?: string
}

export interface DocumentSummary {
  fileId: string
  text: string
  generatedAt: string
}

export interface DocumentChunk {
  id: string
  fileId: string
  text: string
  source: DocumentSource
}

export type DocumentSource =
  | {
      type: 'pdf'
      fileId: string
      page: number
      bbox?: [number, number, number, number]
    }
  | {
      type: 'audio'
      fileId: string
      startMs: number
      endMs: number
    }
  | {
      type: 'video'
      fileId: string
      startMs: number
      endMs: number
    }

export interface TranscriptSegment {
  startMs: number
  endMs: number
  speaker: string
  text: string
}

export type UiState = 'idle' | 'loading' | 'empty' | 'error' | 'forbidden' | 'not_found' | 'processing'
