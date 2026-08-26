import type { Permission, Share } from '@/types'

export const mockPermissions: Record<string, Permission[]> = {
  'acme-contrats': [
    { principal: { kind: 'user', id: 'u-2', name: 'Alice Dupont' }, level: 'reader', origin: 'direct' },
    { principal: { kind: 'group', id: 'g-1', name: 'Groupe Finance' }, level: 'reader', origin: 'direct' },
  ],
  'f-contrat-2024': [
    { principal: { kind: 'user', id: 'u-2', name: 'Alice Dupont' }, level: 'reader', origin: 'inherited', inheritedFrom: 'Contrats' },
    { principal: { kind: 'user', id: 'u-3', name: 'Bob Martin' }, level: 'editor', origin: 'direct' },
  ],
  'f-facture-0425': [
    { principal: { kind: 'user', id: 'u-2', name: 'Alice Dupont' }, level: 'reader', origin: 'denied' },
  ],
}

export const mockShares: Record<string, Share[]> = {
  'f-contrat-2024': [
    {
      id: 'sh-1',
      resourceId: 'f-contrat-2024',
      resourceType: 'file',
      principal: { kind: 'user', id: 'u-2', name: 'Alice Dupont' },
      level: 'editor',
      createdAt: '2026-06-01T09:00:00.000Z',
    },
    {
      id: 'sh-2',
      resourceId: 'f-contrat-2024',
      resourceType: 'file',
      principal: { kind: 'user', id: 'u-3', name: 'Bob Martin' },
      level: 'reader',
      createdAt: '2026-06-05T09:00:00.000Z',
    },
    {
      id: 'sh-3',
      resourceId: 'f-contrat-2024',
      resourceType: 'file',
      principal: { kind: 'group', id: 'g-1', name: 'Groupe Finance' },
      level: 'reader',
      createdAt: '2026-06-05T09:00:00.000Z',
    },
  ],
}
