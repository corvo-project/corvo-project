<template>
  <div>
    <div class="container mt-4">
      <h2>Search Results for "{{ route.query.q }}"</h2>
      <p v-if="searching">
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Loading results...
      </p>
      <div v-else>
        <p class="text-muted" v-if="total">
          Showing page {{ page }} of {{ totalPages }} ({{ total }} results)
        </p>
        <ul class="list-group mt-3" v-if="results.length">
          <li v-for="result in results" :key="result.id" class="list-group-item">
            <router-link :to="{ name: 'DetailPage', params: { id: result.document_id, page: result.page_number } }">
              {{ result.author }} - {{ result.title }} - Page {{ result.page_number }}
            </router-link>
            <br/>
            <small class="text-muted" v-html="result.snippet"></small>
          </li>
        </ul>
        <p v-else class="mt-3">No results found for "{{ route.query.q }}".</p>

        <nav v-if="totalPages > 1" class="mt-4" aria-label="Search results pagination">
          <ul class="pagination justify-content-center">
            <li class="page-item" :class="{ disabled: page <= 1 }">
              <button class="page-link" type="button" @click="changePage(page - 1)">Previous</button>
            </li>
            <li
              v-for="p in visiblePages"
              :key="p"
              class="page-item"
              :class="{ active: p === page }"
            >
              <button class="page-link" type="button" @click="changePage(p)">{{ p }}</button>
            </li>
            <li class="page-item" :class="{ disabled: page >= totalPages }">
              <button class="page-link" type="button" @click="changePage(page + 1)">Next</button>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, watch, computed} from 'vue'
import {useRoute, useRouter} from 'vue-router'

const results = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(25)
const route = useRoute()
const router = useRouter()
const searching = ref(false)

const fetchResults = (query, nextPage) => {
  if (!query) {
    results.value = []
    total.value = 0
    searching.value = false
    return
  }
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/'
  searching.value = true
  fetch(`${baseUrl}search?q=${encodeURIComponent(query)}&page=${encodeURIComponent(nextPage)}&page_size=${encodeURIComponent(pageSize.value)}`)
      .then(response => response.json())
      .then(data => {
        results.value = data.results || []
        total.value = data.total || 0
        page.value = data.page || 1
        pageSize.value = data.page_size || pageSize.value
      })
      .catch(error => {
        console.error('Search error:', error)
      })
      .then(() => {
        searching.value = false
      })
}

const totalPages = computed(() => {
  if (!total.value || !pageSize.value) return 0
  return Math.max(1, Math.ceil(total.value / pageSize.value))
})

const visiblePages = computed(() => {
  const maxVisible = 5
  const half = Math.floor(maxVisible / 2)
  let start = Math.max(1, page.value - half)
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  start = Math.max(1, end - maxVisible + 1)
  const pages = []
  for (let p = start; p <= end; p += 1) pages.push(p)
  return pages
})

const changePage = (nextPage) => {
  if (nextPage < 1 || nextPage > totalPages.value) return
  router.push({name: 'SearchResults', query: {q: route.query.q, page: nextPage}})
}

watch(
  () => [route.query.q, route.query.page],
  ([query, nextPage]) => {
    const parsedPage = Number.parseInt(nextPage, 10)
    fetchResults(query, Number.isNaN(parsedPage) ? 1 : parsedPage)
  },
  {immediate: true}
)
</script>
