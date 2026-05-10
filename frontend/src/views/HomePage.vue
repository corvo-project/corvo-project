<template>
  <div class="container text-center mt-5" id="home">
    <div class="col-lg-6 offset-lg-3 col-12">
      <img src="/corvo.png" alt="Logo" style="max-width: 200px;">
      <h1>CorVo</h1>
      <h2 class="mb-4">Corpora for Volcanoes</h2>
      <input type="text" class="form-control" placeholder="Search..." v-model="query" @keyup.enter="search">
    </div>
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  
  const query = ref('')
  const router = useRouter()
  
  function search() {
    const trimmed = query.value.trim()
    if (!trimmed) return
    router.push({ name: 'SearchResults', query: { q: trimmed, page: 1 } })
  }
</script>
