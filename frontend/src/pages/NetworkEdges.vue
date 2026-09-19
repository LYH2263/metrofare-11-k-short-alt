<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, delJSON } from '../api'
const items = ref([])
const stations = ref([])
const a = ref('A1')
const b = ref('A3')
const err = ref('')
onMounted(load)
async function load() {
  items.value = (await getJSON('/api/edges')).items
  if (!stations.value.length) stations.value = (await getJSON('/api/stations')).items
}
const nameOf = (code) => stations.value.find(s => s.code === code)?.name ?? code
async function addEdge() {
  err.value = ''
  try {
    const r = await postJSON('/api/edges', { a: a.value, b: b.value })
    items.value = r.items
  } catch (e) { err.value = String(e.message ?? e) }
}
async function removeEdge(x, y) {
  err.value = ''
  try {
    const r = await delJSON(`/api/edges/${encodeURIComponent(x)}/${encodeURIComponent(y)}`)
    items.value = r.items
  } catch (e) { err.value = String(e.message ?? e) }
}
</script>
<template>
  <div class="page"><h1>邻接区间</h1>
    <div class="panel">
      <p class="muted">新增邻接可构成环线以产生次短路；删除最短路上的边后，原次短可能成为新最短。</p>
      <select v-model="a"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      —
      <select v-model="b"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      <button @click="addEdge">新增邻接</button>
      <span v-if="err" class="muted">{{ err }}</span>
    </div>
    <div class="panel">
      <div v-for="(e,i) in items" :key="i" class="edge-row">
        <span class="edge-name">{{ e.a }} {{ nameOf(e.a) }} — {{ e.b }} {{ nameOf(e.b) }}</span>
        <button class="danger" @click="removeEdge(e.a, e.b)">删除</button>
      </div>
      <p v-if="!items.length" class="muted">暂无邻接区间</p>
    </div>
  </div>
</template>
