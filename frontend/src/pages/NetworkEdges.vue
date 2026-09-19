<script setup>
import { onMounted, ref } from 'vue'
import { delJSON, getJSON } from '../api'
const items = ref([])
const load = async () => { items.value = (await getJSON('/api/edges')).items }
onMounted(load)
const remove = async (e) => {
  await delJSON(`/api/edges?a=${encodeURIComponent(e.a)}&b=${encodeURIComponent(e.b)}`)
  await load()
}
</script>
<template>
  <div class="page"><h1>邻接区间</h1>
    <ul><li v-for="(e,i) in items" :key="i">{{ e.a }} — {{ e.b }} <button @click="remove(e)">删除</button></li></ul>
  </div>
</template>
