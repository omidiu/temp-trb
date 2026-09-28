<script setup lang="ts">
const route = useRoute()
const api = useApi()
const max = computed(() => (route.query.max ? Number(route.query.max) * 1_000_000 : null))
const { data, pending } = await useAsyncData('search', () =>
  api<{ results: any[] }>('/search', { intent: { constraints: max.value ? { max_price: max.value } : {} } }),
  { watch: [max] },
)
</script>

<template>
  <section>
    <p class="muted" v-if="max">بودجه تا {{ toman(max) }} تومان</p>
    <p v-if="pending" class="muted">در حال جستجو…</p>
    <div v-else class="list">
      <OfferCard v-for="o in data?.results" :key="o.id" :offer="o" />
      <p v-if="!data?.results.length" class="muted">خودرویی پیدا نشد.</p>
    </div>
  </section>
</template>

<style scoped>
.list { display: grid; gap: 12px; }
</style>
