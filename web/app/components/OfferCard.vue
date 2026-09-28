<script setup lang="ts">
defineProps<{ offer: any }>()
</script>

<template>
  <article class="card offer">
    <div>
      <h3>{{ offer.vehicle.name_fa }}</h3>
      <p class="muted">مدل {{ fa(offer.year) }} · {{ km(offer.mileage) }}</p>
    </div>
    <div class="price">{{ toman(offer.price) }} <small>تومان</small></div>
  </article>
</template>

<style scoped>
.offer { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
h3 { margin: 0; font-size: 1.05rem; }
p { margin: 0; }
.price { font-weight: 700; white-space: nowrap; }
</style>
