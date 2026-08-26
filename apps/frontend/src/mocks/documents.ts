import type { DocumentFile, DocumentSummary, TranscriptSegment } from '@/types'
import { currentUser } from './users'

// Folders are no longer mocked here - they come from the real backend (see
// HttpFolderRepository). Files below keep their own hardcoded `path` and
// `folderId`, which is why they still work standalone, but that folderId no
// longer matches any real folder id: files won't show up when browsing a
// real folder until the backend grows file endpoints.

const favoriteFileIds = new Set(['f-contrat-2024', 'f-rapport-t2'])

function file(partial: Omit<DocumentFile, 'ownerId' | 'isFavorite'>): DocumentFile {
  return { ...partial, ownerId: currentUser.id, isFavorite: favoriteFileIds.has(partial.id) }
}

export const mockFiles: DocumentFile[] = [
  file({
    id: 'f-contrat-2024',
    name: 'contrat-2024.pdf',
    kind: 'pdf',
    mimeType: 'application/pdf',
    sizeBytes: 2_400_000,
    folderId: 'acme-contrats',
    path: ['Mes documents', 'Clients', 'ACME', 'Contrats'],
    createdAt: '2024-01-10T09:00:00.000Z',
    updatedAt: '2026-08-25T08:00:00.000Z',
    pageCount: 18,
  }),
  file({
    id: 'f-avenant-2025',
    name: 'avenant-2025.pdf',
    kind: 'pdf',
    mimeType: 'application/pdf',
    sizeBytes: 640_000,
    folderId: 'acme-contrats',
    path: ['Mes documents', 'Clients', 'ACME', 'Contrats'],
    createdAt: '2025-02-15T09:00:00.000Z',
    updatedAt: '2026-08-20T08:00:00.000Z',
    pageCount: 6,
  }),
  file({
    id: 'f-reunion-janvier',
    name: 'reunion-janvier.mp4',
    kind: 'video',
    mimeType: 'video/mp4',
    sizeBytes: 188_000_000,
    folderId: 'acme-reunions',
    path: ['Mes documents', 'Clients', 'ACME', 'Réunions'],
    createdAt: '2026-01-14T09:00:00.000Z',
    updatedAt: '2026-08-24T08:00:00.000Z',
    durationMs: 54 * 60_000 + 12_000,
  }),
  file({
    id: 'f-reunion-fevrier',
    name: 'reunion-fevrier.mp3',
    kind: 'audio',
    mimeType: 'audio/mpeg',
    sizeBytes: 42_000_000,
    folderId: 'acme-reunions',
    path: ['Mes documents', 'Clients', 'ACME', 'Réunions'],
    createdAt: '2026-02-11T09:00:00.000Z',
    updatedAt: '2026-08-24T08:00:00.000Z',
    durationMs: 45 * 60_000 + 12_000,
  }),
  file({
    id: 'f-fiche-client',
    name: 'fiche-client.pdf',
    kind: 'pdf',
    mimeType: 'application/pdf',
    sizeBytes: 210_000,
    folderId: 'acme-admin',
    path: ['Mes documents', 'Clients', 'ACME', 'Documents administratifs'],
    createdAt: '2024-03-01T09:00:00.000Z',
    updatedAt: '2026-07-01T08:00:00.000Z',
    pageCount: 2,
  }),
  file({
    id: 'f-contrat-total',
    name: 'contrat-total.pdf',
    kind: 'pdf',
    mimeType: 'application/pdf',
    sizeBytes: 1_100_000,
    folderId: 'total-contrats',
    path: ['Mes documents', 'Clients', 'Total', 'Contrats'],
    createdAt: '2024-05-20T09:00:00.000Z',
    updatedAt: '2026-08-10T08:00:00.000Z',
    pageCount: 14,
  }),
  file({
    id: 'f-facture-0425',
    name: 'facture-avril-2025.pdf',
    kind: 'pdf',
    mimeType: 'application/pdf',
    sizeBytes: 98_000,
    folderId: 'finance-factures',
    path: ['Mes documents', 'Finance', 'Factures'],
    createdAt: '2025-04-30T09:00:00.000Z',
    updatedAt: '2025-04-30T09:00:00.000Z',
    pageCount: 1,
  }),
  file({
    id: 'f-rapport-t2',
    name: 'rapport-t2-2026.pdf',
    kind: 'pdf',
    mimeType: 'application/pdf',
    sizeBytes: 3_600_000,
    folderId: 'finance-rapports',
    path: ['Mes documents', 'Finance', 'Rapports'],
    createdAt: '2026-07-05T09:00:00.000Z',
    updatedAt: '2026-07-05T09:00:00.000Z',
    pageCount: 32,
  }),
  file({
    id: 'f-procedure-conges',
    name: 'procedure-conges.pdf',
    kind: 'pdf',
    mimeType: 'application/pdf',
    sizeBytes: 320_000,
    folderId: 'rh-procedures',
    path: ['Mes documents', 'RH', 'Procédures'],
    createdAt: '2023-09-01T09:00:00.000Z',
    updatedAt: '2026-01-15T09:00:00.000Z',
    pageCount: 4,
  }),
  file({
    id: 'f-livret-accueil',
    name: 'livret-accueil.pdf',
    kind: 'pdf',
    mimeType: 'application/pdf',
    sizeBytes: 1_800_000,
    folderId: 'rh-interne',
    path: ['Mes documents', 'RH', 'Documents internes'],
    createdAt: '2023-01-10T09:00:00.000Z',
    updatedAt: '2026-02-01T09:00:00.000Z',
    pageCount: 22,
  }),
]

export const mockSummaries: Record<string, DocumentSummary> = {
  'f-contrat-2024': {
    fileId: 'f-contrat-2024',
    text: "Contrat de prestation entre ACME et l'entreprise, conclu pour une durée initiale de trois ans à compter du 1er janvier 2024, avec reconduction tacite et clause de résiliation moyennant un préavis de trois mois.",
    generatedAt: '2026-08-25T08:05:00.000Z',
  },
  'f-avenant-2025': {
    fileId: 'f-avenant-2025',
    text: "Avenant modifiant les conditions tarifaires du contrat initial et prolongeant la clause de résiliation à six mois de préavis.",
    generatedAt: '2026-08-20T08:05:00.000Z',
  },
  'f-contrat-total': {
    fileId: 'f-contrat-total',
    text: "Contrat cadre avec Total, portant sur la fourniture de services, durée de deux ans avec clause de résiliation anticipée en cas de manquement.",
    generatedAt: '2026-08-10T08:05:00.000Z',
  },
}

export const mockAudioTranscripts: Record<string, TranscriptSegment[]> = {
  'f-reunion-fevrier': [
    { startMs: 752_000, endMs: 784_000, speaker: 'Alice', text: "On doit revoir la clause de résiliation avant la fin du mois." },
    { startMs: 784_000, endMs: 820_000, speaker: 'Bob', text: "D'accord, je prépare l'avenant avec le service juridique." },
    { startMs: 820_000, endMs: 860_000, speaker: 'Alice', text: "Parfait, on vise un préavis de six mois." },
  ],
}

export const mockVideoTranscripts: Record<string, TranscriptSegment[]> = {
  'f-reunion-janvier': [
    { startMs: 752_000, endMs: 790_000, speaker: 'Camille', text: "Le point suivant concerne le renouvellement du contrat ACME." },
    { startMs: 790_000, endMs: 830_000, speaker: 'Alice', text: "Nous proposons une reconduction pour trois ans." },
  ],
}
