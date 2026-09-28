<script setup lang="ts">
const route = useRoute()
const api = useApi()
const meta = await useMeta()
const ranked = useRanked()
const { data: offer } = await useAsyncData(`offer-${route.params.id}`, () => api<any>(`/offers/${route.params.id}`))
const rankedRow = computed(() => ranked.value[Number(route.params.id)])

const BODY: Record<string, string> = { sedan: 'سدان', hatchback: 'هاچبک', crossover: 'کراس‌اوور', suv: 'شاسی‌بلند', pickup: 'وانت', other: 'سایر' }
const COND: Record<string, string> = { clean: 'بدون رنگ', minor: 'رنگ جزئی', major: 'رنگ زیاد / تصادفی' }
const SOURCES: Record<string, string> = { divar: 'دیوار', bama: 'باما' }
const CONF: Record<string, string> = { high: 'زیاد', medium: 'متوسط', low: 'کم' }
const prefLabel = (k: string) => (k.startsWith('like:') ? `مشابه ${meta.families[k.slice(5)]}` : meta.preferences[k])
const specs = computed(() => {
  const o = offer.value, v = o.vehicle
  return [
    ['مدل', fa(o.year)], ['کارکرد', km(o.mileage)], ['بدنه', COND[o.body_condition] ?? 'نامشخص'],
    ['گیربکس', o.gearbox === 'automatic' ? 'اتوماتیک' : 'دنده‌ای'], ['سوخت', o.fuel_type === 'dual' ? 'دوگانه‌سوز' : 'بنزینی'],
    ['نوع بدنه', BODY[v.body_type]], ['موتور', v.engine_cc ? `${fa(v.engine_cc)} سی‌سی` : '—'],
    ['مصرف ترکیبی', v.fuel_consumption ? `${fa(v.fuel_consumption)} لیتر` : '—'],
    ['ایربگ', v.airbags != null ? fa(v.airbags) : '—'], ['ABS', v.abs ? 'دارد' : v.abs === false ? 'ندارد' : '—'],
  ]
})
</script>

<template>
  <section v-if="offer" class="detail">
    <a href="#" class="muted back" @click.prevent="$router.back()">← بازگشت به نتایج</a>
    <header class="card head">
      <img v-if="offer.image_url" :src="offer.image_url" alt="" class="photo" />
      <div>
        <h1>{{ offer.vehicle.name_fa }} <small class="muted">مدل {{ fa(offer.year) }}</small></h1>
        <p class="price">{{ toman(offer.price) }} تومان <VerdictBadge :offer="offer" /></p>
        <p v-if="offer.fair_price" class="muted">
          قیمت منصفانه (میانهٔ قیمت آگهی‌های مشابه): {{ toman(offer.fair_price) }} ·
          {{ fa(offer.comparables.length) }} خودروی مشابه · اطمینان {{ CONF[offer.confidence] }}
        </p>
      </div>
    </header>

    <div v-if="offer.comparables.length" class="card">
      <h2>جایگاه قیمت در میان خودروهای مشابه</h2>
      <PriceStrip :price="offer.price" :fair="offer.fair_price" :comparables="offer.comparables" />
    </div>

    <div v-if="rankedRow" class="card">
      <h2>چرا این رتبه؟ <small class="muted">امتیاز {{ fa(Math.round(rankedRow.score * 100)) }}٪</small></h2>
      <div class="bars">
        <div class="bar-row">
          <span>منصفانه بودن قیمت <small class="muted">×۲</small></span>
          <div class="bar"><i :style="{ width: `${rankedRow.deal * 100}%` }" /></div>
          <span>{{ fa(Math.round(rankedRow.deal * 100)) }}٪</span>
        </div>
        <div v-for="b in rankedRow.breakdown" :key="b.key" class="bar-row">
          <span>{{ prefLabel(b.key) }} <small class="muted">×{{ fa(b.weight) }}{{ b.origin.startsWith('need:') ? ` · ${meta.needs[b.origin.slice(5)]?.label}` : '' }}</small></span>
          <div class="bar" :class="{ unknown: !b.known }"><i :style="{ width: `${b.score * 100}%` }" /></div>
          <span>{{ b.known ? `${fa(Math.round(b.score * 100))}٪` : 'نامشخص' }}</span>
        </div>
      </div>
      <p class="muted formula">امتیاز = (۲ × قیمت + مجموع وزن × امتیاز هر ترجیح) ÷ (۲ + مجموع وزن‌ها)</p>
    </div>

    <div class="card">
      <h2>مشخصات</h2>
      <dl class="specs"><template v-for="[k, v] in specs" :key="k"><dt>{{ k }}</dt><dd>{{ v }}</dd></template></dl>
      <p v-if="offer.model_stats?.depreciation != null" class="muted">
        این مدل به‌طور میانگین سالی {{ fa(Math.round(offer.model_stats.depreciation * 1000) / 10) }}٪ افت قیمت دارد (از روی آگهی‌ها).
      </p>
    </div>

    <div class="card">
      <h2>آگهی‌ها</h2>
      <ul class="listings">
        <li v-for="l in offer.listings" :key="l.url">
          <a :href="l.url" target="_blank" rel="noopener">{{ SOURCES[l.source] ?? l.source }} — {{ toman(l.price) }} تومان ↗</a>
          <p v-if="l.description" class="muted desc">{{ l.description }}</p>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.detail { display: grid; gap: 14px; }
.back { text-decoration: none; }
.head { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
.photo { width: 220px; max-width: 100%; border-radius: 10px; }
h1 { margin: 0; font-size: 1.4rem; }
h2 { margin: 0 0 10px; font-size: 1.05rem; }
.price { font-size: 1.2rem; font-weight: 700; margin: 4px 0; display: flex; gap: 10px; align-items: center; }
.bars { display: grid; gap: 8px; }
.bar-row { display: grid; grid-template-columns: minmax(120px, 220px) 1fr 56px; gap: 10px; align-items: center; font-size: .9rem; }
.bar { height: 8px; background: var(--neutral-soft); border-radius: 99px; overflow: hidden; }
.bar i { display: block; height: 100%; background: var(--accent); border-radius: 99px; }
.bar.unknown i { background: var(--muted); opacity: .4; }
.formula { font-size: .8rem; margin: 10px 0 0; }
.specs { display: grid; grid-template-columns: max-content 1fr; gap: 4px 16px; margin: 0; }
dt { color: var(--muted); }
dd { margin: 0; }
.listings { margin: 0; padding: 0; list-style: none; display: grid; gap: 10px; }
.desc { white-space: pre-line; font-size: .85rem; margin: 4px 0 0; }
@media (max-width: 520px) { .bar-row { grid-template-columns: 1fr 1fr 48px; } }
</style>
