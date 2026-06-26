<template>
  <div>
    <div class="container mt-4">
      <div class="row">
        <div class="col-12" id="main-map">
          <l-map ref="map" v-model:zoom="zoom" v-model:center="center" :useGlobalLeaflet="false">
            <l-tile-layer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                layer-type="base"
                name="OpenStreetMap">
            </l-tile-layer>
            <l-marker v-for="pin in pins" :key="pin.id" :lat-lng="pin.coordinates">
              <l-popup>
                <strong>{{ pin.name }}</strong><br/>
                <router-link :to="{ name: 'SearchResults', query: { toponyms: pin.id } }">
                  Cerca documenti
                </router-link>
              </l-popup>
            </l-marker>
          </l-map>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import "leaflet/dist/leaflet.css"
import { LMap, LMarker, LPopup, LTileLayer } from "@vue-leaflet/vue-leaflet"
import { ref, onMounted } from "vue"

const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/'

const zoom = ref(11)
const center = ref([40.822317, 14.3588341])
const pins = ref([])

function midpoint(coordinates) {
  const n = coordinates.length
  const sumLat = coordinates.reduce((s, c) => s + c[0], 0)
  const sumLng = coordinates.reduce((s, c) => s + c[1], 0)
  return [sumLat / n, sumLng / n]
}

onMounted(async () => {
  const toponyms = await fetch(`${baseUrl}toponyms`).then(r => r.json())
  const result = []
  for (const t of toponyms) {
    const marker = t.location_info?.marker
    if (!marker) continue
    if (marker.type === 'circle' || marker.type === 'simple') {
      if (marker.lat != null && marker.lng != null) {
        result.push({ id: t.id, name: t.name, coordinates: [marker.lat, marker.lng] })
      }
    } else if (marker.type === 'line') {
      if (Array.isArray(marker.coordinates) && marker.coordinates.length > 0) {
        result.push({ id: t.id, name: t.name, coordinates: midpoint(marker.coordinates) })
      }
    }
  }
  pins.value = result
})
</script>

<style>
#main-map {
  height: 85vh;
  width: 100vw;
}
</style>
