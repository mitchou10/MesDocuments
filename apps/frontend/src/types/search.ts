import type { DocumentSource } from './document'

export type QueryScope =
  | { type: 'all' }
  | { type: 'folder'; id: string; recursive: boolean }
  | { type: 'file'; id: string }

export type SearchResultKind = 'keyword' | 'semantic' | 'hybrid'

export interface SearchFilters {
  folderId?: string
  fileKind?: string
  ownerId?: string
  dateFrom?: string
  dateTo?: string
}

export interface SearchRequest {
  query: string
  scope: QueryScope
  filters?: SearchFilters
}

export interface SearchResult {
  fileId: string
  fileName: string
  chunkId: string
  excerpt: string
  score: number
  kind: SearchResultKind
  source: DocumentSource
}

export interface SearchResponse {
  query: string
  scope: QueryScope
  results: SearchResult[]
  tookMs: number
}

export interface QueryRequest {
  question: string
  scope: QueryScope
}

export interface QueryResponse {
  answer: string
  sources: DocumentSource[]
}
