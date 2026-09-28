<script setup lang="ts">
const props = defineProps<{ price: number; fair: number | null; comparables: { id: number; price: number }[] }>()
const range = computed(() => {
  const all = [props.price, ...props.comparables.map(c => c.price), ...(props.fair ? [props.fair] : [])]
  const lo = Math.min(...all), hi = Math.max(...all)
  const pad = (hi - lo) * 0.08 || lo * 0.05
  return [lo - pad, hi + pad] as const
})
// RTL reading: cheaper on the right.
const pos = (p: number) => `${((range.value[1] - p) / (range.value[1] - range.value[0])) * 100}%`
</script>

<template>
  <div class="strip" role="img" :aria-label="`قیمت این خودرو در میان ${comparables.length} خودروی مشابه`">
    <div class="axis" />
    <span v-for="c in comparables" :key="c.id" class="dot" :style="{ insetInlineStart: pos(c.price) }" :title="toman(c.price)" />
    <span v-if="fair" class="median" :style="{ insetInlineStart: pos(fair) }"><em>میانه {{ toman(fair) }}</em></span>
    <span class="me" :style="{ insetInlineStart: pos(price) }"><em>این خودرو {{ toman(price) }}</em></span>
    <div class="ends"><small>ارزان‌تر</small><small>گران‌تر</small></div>
  </div>
</template>

<style scoped>
.strip { position: relative; height: 92px; margin: 8px 12px 0; }
.axis { position: absolute; top: 44px; inset-inline: 0; height: 2px; background: var(--border); }
.dot, .me, .median { position: absolute; top: 38px; transform: translateX(50%); }
.dot { width: 12px; height: 12px; border-radius: 50%; background: var(--muted); opacity: .55; top: 39px; }
.median { width: 2px; height: 26px; top: 32px; background: var(--text); }
.median em { position: absolute; top: -24px; transform: translateX(50%); white-space: nowrap; font-style: normal; font-size: .8rem; }
.me { width: 16px; height: 16px; border-radius: 50%; background: var(--accent); top: 37px; }
.me em { position: absolute; top: 22px; transform: translateX(50%); white-space: nowrap; font-style: normal; font-size: .8rem; color: var(--accent); font-weight: 700; }
.ends { position: absolute; bottom: 0; inset-inline: 0; display: flex; justify-content: space-between; color: var(--muted); }
</style>
