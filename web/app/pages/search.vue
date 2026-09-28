<script setup lang="ts">
const route = useRoute()
const api = useApi()
const meta = await useMeta()

const intent = ref<any>(null)
const results = ref<any[]>([])
const overBudget = ref<any[]>([])
const count = ref(0)
const relaxations = ref<any[]>([])
const ranked = useRanked()
const loading = ref(false)
const text = ref(String(route.query.q || ''))

async function runSearch(explicit: any) {
  loading.value = true
  try {
    const res = await api<any>('/search', { intent: explicit })
    intent.value = res.intent
    results.value = res.results
    overBudget.value = res.over_budget
    count.value = res.count
    relaxations.value = res.relaxations
    ranked.value = Object.fromEntries([...res.results, ...res.over_budget].map((o: any) => [o.id, o]))
  } finally {
    loading.value = false
  }
}
async function parseAndSearch(q: string) {
  loading.value = true
  const parsed = await api<any>('/intent/parse', { text: q })
  await runSearch(parsed)
}
watch(() => route.query.q, q => { text.value = String(q || ''); parseAndSearch(text.value) }, { immediate: true })
function relax(patch: Record<string, unknown>) {
  const i = intent.value
  runSearch({ text: i.text, constraints: { ...i.constraints, ...patch }, preferences: i.preferences, needs: i.needs, spans: i.spans, source: 'edited' })
}
const submit = () => navigateTo({ path: '/search', query: { q: text.value } })
</script>

<template>
  <section class="page">
    <form class="searchbox" @submit.prevent="submit">
      <input v-model="text" class="input" placeholder="چه ماشینی لازم داری؟" />
      <button class="btn">جستجو</button>
    </form>
    <ChipBar v-if="intent" :intent="intent" :meta="meta" @change="runSearch" />
    <p v-if="loading" class="muted">در حال جستجو…</p>
    <template v-else>
      <p v-if="results.length" class="muted">{{ fa(count) }} خودرو، مرتب‌شده بر اساس تطابق با خواسته‌ها و منصفانه بودن قیمت</p>
      <div class="list">
        <OfferCard v-for="o in results" :key="o.id" :offer="o" />
        <div v-if="!results.length" class="card empty">
          <p>با این شرط‌ها خودرویی پیدا نشد.</p>
          <template v-if="relaxations.length">
            <p class="muted">با یک تغییر کوچک:</p>
            <div class="relax">
              <button v-for="r in relaxations" :key="r.label" class="btn ghost" @click="relax(r.patch)">
                {{ r.label }}: {{ fa(r.count) }} خودرو
              </button>
            </div>
          </template>
        </div>
      </div>
      <template v-if="overBudget.length">
        <h2 class="group">کمی بالاتر از بودجه (تا ۱۰٪)</h2>
        <div class="list"><OfferCard v-for="o in overBudget" :key="o.id" :offer="o" /></div>
      </template>
    </template>
  </section>
</template>

<style scoped>
.page { display: grid; gap: 16px; }
.searchbox { display: flex; gap: 8px; }
.list { display: grid; gap: 12px; }
.group { font-size: 1.1rem; margin: 12px 0 0; }
.empty p { margin: 0 0 8px; }
.relax { display: flex; flex-wrap: wrap; gap: 8px; }
.btn.ghost { background: var(--accent-soft); color: var(--accent); }
</style>
