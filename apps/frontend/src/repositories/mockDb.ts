import { mockFiles } from '@/mocks'
import type { DocumentFile } from '@/types'

// Mutable in-memory store shared by every Mock*Repository, seeded from the
// static mock fixtures. Stands in for the future backend database.
// Folders are no longer mocked here (see HttpFolderRepository) - only files
// still are, since the backend has no file endpoints yet.
export const db = {
  files: mockFiles.map((f): DocumentFile => ({ ...f })),
}
