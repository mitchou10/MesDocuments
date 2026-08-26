import { HttpFolderRepository } from './HttpFolderRepository'
import { MockAgentRepository } from './MockAgentRepository'
import { MockDocumentRepository } from './MockDocumentRepository'
import { MockPermissionRepository } from './MockPermissionRepository'
import { MockSearchRepository } from './MockSearchRepository'
import { MockSharingRepository } from './MockSharingRepository'

// Single composition point: swap these instances for HTTP-backed
// implementations once the real backend exists — nothing else changes.
export const folderRepository = new HttpFolderRepository()
export const documentRepository = new MockDocumentRepository()
export const searchRepository = new MockSearchRepository()
export const sharingRepository = new MockSharingRepository()
export const permissionRepository = new MockPermissionRepository()
export const agentRepository = new MockAgentRepository()

export * from './types'
