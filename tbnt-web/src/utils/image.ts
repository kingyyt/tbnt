export const getImageUrl = (path: string | null | undefined) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const baseUrl = import.meta.env.VITE_API_ORIGIN || 'http://localhost:8000'
  return `${baseUrl}${path}`
}
