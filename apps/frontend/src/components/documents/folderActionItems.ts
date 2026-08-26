import type { ActionMenuItem } from '@/components/common/ActionsMenu.vue'

export const folderActionItems: ActionMenuItem[] = [
  { key: 'open', label: 'Ouvrir', icon: 'fr-icon-folder-2-line' },
  { key: 'rename', label: 'Renommer', icon: 'fr-icon-edit-line' },
  { key: 'share', label: 'Partager', icon: 'fr-icon-share-line' },
  { key: 'new-subfolder', label: 'Créer un sous-dossier', icon: 'fr-icon-add-circle-line' },
  { key: 'delete', label: 'Supprimer', icon: 'fr-icon-delete-bin-line', danger: true },
]

// Same menu, minus "Ouvrir" - meaningless when it's the folder you're
// already looking at (used for the current folder's own "..." menu).
export const currentFolderActionItems: ActionMenuItem[] = folderActionItems.filter((item) => item.key !== 'open')
