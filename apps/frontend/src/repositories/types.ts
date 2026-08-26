import type {
  AgentQueryRequest,
  AgentResponse,
  DocumentFile,
  DocumentSummary,
  FileVersion,
  Folder,
  FolderChildren,
  Permission,
  PrincipalRef,
  QueryRequest,
  QueryResponse,
  SearchRequest,
  SearchResponse,
  Share,
  TranscriptSegment,
} from '@/types'

export interface FolderRepository {
  getFolder(id: string): Promise<Folder>
  // null = root ("Mes documents"): there is no single root folder resource,
  // only folders whose parentId is null.
  getChildren(id: string | null): Promise<FolderChildren>
  createFolder(parentId: string | null, name: string): Promise<Folder>
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
  upload(folderId: string, file: File): Promise<DocumentFile>
}

export interface SearchRepository {
  search(request: SearchRequest): Promise<SearchResponse>
}

export interface SharingRepository {
  getShares(resourceId: string, resourceType: 'file' | 'folder'): Promise<Share[]>
  addShare(share: Omit<Share, 'id' | 'createdAt'>): Promise<Share>
  removeShare(shareId: string): Promise<void>
}

export interface UserRepository {
  search(query: string): Promise<PrincipalRef[]>
}

export interface PermissionRepository {
  getPermissions(resourceId: string): Promise<Permission[]>
}

export interface AgentRepository {
  query(request: AgentQueryRequest): Promise<AgentResponse>
}
