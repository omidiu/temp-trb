<script setup lang="ts">
import type { Meta } from '~/composables/useMeta'

const props = defineProps<{ intent: any; meta: Meta }>()
const emit = defineEmits<{ change: [intent: any] }>()

const openNeed = ref<string | null>(null)
const adding = ref(false)
const editingBudget = ref(false)
const budgetInput = ref<number | null>(null)

function explicit() {
  const i = props.intent
  return JSON.parse(JSON.stringify({
    text: i.text, constraints: i.constraints, preferences: i.preferences, needs: i.needs, spans: i.spans, source: 'edited',
  }))
}
function update(fn: (i: any) => void) {
  const i = explicit()
  fn(i)
  emit('change', i)
}

const c = computed(() => props.intent.constraints)
const constraintChips = computed(() => {
  const out: { key: string; label: string; clear: (i: any) => void }[] = []
  const x = c.value
  const F = props.meta.families
  if (x.max_price) out.push({ key: 'max_price', label: `بودجه ≤ ${toman(x.max_price)}`, clear: i => (i.constraints.max_price = null) })
  if (x.min_price) out.push({ key: 'min_price', label: `قیمت ≥ ${toman(x.min_price)}`, clear: i => (i.constraints.min_price = null) })
  if (x.city) out.push({ key: 'city', label: 'تهران', clear: i => (i.constraints.city = null) })
  if (x.min_year) out.push({ key: 'min_year', label: `مدل ≥ ${fa(x.min_year)}`, clear: i => (i.constraints.min_year = null) })
  if (x.max_year) out.push({ key: 'max_year', label: `مدل ≤ ${fa(x.max_year)}`, clear: i => (i.constraints.max_year = null) })
  if (x.max_mileage) out.push({ key: 'max_mileage', label: `کارکرد ≤ ${fa(x.max_mileage)} کیلومتر`, clear: i => (i.constraints.max_mileage = null) })
  if (x.models?.length) out.push({ key: 'models', label: `فقط ${x.models.map((m: string) => F[m]).join('، ')}`, clear: i => (i.constraints.models = []) })
  if (x.exclude_models?.length) out.push({ key: 'exclude_models', label: `نه ${x.exclude_models.map((m: string) => F[m]).join('، ')}`, clear: i => (i.constraints.exclude_models = []) })
  if (x.gearbox) out.push({ key: 'gearbox', label: x.gearbox === 'automatic' ? 'فقط اتوماتیک' : 'فقط دنده‌ای', clear: i => (i.constraints.gearbox = null) })
  if (x.fuel_type) out.push({ key: 'fuel_type', label: x.fuel_type === 'dual' ? 'فقط دوگانه‌سوز' : 'فقط بنزینی', clear: i => (i.constraints.fuel_type = null) })
  if (x.body_condition) out.push({ key: 'body_condition', label: props.meta.conditions[x.body_condition], clear: i => (i.constraints.body_condition = null) })
  return out
})

const prefLabel = (p: any) => (p.key === 'like' ? `مشابه ${props.meta.families[p.value]}` : props.meta.preferences[p.key])
const segments = computed(() => {
  const i = props.intent
  const spans = [...Object.values(i.spans || {}), ...i.preferences.map((p: any) => p.span), ...i.needs.map((n: any) => n.span)]
  return highlight(i.text || '', spans as string[])
})
const dropped = (need: string) => props.intent.dropped.filter((d: any) => d.need === need)

function saveBudget() {
  const v = budgetInput.value
  update(i => (i.constraints.max_price = v ? Math.round(v * 1_000_000) : null))
  editingBudget.value = false
}
function add(value: string) {
  adding.value = false
  const [kind, key] = value.split(':')
  update(i => {
    if (kind === 'need' && !i.needs.some((n: any) => n.key === key)) i.needs.push({ key, off: [] })
    if (kind === 'pref' && !i.preferences.some((p: any) => p.key === key)) i.preferences.push({ key, strength: 'normal' })
  })
}
</script>

