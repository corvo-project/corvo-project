<template>
  <div>
    <!-- Search form (collapsed mini-bar or full advanced form) -->
    <div class="border-bottom bg-light">
      <div class="container py-2">

        <!-- Mini collapsed bar (read-only summary) -->
        <div v-if="!formExpanded" class="d-flex align-items-center gap-2 flex-wrap">
          <div class="flex-grow-1 d-flex flex-wrap align-items-center gap-2">
            <span v-if="form.q" class="fw-semibold">"{{ form.q }}"</span>
            <span v-if="form.eventIds.length">
              <span class="text-muted small me-1">Events ({{ form.eventMode }}):</span>
              <span
                v-for="eid in form.eventIds" :key="eid"
                class="badge bg-primary me-1"
              >{{ eventTypes.find(e => e.id === eid)?.description ?? eid }}</span>
            </span>
            <span v-if="form.selectedToponyms.length">
              <span class="text-muted small me-1">Toponyms ({{ form.toponymMode }}):</span>
              <span
                v-for="tv in form.selectedToponyms" :key="tv.id"
                class="badge bg-secondary me-1"
              >{{ tv.name }}</span>
            </span>
            <span v-if="!hasAnyFilter" class="text-muted fst-italic small">No active filters</span>
          </div>
          <button class="btn btn-outline-secondary btn-sm" type="button" @click="formExpanded = true">
            Edit ▾
          </button>
        </div>

        <!-- Full advanced form -->
        <div v-else>
          <form @submit.prevent="submitSearch">
            <div class="row g-3">

              <!-- Free text -->
              <div class="col-12">
                <label class="form-label fw-semibold">Free text search</label>
                <input v-model="form.q" type="text" class="form-control" placeholder="Search...">
              </div>

              <!-- Event types -->
              <div class="col-md-6" v-if="eventTypes.length">
                <label class="form-label fw-semibold">Event types</label>
                <div class="border rounded p-2" style="max-height: 200px; overflow-y: auto;">
                  <div v-for="et in eventTypes" :key="et.id" class="form-check">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      :id="`et-${et.id}`"
                      :value="et.id"
                      v-model="form.eventIds"
                    >
                    <label class="form-check-label" :for="`et-${et.id}`">{{ et.description }}</label>
                  </div>
                </div>
                <div class="mt-1 d-flex gap-3">
                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" id="event-or" value="OR" v-model="form.eventMode">
                    <label class="form-check-label" for="event-or">OR (any)</label>
                  </div>
                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" id="event-and" value="AND" v-model="form.eventMode">
                    <label class="form-check-label" for="event-and">AND (all)</label>
                  </div>
                </div>
              </div>

              <!-- Toponyms chips autocomplete -->
              <div class="col-md-6">
                <label class="form-label fw-semibold">Toponyms</label>
                <div class="position-relative">
                  <div
                    class="form-control d-flex flex-wrap gap-1 align-items-center"
                    style="min-height: 40px; height: auto; cursor: text;"
                    @click="focusToponymInput"
                  >
                    <span
                      v-for="tv in form.selectedToponyms"
                      :key="tv.id"
                      class="badge bg-secondary d-flex align-items-center gap-1"
                    >
                      {{ tv.name }}
                      <button
                        type="button"
                        class="btn-close btn-close-white"
                        style="font-size: 0.6em;"
                        @click.stop="removeToponym(tv.id)"
                      ></button>
                    </span>
                    <input
                      ref="toponymInput"
                      v-model="toponymSearch"
                      type="text"
                      class="border-0 bg-transparent flex-grow-1"
                      style="outline: none; min-width: 120px;"
                      placeholder="Type to search toponyms..."
                      @input="onToponymInput"
                      @keydown.down.prevent="highlightNext"
                      @keydown.up.prevent="highlightPrev"
                      @keydown.enter.prevent="selectHighlighted"
                      @keydown.escape="closeSuggestions"
                      @blur="closeSuggestions"
                    >
                  </div>
                  <ul
                    v-if="toponymSuggestions.length"
                    class="dropdown-menu show w-100"
                    style="max-height: 200px; overflow-y: auto; z-index: 1050;"
                  >
                    <li v-for="(tv, i) in toponymSuggestions" :key="tv.id">
                      <button
                        type="button"
                        class="dropdown-item"
                        :class="{ active: i === highlightedIndex }"
                        @mousedown.prevent="selectToponym(tv)"
                      >
                        {{ tv.name }}
                      </button>
                    </li>
                  </ul>
                </div>
                <div class="mt-1 d-flex gap-3">
                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" id="toponym-or" value="OR" v-model="form.toponymMode">
                    <label class="form-check-label" for="toponym-or">OR (any)</label>
                  </div>
                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" id="toponym-and" value="AND" v-model="form.toponymMode">
                    <label class="form-check-label" for="toponym-and">AND (all)</label>
                  </div>
                </div>
              </div>

            </div>

            <div class="mt-3 d-flex gap-2">
              <button class="btn btn-primary" type="submit">Search</button>
              <button class="btn btn-outline-secondary" type="button" @click="resetForm">Reset</button>
              <button class="btn btn-link btn-sm ms-auto" type="button" @click="formExpanded = false">
                Collapse ▴
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Results -->
    <div class="container mt-4">
      <div v-if="!hasAnyFilter" class="text-muted">
        Use the form above to search.
      </div>

      <div v-else>
        <p v-if="searching">
          <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          Loading results...
        </p>
        <div v-else>
          <p class="text-muted" v-if="total">
            Showing page {{ page }} of {{ totalPages }} ({{ total }} results)
          </p>
          <ul class="list-group mt-3" v-if="results.length">
            <li v-for="result in results" :key="`${result.document_id}-${result.page_number}`" class="list-group-item">
              <router-link :to="{ name: 'DetailPage', params: { id: result.document_id, page: result.page_number } }">
                {{ result.author }} - {{ result.title }} - Page {{ result.page_number }}
              </router-link>
              <br/>
              <small class="text-muted" v-html="result.snippet"></small>
            </li>
          </ul>
          <p v-else class="mt-3">No results found.</p>

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
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/'

