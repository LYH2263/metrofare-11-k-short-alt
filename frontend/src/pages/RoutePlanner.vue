<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const stations = ref([])
const start = ref('A1')
const end = ref('A3')
const out = ref(null)
onMounted(async () => { stations.value = (await getJSON('/api/stations')).items })
const nameOf = (code) => stations.value.find(s => s.code === code)?.name ?? code
const fmtPath = (p) => p ? p.map(nameOf).join(' → ') : ''
const run = async () => { out.value = await postJSON('/api/quote', { start: start.value, end: end.value, persist: true }) }
</script>
<template>
  <div class="page"><h1>最短 / 次短站数票价对照</h1>
    <div class="panel">
      <select v-model="start"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      →
      <select v-model="end"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      <button @click="run">试算</button>
      <span v-if="out && out.run_id" class="muted">（已按最短路写入试算记录 #{{ out.run_id }}，次短仅展示）</span>
    </div>
    <div v-if="out" class="panel">
      <p v-if="!out.reachable" class="muted">不可达</p>
      <div v-else class="compare">
        <div class="route-card">
          <h3>最短路</h3>
          <p class="route-path">{{ fmtPath(out.path) }}</p>
          <p>站数 {{ out.hops }} · 票价 <span class="hero-num">¥{{ out.fare }}</span></p>
        </div>
        <div class="route-card">
          <h3>次短路（站数严格更多）</h3>
          <template v-if="out.second">
            <p class="route-path">{{ fmtPath(out.second.path) }}</p>
            <p>站数 {{ out.second.hops }} · 票价 <span class="hero-num">¥{{ out.second.fare }}</span></p>
          </template>
          <p v-else class="muted">不存在严格更长的简单路</p>
        </div>
      </div>
    </div>
  </div>
</template>
