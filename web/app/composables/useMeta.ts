export interface Meta {
  needs: Record<string, { label: string; recipe: { key: string; strength: string }[] }>
  preferences: Record<string, string>
  families: Record<string, string>
  conditions: Record<string, string>
}

let cache: Promise<Meta> | null = null
export function useMeta() {
  const api = useApi()
  cache ??= api<Meta>('/needs')
  return cache
}
