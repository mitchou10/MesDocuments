import { mockPermissions } from '@/mocks'
import type { Permission } from '@/types'
import { randomDelay } from '@/utils/async'
import type { PermissionRepository } from './types'

export class MockPermissionRepository implements PermissionRepository {
  async getPermissions(resourceId: string): Promise<Permission[]> {
    await randomDelay()
    return mockPermissions[resourceId] ?? []
  }
}