// Lookup data
const eventTypes = ref([])
const allToponymVariants = ref([])

// Form state
const form = ref({
  q: '',
  eventIds: [],
  eventMode: 'OR',
  selectedToponyms: [],
  toponymMode: 'OR',
})
const formExpanded = ref(false)

// Toponym autocomplete state
const toponymSearch = ref('')
const toponymSuggestions = ref([])
const highlightedIndex = ref(-1)
const toponymInput = ref(null)

// Results state
const results = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(25)
const searching = ref(false)

// Derived
const hasAnyFilter = computed(() =>
  form.value.q.trim() || form.value.eventIds.length || form.value.selectedToponyms.length
)

const isAdvanced = computed(() =>
  form.value.eventIds.length > 0 || form.value.selectedToponyms.length > 0
)

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
  for (let p = start; p <= end; p++) pages.push(p)
  return pages
})

// Load lookup data
onMounted(async () => {
  const [etRes, tvRes] = await Promise.all([
    fetch(`${baseUrl}event-types`).then(r => r.json()),
    fetch(`${baseUrl}toponyms`).then(r => r.json()),
  ])
  eventTypes.value = etRes
  allToponymVariants.value = tvRes
  syncFormFromRoute()
})

function syncFormFromRoute() {
  const q = route.query.q || ''
  const events = route.query.events ? route.query.events.split(',').map(Number).filter(Boolean) : []
  const eventMode = route.query.event_mode || 'OR'
  const toponymIds = route.query.toponyms ? route.query.toponyms.split(',').map(Number).filter(Boolean) : []
  const toponymMode = route.query.toponym_mode || 'OR'

  form.value.q = q
  form.value.eventIds = events
  form.value.eventMode = eventMode
  form.value.toponymMode = toponymMode
  form.value.selectedToponyms = toponymIds.length
    ? allToponymVariants.value.filter(tv => toponymIds.includes(tv.id))
    : []

  // Expand form if arriving with no search params (direct "Advanced Search" nav click)
  const hasParams = q || events.length || toponymIds.length
  formExpanded.value = !hasParams
}

