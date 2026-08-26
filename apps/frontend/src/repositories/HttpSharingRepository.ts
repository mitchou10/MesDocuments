import type { PermissionLevel, PrincipalRef, Share } from '@/types'
import type { SharingRepository } from './types'

const FOLDERS_BASE_URL = '/api/v1/folders'
const SHARES_BASE_URL = '/api/v1/shares'
const USERS_BASE_URL = '/api/v1/users'

interface ShareDto {
  id: string
  resource_type: 'file' | 'folder'
  resource_id: string
  principal_type: 'user' | 'group'
  principal_id: string
  level: PermissionLevel
  created_by: string
  created_at: string
}

interface UserDto {
  id: string
  username: string | null
  display_name: string | null
  email: string | null
}

async function apiFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
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

// A share only stores a principal_id - resolving it to a display name needs
// a lookup per unique user. Groups have no directory yet, so they fall back
// to a generic label instead of a broken lookup.
async function resolvePrincipal(type: 'user' | 'group', id: string): Promise<PrincipalRef> {
  if (type === 'group') return { kind: 'group', id, name: 'Groupe' }
  try {
    const dto = await apiFetch<UserDto>(`${USERS_BASE_URL}/${id}`)
    return { kind: 'user', id, name: dto.display_name ?? dto.username ?? dto.email ?? id }
  } catch {
    return { kind: 'user', id, name: id }
  }
}

async function mapShare(dto: ShareDto): Promise<Share> {
  return {
    id: dto.id,
    resourceId: dto.resource_id,
    resourceType: dto.resource_type,
    principal: await resolvePrincipal(dto.principal_type, dto.principal_id),
    level: dto.level,
    createdAt: dto.created_at,
  }
}

export class HttpSharingRepository implements SharingRepository {
  async getShares(resourceId: string, resourceType: 'file' | 'folder'): Promise<Share[]> {
    if (resourceType !== 'folder') {
      throw new Error('Le partage de fichiers individuels n’est pas encore disponible côté backend.')
    }
    const dtos = await apiFetch<ShareDto[]>(`${FOLDERS_BASE_URL}/${resourceId}/shares`)
    return Promise.all(dtos.map(mapShare))
  }

  async addShare(share: Omit<Share, 'id' | 'createdAt'>): Promise<Share> {
    if (share.resourceType !== 'folder') {
      throw new Error('Le partage de fichiers individuels n’est pas encore disponible côté backend.')
    }
    const dto = await apiFetch<ShareDto>(`${FOLDERS_BASE_URL}/${share.resourceId}/shares`, {
      method: 'POST',
      body: JSON.stringify({
        resource_type: share.resourceType,
        resource_id: share.resourceId,
        principal_type: share.principal.kind,
        principal_id: share.principal.id,
        level: share.level,
      }),
    })
    return mapShare(dto)
  }

  async removeShare(shareId: string): Promise<void> {
    await apiFetch<void>(`${SHARES_BASE_URL}/${shareId}`, { method: 'DELETE' })
  }
}
