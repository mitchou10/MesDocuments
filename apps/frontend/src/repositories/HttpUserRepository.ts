import type { PrincipalRef } from '@/types'
import type { UserRepository } from './types'

const BASE_URL = '/api/v1/users'

interface UserDto {
  id: string
  username: string | null
  display_name: string | null
  email: string | null
}

function mapUser(dto: UserDto): PrincipalRef {
  return { kind: 'user', id: dto.id, name: dto.display_name ?? dto.username ?? dto.email ?? dto.id }
}

export class HttpUserRepository implements UserRepository {
  async search(query: string): Promise<PrincipalRef[]> {
    const response = await fetch(`${BASE_URL}/search?q=${encodeURIComponent(query)}`, {
      credentials: 'same-origin',
    })
    if (!response.ok) {
      const body = await response.json().catch(() => null)
      throw new Error(body?.detail ?? `Recherche échouée (${response.status})`)
    }
    const dtos = (await response.json()) as UserDto[]
    return dtos.map(mapUser)
  }
}
