export interface User {
  id: string
  displayName: string
  email: string
  avatarUrl?: string
}

export interface Group {
  id: string
  name: string
  memberCount: number
}
