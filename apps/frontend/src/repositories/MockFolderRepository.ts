import type { Folder, FolderChildren } from '@/types'
import { randomDelay } from '@/utils/async'
import { db, generateFolderId } from './mockDb'
import type { FolderRepository } from './types'

export class MockFolderRepository implements FolderRepository {
  async getFolder(id: string): Promise<Folder> {
    await randomDelay()
    const folder = db.folders.find((f) => f.id === id)
    if (!folder) throw new Error(`Folder ${id} not found`)
    return folder
  }

  async getChildren(id: string): Promise<FolderChildren> {
    await randomDelay()
    const folder = await this.getFolder(id)
    const subfolders = db.folders.filter((f) => f.parentId === id)
    const files = db.files.filter((f) => f.folderId === id)
    return { folder, subfolders, files }
  }

  async createFolder(parentId: string, name: string): Promise<Folder> {
    await randomDelay()
    const parent = await this.getFolder(parentId)
    const folder: Folder = {
      id: generateFolderId(),
      name,
      parentId,
      path: [...parent.path, parent.name],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      isFavorite: false,
    }
    db.folders.push(folder)
    return folder
  }

  async rename(id: string, name: string): Promise<Folder> {
    await randomDelay()
    const folder = await this.getFolder(id)
    folder.name = name
    folder.updatedAt = new Date().toISOString()
    return folder
  }

  async remove(id: string): Promise<void> {
    await randomDelay()
    db.folders = db.folders.filter((f) => f.id !== id)
    db.files = db.files.filter((f) => f.folderId !== id)
  }

  async toggleFavorite(id: string): Promise<Folder> {
    await randomDelay()
    const folder = await this.getFolder(id)
    folder.isFavorite = !folder.isFavorite
    return folder
  }
}