<template>
  <div class="chipbar">
    <p v-if="intent.text" class="said">
      <template v-for="(s, n) in segments" :key="n"><mark v-if="s.mark">{{ s.text }}</mark><span v-else>{{ s.text }}</span></template>
      <small class="muted"> · {{ intent.source === 'llm' ? 'فهمیده‌شده با هوش مصنوعی' : intent.source === 'keywords' ? 'فهمیده‌شده با کلیدواژه' : 'ویرایش‌شده' }}</small>
    </p>
    <div class="chips">
      <span v-for="ch in constraintChips" :key="ch.key" class="chip hard">
        {{ ch.label }} <button aria-label="حذف" @click="update(ch.clear)">×</button>
      </span>
      <span v-if="!c.max_price" class="chip empty">
        <template v-if="!editingBudget"><button class="link" @click="editingBudget = true">بودجه؟</button></template>
        <form v-else @submit.prevent="saveBudget"><input v-model.number="budgetInput" type="number" placeholder="میلیون تومان" class="mini" autofocus /></form>
      </span>

      <span v-for="(p, n) in intent.preferences" :key="`p${n}`" class="chip soft" :class="{ strong: p.strength === 'strong' }">
        <button class="link" :title="p.strength === 'strong' ? 'مهم' : 'برای مهم کردن کلیک کنید'"
          @click="update(i => (i.preferences[n].strength = p.strength === 'strong' ? 'normal' : 'strong'))">
          {{ p.strength === 'strong' ? '★ ' : '' }}{{ prefLabel(p) }}
        </button>
        <button aria-label="حذف" @click="update(i => i.preferences.splice(n, 1))">×</button>
      </span>

      <span v-for="(need, n) in intent.needs" :key="`n${n}`" class="chip need">
        <button class="link" @click="openNeed = openNeed === need.key ? null : need.key">{{ meta.needs[need.key]?.label }} ▾</button>
        <button aria-label="حذف" @click="update(i => i.needs.splice(n, 1))">×</button>
        <div v-if="openNeed === need.key" class="popover card">
          <p class="muted">«{{ meta.needs[need.key].label }}» یعنی:</p>
          <label v-for="r in meta.needs[need.key].recipe" :key="r.key" class="recipe"
            :class="{ dropped: dropped(need.key).some((d: any) => d.key === r.key) }">
            <input type="checkbox" :checked="!need.off?.includes(r.key)"
              @change="update(i => { const o = i.needs[n].off ||= []; const k = o.indexOf(r.key); k >= 0 ? o.splice(k, 1) : o.push(r.key) })" />
            {{ r.strength === 'strong' ? '★ ' : '' }}{{ meta.preferences[r.key] }}
            <small v-for="d in dropped(need.key).filter((d: any) => d.key === r.key)" :key="d.key" class="muted"> — {{ d.reason }}</small>
          </label>
        </div>
      </span>

      <span class="chip add">
        <button v-if="!adding" class="link" @click="adding = true">+ افزودن</button>
        <select v-else class="mini" @change="add(($event.target as HTMLSelectElement).value)">
          <option value="">انتخاب کنید…</option>
          <optgroup label="نیاز">
            <option v-for="(v, k) in meta.needs" :key="k" :value="`need:${k}`">{{ v.label }}</option>
          </optgroup>
          <optgroup label="ترجیح">
            <option v-for="(v, k) in meta.preferences" :key="k" :value="`pref:${k}`" v-show="k !== 'like'">{{ v }}</option>
          </optgroup>
        </select>
      </span>
    </div>
  </div>
</template>

<style scoped>
.chipbar { display: grid; gap: 8px; }
.said { margin: 0; font-size: 1.05rem; }
mark { background: var(--accent-soft); color: inherit; border-radius: 4px; padding: 0 2px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { position: relative; display: inline-flex; align-items: center; gap: 4px; border-radius: 999px; padding: 2px 10px; font-size: .9rem; border: 1px solid var(--border); background: var(--surface); }
.chip button { background: none; border: 0; color: inherit; cursor: pointer; padding: 0 2px; font: inherit; }
.chip.hard { background: var(--text); color: var(--bg); border-color: var(--text); }
.chip.soft.strong { border-color: var(--accent); color: var(--accent); font-weight: 500; }
.chip.need { border-color: var(--accent); background: var(--accent-soft); }
.chip.empty, .chip.add { border-style: dashed; color: var(--muted); }
.mini { font: inherit; padding: 2px 6px; border: 1px solid var(--border); border-radius: 6px; background: var(--surface); color: var(--text); width: 140px; }
.popover { position: absolute; top: 110%; inset-inline-start: 0; z-index: 10; width: 280px; display: grid; gap: 4px; padding: 12px; }
.popover p { margin: 0 0 4px; }
.recipe { display: flex; gap: 6px; align-items: baseline; font-size: .9rem; }
.recipe.dropped { text-decoration: line-through; color: var(--muted); }
</style>
