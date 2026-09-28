<script setup lang="ts">
defineProps<{ offer: any }>()
</script>

<template>
  <article class="card offer">
    <img v-if="offer.image_url" :src="offer.image_url" alt="" class="thumb" loading="lazy" />
    <div v-else class="thumb placeholder" />
    <div class="body">
      <h3>{{ offer.vehicle.name_fa }}</h3>
      <p class="muted">مدل {{ fa(offer.year) }} · {{ km(offer.mileage) }}</p>
      <div class="tags">
        <VerdictBadge :offer="offer" />
        <span v-if="offer.sources?.length > 1" class="tag">روی {{ fa(offer.sources.length) }} سایت</span>
      </div>
    </div>
    <div class="price">{{ toman(offer.price) }} <small>تومان</small></div>
  </article>
</template>

<style scoped>
.offer { display: flex; align-items: center; gap: 14px; }
.thumb { width: 96px; height: 72px; object-fit: cover; border-radius: 8px; flex: none; background: var(--neutral-soft); }
.body { flex: 1; min-width: 0; }
h3 { margin: 0; font-size: 1.05rem; }
p { margin: 0; }
.tags { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 4px; }
.tag { font-size: .8rem; padding: 1px 8px; border-radius: 999px; background: var(--neutral-soft); }
.price { font-weight: 700; white-space: nowrap; }
@media (max-width: 520px) {
  .offer { flex-wrap: wrap; }
  .price { width: 100%; }
}
</style>
