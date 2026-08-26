import type {
  AgentQueryRequest,
  AgentResponse,
  DocumentFile,
  DocumentSummary,
  FileVersion,
  Folder,
  FolderChildren,
  Permission,
  QueryRequest,
  QueryResponse,
  SearchRequest,
  SearchResponse,
  Share,
  TranscriptSegment,
} from '@/types'

export interface FolderRepository {
  getFolder(id: string): Promise<Folder>
  getChildren(id: string): Promise<FolderChildren>
  createFolder(parentId: string, name: string): Promise<Folder>
  rename(id: string, name: string): Promise<Folder>
  remove(id: string): Promise<void>
  toggleFavorite(id: string): Promise<Folder>
}

export interface DocumentRepository {
  getDocument(id: string): Promise<DocumentFile>
  getVersions(id: string): Promise<FileVersion[]>
  getSummary(id: string): Promise<DocumentSummary | null>
  getTranscript(id: string): Promise<TranscriptSegment[]>
  rename(id: string, name: string): Promise<DocumentFile>
  remove(id: string): Promise<void>
  toggleFavorite(id: string): Promise<DocumentFile>
  askQuestion(request: QueryRequest): Promise<QueryResponse>
}

export interface SearchRepository {
  search(request: SearchRequest): Promise<SearchResponse>
}

export interface SharingRepository {
  getShares(resourceId: string): Promise<Share[]>
  addShare(share: Omit<Share, 'id' | 'createdAt'>): Promise<Share>
  removeShare(shareId: string): Promise<void>
}

export interface PermissionRepository {
  getPermissions(resourceId: string): Promise<Permission[]>
}

export interface AgentRepository {
  query(request: AgentQueryRequest): Promise<AgentResponse>
}
