<template>
  <div class="d-flex flex-column h-100">

    <nav class="navbar navbar-expand-md navbar-dark bg-dark">
      <div class="container">
        <router-link class="navbar-brand" to="/">CorVo</router-link>
        <div class="collapse navbar-collapse">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/">Home</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/project">Project</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/map">Map</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/publications">Publications</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/dataset">Dataset</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/staff">Staff</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :to="{ name: 'SearchResults' }">Advanced search</router-link>
            </li>
          </ul>
          <form class="d-flex" @submit.prevent="submitSearch">
            <input
              v-model="query"
              class="form-control me-2"
              type="search"
              placeholder="Search"
            >
            <button class="btn btn-outline-light" type="submit">Go</button>
          </form>

        </div>
      </div>
    </nav>
    <main class="flex-grow-1">
      <router-view></router-view>
    </main>
    <footer class="bg-body mt-3">
      <div class="container">
        <div class="row d-flex flex-wrap justify-content-between align-items-center text-center">
          <div class="col-md-3 p-4">
            <a href="https://www.mur.gov.it/it"><img src="/loghi/miur.jpg" alt="Logo MUR"></a>
          </div>
          <div class="col-md-3 p-4">
            <a href="https://www.italiadomani.gov.it/"><img src="/loghi/pnrr.jpg" alt="Logo PNRR"></a>
          </div>
          <div class="col-md-3 p-4">
            <a href="https://next-generation-eu.europa.eu/index_it"><img src="/loghi/nextgeneu.jpg" alt="Logo NextGenerationEU"></a>
          </div>
          <div class="col-md-3 p-4">
            <a href="https://meet.ingv.it/"><img src="/loghi/meet.jpg" alt="Logo MEET"></a>
          </div>
        </div>
        <div class="row d-flex flex-wrap justify-content-between align-items-center text-center">
          <div class="col-md-3 p-4">
            <a href="https://www.igg.cnr.it/"><img src="/loghi/logo-igg.png" alt="Logo IGG"></a>
          </div>
          <div class="col-md-3 p-4">
            <a href="https://www.cnr.it/"><img src="/loghi/logo_cnr_affiancato.png" alt="Logo CNR"></a>
          </div>
          <div class="col-md-3 p-4">
            <a href="https://www.unipv.it/"><img src="/loghi/logo_unipv_amaranto.png" alt="Logo Università di Pavia"></a>
          </div>
          <div class="col-md-3 p-4">
            <a href="https://www.unitn.it/"><img src="/loghi/UniTrento_logo_ITA_colore.jpg" alt="Logo Università di Trento"></a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      query: ''
    }
  },
  methods: {
    submitSearch() {
      const trimmed = this.query.trim()
      if (!trimmed) return
      this.$router.push({name: 'SearchResults', query: {q: trimmed, page: 1}})
    }
  }
}
</script>
