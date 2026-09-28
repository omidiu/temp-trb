// Same-length normalization so indices in the normalized text map back to the original.
const norm = (s: string) =>
  s.replace(/[۰-۹]/g, d => String('۰۱۲۳۴۵۶۷۸۹'.indexOf(d)))
    .replace(/[٠-٩]/g, d => String('٠١٢٣٤٥٦٧٨٩'.indexOf(d)))
    .replace(/‌/g, ' ').replace(/ي/g, 'ی').replace(/ك/g, 'ک')

/** Split `text` into segments, marking the ones that match any span. */
export function highlight(text: string, spans: string[]) {
  const t = norm(text)
  const marks: [number, number][] = []
  for (const s of spans) {
    const n = norm(s || '').trim()
    if (!n) continue
    const i = t.indexOf(n)
    if (i >= 0) marks.push([i, i + n.length])
  }
  marks.sort((a, b) => a[0] - b[0])
  const out: { text: string; mark: boolean }[] = []
  let pos = 0
  for (const [a, b] of marks) {
    if (a < pos) continue
    if (a > pos) out.push({ text: text.slice(pos, a), mark: false })
    out.push({ text: text.slice(a, b), mark: true })
    pos = b
  }
  if (pos < text.length) out.push({ text: text.slice(pos), mark: false })
  return out
}
