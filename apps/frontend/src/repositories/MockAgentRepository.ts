import type { AgentActivity, AgentMessage, AgentQueryRequest, AgentResponse } from '@/types'
import { randomDelay } from '@/utils/async'
import { MockSearchRepository } from './MockSearchRepository'
import type { AgentRepository } from './types'

const searchRepository = new MockSearchRepository()

let nextMessageId = 1000

function scopeLabel(scope: AgentQueryRequest['scope']): string {
  if (scope.type === 'all') return 'Tous mes documents'
  if (scope.type === 'folder') return 'ce dossier'
  return 'ce document'
}

export class MockAgentRepository implements AgentRepository {
  async query(request: AgentQueryRequest): Promise<AgentResponse> {
    const searchResponse = await searchRepository.search({ query: request.question, scope: request.scope })

    const activities: AgentActivity[] = [
      { id: 'a-1', label: `Recherche dans ${scopeLabel(request.scope)}`, status: 'done' },
      { id: 'a-2', label: `${searchResponse.results.length} document(s) trouvé(s)`, status: 'done' },
      { id: 'a-3', label: 'Analyse des passages pertinents', status: 'done' },
      { id: 'a-4', label: 'Vérification des sources', status: 'done' },
    ]

    await randomDelay(600, 1400)

    nextMessageId += 1
    const answer =
      searchResponse.results.length > 0
        ? buildAnswer(request.question, searchResponse.results.length)
        : "Je n'ai trouvé aucun document pertinent pour répondre à cette question."

    const message: AgentMessage = {
      id: `am-${nextMessageId}`,
      role: 'agent',
      text: answer,
      createdAt: new Date().toISOString(),
      activities,
      sources: searchResponse.results.slice(0, 4).map((r) => r.source),
    }

    return { message }
  }
}

function buildAnswer(question: string, resultCount: number): string {
  const lower = question.toLowerCase()
  if (lower.includes('résiliation') || lower.includes('resiliation')) {
    return `J'ai identifié ${resultCount} passage(s) évoquant la résiliation. Le contrat ACME initial prévoit un préavis de trois mois, porté à six mois par l'avenant 2025. Le contrat Total permet une résiliation anticipée en cas de manquement.`
  }
  if (lower.includes('durée') || lower.includes('duree')) {
    return `D'après les documents analysés, les contrats ont une durée initiale de deux à trois ans.`
  }
  return `J'ai analysé ${resultCount} passage(s) pertinent(s) pour répondre à votre question.`
}
