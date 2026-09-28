const nf = new Intl.NumberFormat('fa-IR')

export const fa = (n: number | string | null | undefined) =>
  n === null || n === undefined ? '' : typeof n === 'number' ? nf.format(n) : n.replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[+d])

/** 495_000_000 → "۴۹۵ میلیون"; 1_250_000_000 → "۱٫۲۵ میلیارد" */
export function toman(n: number | null | undefined) {
  if (n === null || n === undefined) return ''
  if (n >= 1_000_000_000) return `${fa(+(n / 1_000_000_000).toFixed(2))} میلیارد`
  return `${fa(Math.round(n / 1_000_000))} میلیون`
}

export const km = (n: number) => `${fa(n)} کیلومتر`
