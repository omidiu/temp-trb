<script setup lang="ts">
const budget = ref<number | null>(null)
function go() {
  navigateTo({ path: '/search', query: budget.value ? { max: String(budget.value) } : {} })
}
</script>

<template>
  <section class="hero card">
    <h1>ماشین مناسبت رو پیدا کن</h1>
    <form @submit.prevent="go" class="row">
      <input v-model.number="budget" class="input" type="number" placeholder="حداکثر بودجه (میلیون تومان)" />
      <button class="btn">جستجو</button>
    </form>
  </section>
</template>

<style scoped>
.hero { margin-top: 24px; }
.row { display: flex; gap: 8px; }
</style>
