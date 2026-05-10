import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import ProjectPage from '../views/ProjectPage.vue'
import SearchResults from '../views/SearchResults.vue'
import MapPage from '../views/MapPage.vue'
import DetailPage from '../views/DetailPage.vue'
import PublicationsPage from '../views/PublicationsPage.vue'
import DatasetPage from '../views/DatasetPage.vue'
import StaffPage from '../views/StaffPage.vue'

const routes = [
    { path: '/', name: 'Home', component: HomePage },
    { path: '/project', name: 'ProjectPage', component: ProjectPage },
    { path: '/search', name: 'SearchResults', component: SearchResults },
    { path: '/map', name: 'MapPage', component: MapPage },
    { path: '/publications', name: 'PublicationsPage', component: PublicationsPage },
    { path: '/dataset', name: 'DatasetPage', component: DatasetPage },
    { path: '/staff', name: 'StaffPage', component: StaffPage },
    { path: '/document/:id/page/:page', name: 'DetailPage', component: DetailPage, props: true }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
