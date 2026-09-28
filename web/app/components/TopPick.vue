<script setup lang="ts">
defineProps<{ offer: any; explanation: any; loading: boolean }>()
const METHOD: Record<string, string> = {
  llm: 'نوشته‌شده با هوش مصنوعی، فقط از روی اعداد رتبه‌بندی',
  template: 'متن الگو از روی اعداد رتبه‌بندی',
  template_after_llm_rejected: 'متن هوش مصنوعی رد شد (عدد ساختگی داشت)؛ متن الگو نمایش داده شد',
}
</script>

<template>
  <section class="card top">
    <p class="kicker">بهترین انتخاب برای شما</p>
    <OfferCard :offer="offer" class="inner" />
    <div class="why">
      <h3>چرا این و چرا بقیه نه؟</h3>
      <p v-if="loading" class="muted">در حال نوشتن توضیح…</p>
      <template v-else-if="explanation?.text">
        <p class="text">{{ explanation.text }}</p>
        <details>
          <summary class="muted">{{ METHOD[explanation.method] }} · دادهٔ پشت این توضیح</summary>
          <pre dir="ltr">{{ JSON.stringify(explanation.fact_sheet, null, 1) }}</pre>
        </details>
      </template>
    </div>
  </section>
</template>

<style scoped>
.top { border-color: var(--accent); display: grid; gap: 10px; }
.kicker { margin: 0; color: var(--accent); font-weight: 700; }
.inner { border: 0; padding: 0; }
.why h3 { margin: 0 0 4px; font-size: 1rem; }
.text { margin: 0; line-height: 2; }
details { margin-top: 8px; }
summary { cursor: pointer; font-size: .85rem; }
pre { font-size: .75rem; max-height: 260px; overflow: auto; background: var(--neutral-soft); padding: 10px; border-radius: 8px; text-align: left; }
</style>
