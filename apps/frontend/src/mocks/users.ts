import type { Group, User } from '@/types'

export const currentUser: User = {
  id: 'u-1',
  displayName: 'Camille Bernard',
  email: 'camille.bernard@example.fr',
}

export const mockUsers: User[] = [
  currentUser,
  { id: 'u-2', displayName: 'Alice Dupont', email: 'alice.dupont@example.fr' },
  { id: 'u-3', displayName: 'Bob Martin', email: 'bob.martin@example.fr' },
]

export const mockGroups: Group[] = [{ id: 'g-1', name: 'Groupe Finance', memberCount: 8 }]
