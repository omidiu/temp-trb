<script setup lang="ts">
const text = ref('')
const meta = await useMeta()
const EXAMPLES = [
  'ماشین خانوادگی تا ۸۰۰ میلیون، خیلی کم‌مصرف',
  'برای اسنپ، دوگانه‌سوز، مدل ۹۸ به بالا',
  '۲۰۶ یا کوییک تا ۶۰۰ میلیون، بدون رنگ',
  'فقط اتوماتیک زیر ۳۰۰ میلیون',
]
const go = (q: string) => q.trim() && navigateTo({ path: '/search', query: { q: q.trim() } })
</script>

<template>
  <section class="hero">
    <h1>بگو چه ماشینی لازم داری</h1>
    <p class="muted">آگهی‌های دیوار و باما را یکجا می‌گردیم، تکراری‌ها را یکی می‌کنیم و می‌گوییم کدام قیمت منصفانه است.</p>
    <form class="card box" @submit.prevent="go(text)">
      <textarea v-model="text" class="input" rows="2" :placeholder="EXAMPLES[0]" @keydown.enter.exact.prevent="go(text)" />
      <button class="btn">جستجو</button>
    </form>
    <div class="row">
      <span class="muted">مثلاً:</span>
      <button v-for="e in EXAMPLES" :key="e" class="pill" @click="go(e)">{{ e }}</button>
    </div>
    <div class="row">
      <span class="muted">یا بر اساس نیاز:</span>
      <button v-for="(n, k) in meta.needs" :key="k" class="pill need" @click="go(`ماشین ${n.label}`)">{{ n.label }}</button>
    </div>
  </section>
</template>

<style scoped>
.hero { margin-top: 32px; display: grid; gap: 14px; }
h1 { margin: 0; font-size: 1.8rem; }
.box { display: flex; gap: 8px; align-items: stretch; }
textarea { resize: none; }
.row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.pill { border: 1px solid var(--border); background: var(--surface); color: var(--text); border-radius: 999px; padding: 4px 12px; cursor: pointer; }
.pill.need { border-color: var(--accent); color: var(--accent); }
@media (max-width: 520px) { .box { flex-direction: column; } }
</style>
