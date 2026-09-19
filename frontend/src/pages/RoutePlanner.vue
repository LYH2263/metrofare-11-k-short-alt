<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const stations = ref([])
const start = ref('A1')
const end = ref('B2')
const out = ref(null)
onMounted(async () => { stations.value = (await getJSON('/api/stations')).items })
const run = async () => { out.value = await postJSON('/api/quote', { start: start.value, end: end.value, persist: true }) }
</script>
<template>
  <div class="page"><h1>最短站数票价</h1>
    <div class="panel">
      <select v-model="start"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      →
      <select v-model="end"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      <button @click="run">试算</button>
    </div>
    <div v-if="out" class="compare">
      <div class="panel"><h2>最短</h2>
        <template v-if="out.reachable">
          <p>站数 {{ out.hops }} · 票价 <span class="hero-num">¥{{ out.fare }}</span></p>
          <p class="muted">{{ out.path.join(' → ') }}</p>
        </template>
        <p v-else class="muted">不可达</p>
      </div>
      <div class="panel"><h2>次短</h2>
        <template v-if="out.reachable">
          <template v-if="out.alt">
            <p>站数 {{ out.alt.hops }} · 票价 <span class="hero-num">¥{{ out.alt.fare }}</span></p>
            <p class="muted">{{ out.alt.path.join(' → ') }}</p>
          </template>
          <p v-else class="muted">无严格更长的简单路</p>
        </template>
        <p v-else class="muted">—</p>
      </div>
    </div>
  </div>
</template>