function submitSearch() {
  const query = {}
  if (form.value.q.trim()) query.q = form.value.q.trim()
  if (form.value.eventIds.length) {
    query.events = form.value.eventIds.join(',')
    query.event_mode = form.value.eventMode
  }
  if (form.value.selectedToponyms.length) {
    query.toponyms = form.value.selectedToponyms.map(t => t.id).join(',')
    query.toponym_mode = form.value.toponymMode
  }
  query.page = '1'
  router.push({ name: 'SearchResults', query })
}

function resetForm() {
  form.value = { q: '', eventIds: [], eventMode: 'OR', selectedToponyms: [], toponymMode: 'OR' }
  toponymSearch.value = ''
  toponymSuggestions.value = []
}

function changePage(nextPage) {
  if (nextPage < 1 || nextPage > totalPages.value) return
  const query = { ...route.query, page: nextPage }
  router.push({ name: 'SearchResults', query })
}

// Fetch results whenever route changes
watch(
  () => [route.query],
  () => {
    syncFormFromRoute()
    fetchResults()
  },
  { immediate: true, deep: true }
)

function fetchResults() {
  const q = route.query.q || ''
  const events = route.query.events || ''
  const toponyms = route.query.toponyms || ''
  const currentPage = Number.parseInt(route.query.page, 10) || 1

  if (!q && !events && !toponyms) {
    results.value = []
    total.value = 0
    searching.value = false
    return
  }

  searching.value = true

  let url
  if (events || toponyms) {
    const params = new URLSearchParams()
    if (q) params.set('q', q)
    if (events) { params.set('events', events); params.set('event_mode', route.query.event_mode || 'OR') }
    if (toponyms) { params.set('toponyms', toponyms); params.set('toponym_mode', route.query.toponym_mode || 'OR') }
    params.set('page', currentPage)
    params.set('page_size', pageSize.value)
    url = `${baseUrl}advanced-search?${params.toString()}`
  } else {
    url = `${baseUrl}search?q=${encodeURIComponent(q)}&page=${currentPage}&page_size=${pageSize.value}`
  }

  fetch(url)
    .then(r => r.json())
    .then(data => {
      results.value = data.results || []
      total.value = data.total || 0
      page.value = data.page || 1
      pageSize.value = data.page_size || pageSize.value
    })
    .catch(err => console.error('Search error:', err))
    .finally(() => { searching.value = false })
}

// Toponym autocomplete
function onToponymInput() {
  const q = toponymSearch.value.trim().toLowerCase()
  highlightedIndex.value = -1
  if (!q) { toponymSuggestions.value = []; return }
  const selectedIds = new Set(form.value.selectedToponyms.map(t => t.id))
  toponymSuggestions.value = allToponymVariants.value
    .filter(tv => !selectedIds.has(tv.id) && tv.name.toLowerCase().includes(q))
    .slice(0, 10)
}

function selectToponym(tv) {
  if (!form.value.selectedToponyms.find(t => t.id === tv.id)) {
    form.value.selectedToponyms.push(tv)
  }
  toponymSearch.value = ''
  toponymSuggestions.value = []
  highlightedIndex.value = -1
}

function removeToponym(id) {
  form.value.selectedToponyms = form.value.selectedToponyms.filter(t => t.id !== id)
}

function closeSuggestions() {
  setTimeout(() => { toponymSuggestions.value = [] }, 150)
}

function highlightNext() {
  if (toponymSuggestions.value.length === 0) return
  highlightedIndex.value = Math.min(highlightedIndex.value + 1, toponymSuggestions.value.length - 1)
}

function highlightPrev() {
  highlightedIndex.value = Math.max(highlightedIndex.value - 1, -1)
}

function selectHighlighted() {
  if (highlightedIndex.value >= 0 && toponymSuggestions.value[highlightedIndex.value]) {
    selectToponym(toponymSuggestions.value[highlightedIndex.value])
  }
}

function focusToponymInput() {
  nextTick(() => toponymInput.value?.focus())
}
</script>
