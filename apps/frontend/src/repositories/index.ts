import { HttpDocumentRepository } from './HttpDocumentRepository'
import { HttpFolderRepository } from './HttpFolderRepository'
import { HttpSharingRepository } from './HttpSharingRepository'
import { HttpUserRepository } from './HttpUserRepository'
import { MockAgentRepository } from './MockAgentRepository'
import { MockPermissionRepository } from './MockPermissionRepository'
import { MockSearchRepository } from './MockSearchRepository'
import type {
  AgentRepository,
  DocumentRepository,
  FolderRepository,
  PermissionRepository,
  SearchRepository,
  SharingRepository,
  UserRepository,
} from './types'

// Single composition point: swap these instances for HTTP-backed
// implementations once the real backend exists — nothing else changes.
// Typed against the interfaces (not the concrete classes) so a swap can
// never silently narrow or widen a method's signature at call sites.
export const folderRepository: FolderRepository = new HttpFolderRepository()
export const documentRepository: DocumentRepository = new HttpDocumentRepository()
export const searchRepository: SearchRepository = new MockSearchRepository()
export const sharingRepository: SharingRepository = new HttpSharingRepository()
export const userRepository: UserRepository = new HttpUserRepository()
export const permissionRepository: PermissionRepository = new MockPermissionRepository()
export const agentRepository: AgentRepository = new MockAgentRepository()

export * from './types'
