<template>
  <div>
    <div class="container mt-4">
      <div class="row">
        <div class="col-12 text-center pb-3" v-if="docLoaded">
          <h2>{{page_info.document_author}}</h2>
          <h1>{{page_info.document_title}}</h1>
        </div>
        <div class="d-flex justify-content-center align-items-center gap-3 mb-4 col-12">
          <button class="btn btn-primary me-2" @click="prevPage" :disabled="currentPage <= 1">Previous</button>
          <span class="fw-bold">Pagina {{page_info.page_number}}</span>
          <button class="btn btn-primary" @click="nextPage">Next</button>
        </div>
        <div class="col-md-6 d-flex align-items-center justify-content-center">
          <div v-if="!imageLoaded" class="text-center w-100">
            <div class="spinner-border text-primary" role="status"></div>
          </div>
          <img
              v-if="imageUrl"
              :src="imageUrl"
              alt="Scanned Page"
              class="img-fluid"
              v-show="imageLoaded"
              @load="onImageLoad"
              @error="onImageError"
          >
        </div>
        <div class="col-md-6">
          <pre>{{ text }}</pre>
        </div>
      </div>
      <div class="col-12 mt-4" v-if="events.length > 0">
        <h5>Eventi</h5>
        <ul class="list-group">
          <li class="list-group-item" v-for="(ev, i) in events" :key="i">
            <span class="badge bg-secondary me-2">{{ ev.event_type }}</span>
            {{ ev.sentence }}
          </li>
        </ul>
      </div>
      <div class="d-flex justify-content-center align-items-center gap-3 mt-4 col-12">
        <button class="btn btn-primary me-2" @click="prevPage" :disabled="currentPage <= 1">Previous</button>
        <span class="fw-bold">Pagina {{page_info.page_number}}</span>
        <button class="btn btn-primary" @click="nextPage">Next</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, watch, onMounted} from 'vue'
import {useRoute, useRouter} from 'vue-router'

const route = useRoute()
const router = useRouter()

const id = route.params.id
const currentPage = ref(parseInt(route.params.page))
const text = ref('')
const imageUrl = ref('')
const navbarQuery = ref('')
const imageLoaded = ref(false)
const docLoaded = ref(false)
const page_info = ref({})
const events = ref([])

function onImageLoad() {
  imageLoaded.value = true
}

function onImageError() {
  imageLoaded.value = false
  console.error('Image failed to load.')
}

function submitSearch() {
  if (navbarQuery.value.trim() !== '') {
    router.push({name: 'SearchResults', query: {q: navbarQuery.value}})
  }
}

function loadPage() {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/'
  docLoaded.value = false
  fetch(`${baseUrl}documents/${id}/pages/${currentPage.value}`)
      .then(response => response.json())
      .then(data => {
        text.value = data.content
        page_info.value = data
        events.value = data.events || []
        docLoaded.value = true
        imageLoaded.value = false
        imageUrl.value = `${import.meta.env.VITE_API_BASE_URL}/static/${data.file_name}/page-${currentPage.value.toString().padStart(3, '0')}.jpg`
      })
      .catch(error => {
        console.error('Page load error:', error)
      })
}

function prevPage() {
  const newPage = currentPage.value - 1
  if (newPage >= 1) {
    router.push({name: 'DetailPage', params: {id, page: newPage}})
  }
}

function nextPage() {
  const newPage = currentPage.value + 1
  router.push({name: 'DetailPage', params: {id, page: newPage}})
}

onMounted(loadPage)

watch(() => route.params.page, (newVal) => {
  currentPage.value = parseInt(newVal)
  loadPage()
})
</script>

<style scoped>
pre {
  white-space: pre-wrap;
}
</style>