export type PermissionLevel = 'reader' | 'editor' | 'owner'

export type PermissionOrigin = 'direct' | 'inherited' | 'denied'

export interface PrincipalRef {
  kind: 'user' | 'group'
  id: string
  name: string
}

export interface Permission {
  principal: PrincipalRef
  level: PermissionLevel
  origin: PermissionOrigin
  inheritedFrom?: string
}

export interface Share {
  id: string
  resourceId: string
  resourceType: 'file' | 'folder'
  principal: PrincipalRef
  level: PermissionLevel
  createdAt: string
}
