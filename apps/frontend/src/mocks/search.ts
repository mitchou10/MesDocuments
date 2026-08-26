import type { DocumentChunk } from '@/types'

export const mockChunks: DocumentChunk[] = [
  {
    id: 'c-1',
    fileId: 'f-contrat-2024',
    text: '... le présent contrat est conclu pour une durée initiale de trois ans, la clause de résiliation prévoit un préavis de trois mois ...',
    source: { type: 'pdf', fileId: 'f-contrat-2024', page: 12, bbox: [72, 320, 520, 360] },
  },
  {
    id: 'c-2',
    fileId: 'f-contrat-2024',
    text: '... la durée du contrat est fixée à trois ans à compter de la date de signature ...',
    source: { type: 'pdf', fileId: 'f-contrat-2024', page: 4, bbox: [72, 120, 520, 160] },
  },
  {
    id: 'c-3',
    fileId: 'f-avenant-2025',
    text: '... la clause de résiliation est portée à six mois de préavis à compter du présent avenant ...',
    source: { type: 'pdf', fileId: 'f-avenant-2025', page: 4, bbox: [72, 200, 520, 240] },
  },
  {
    id: 'c-4',
    fileId: 'f-contrat-total',
    text: '... résiliation anticipée possible en cas de manquement grave de l’une des parties ...',
    source: { type: 'pdf', fileId: 'f-contrat-total', page: 8, bbox: [72, 400, 520, 440] },
  },
  {
    id: 'c-5',
    fileId: 'f-reunion-fevrier',
    text: "... on doit revoir la clause de résiliation avant la fin du mois ...",
    source: { type: 'audio', fileId: 'f-reunion-fevrier', startMs: 752_000, endMs: 784_000 },
  },
  {
    id: 'c-6',
    fileId: 'f-reunion-janvier',
    text: '... le point suivant concerne le renouvellement du contrat ACME ...',
    source: { type: 'video', fileId: 'f-reunion-janvier', startMs: 752_000, endMs: 790_000 },
  },
]
