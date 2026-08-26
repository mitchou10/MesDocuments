import type { FileKind } from '@/types'

const iconByKind: Record<FileKind, string> = {
  pdf: 'fr-icon-file-pdf-line',
  audio: 'fr-icon-mic-line',
  video: 'fr-icon-camera-line',
  image: 'fr-icon-image-line',
  other: 'fr-icon-file-line',
}

const labelByKind: Record<FileKind, string> = {
  pdf: 'PDF',
  audio: 'Audio',
  video: 'Vidéo',
  image: 'Image',
  other: 'Fichier',
}

export function iconForFileKind(kind: FileKind): string {
  return iconByKind[kind]
}

export function labelForFileKind(kind: FileKind): string {
  return labelByKind[kind]
}
