export function delay(ms = 300): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export function randomDelay(minMs = 200, maxMs = 500): Promise<void> {
  return delay(minMs + Math.random() * (maxMs - minMs))
}
