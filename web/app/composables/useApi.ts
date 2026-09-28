export function useApi() {
  const base = useRuntimeConfig().public.apiBase
  return <T>(path: string, body?: unknown) =>
    $fetch<T>(`${base}${path}`, body === undefined ? {} : { method: 'POST', body })
}
