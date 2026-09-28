<script setup lang="ts">
const props = defineProps<{ offer: any }>()
const LABELS: Record<string, string> = {
  great: 'زیر قیمت', fair: 'منصفانه', overpriced: 'گران', suspicious: 'مشکوک', unknown: 'داده کافی نیست',
}
const EXCLUSIONS: Record<string, string> = {
  instalment: 'قسطی / لیزینگی', presale: 'حواله / پیش‌فروش', placeholder: 'قیمت نامعتبر',
}
const label = computed(() => (props.offer.exclusion ? EXCLUSIONS[props.offer.exclusion] : LABELS[props.offer.verdict]))
const kind = computed(() => (props.offer.exclusion ? 'unknown' : props.offer.verdict))
const tip = computed(() => {
  const o = props.offer
  if (o.exclusion) return 'این آگهی در قیمت‌گذاری منصفانه حساب نمی‌شود'
  if (o.verdict === 'unknown') return 'کمتر از ۵ خودروی مشابه برای مقایسه پیدا شد'
  if (o.verdict === 'suspicious') return `بیش از ۲۵٪ زیر قیمت منصفانه (${toman(o.fair_price)}) — احتمال کلاهبرداری یا ایراد پنهان`
  const pct = Math.round((o.p_cheaper ?? 0) * 100)
  return `ارزان‌تر از ${fa(pct)}٪ خودروهای مشابه · قیمت منصفانه ${toman(o.fair_price)}`
})
</script>

<template>
  <span class="badge" :class="kind" :title="tip">{{ label }}</span>
</template>

<style scoped>
.badge { font-size: .8rem; font-weight: 500; padding: 1px 10px; border-radius: 999px; white-space: nowrap; cursor: help; }
.great { background: var(--good-soft); color: var(--good); }
.fair { background: var(--neutral-soft); color: var(--text); }
.overpriced { background: var(--bad-soft); color: var(--bad); }
.suspicious { background: var(--warn-soft); color: var(--warn); }
.unknown { background: var(--neutral-soft); color: var(--muted); }
</style>
