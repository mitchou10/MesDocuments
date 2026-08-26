import { mockFiles, mockFolders } from '@/mocks'
import type { DocumentFile, Folder } from '@/types'

// Mutable in-memory store shared by every Mock*Repository, seeded from the
// static mock fixtures. Stands in for the future backend database.
export const db = {
  folders: mockFolders.map((f): Folder => ({ ...f })),
  files: mockFiles.map((f): DocumentFile => ({ ...f })),
}

let nextFolderId = 1000

export function generateFolderId(): string {
  nextFolderId += 1
  return `folder-${nextFolderId}`
}
