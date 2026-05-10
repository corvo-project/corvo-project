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
            <l-marker v-for="comune in comuni" :lat-lng="comune.coordinates" :name="comune.name">
              <l-popup>
                <strong>{{ comune.name }}</strong><br/>
                <a :href="`${baseUrl}search/?q=${comune.search_text}`">
                  Cerca documenti
                </a>
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
import {LMap, LMarker, LPopup, LTileLayer} from "@vue-leaflet/vue-leaflet"
import {ref} from "vue";

const baseUrl = ref(import.meta.env.VITE_BASE_URL || 'http://localhost:8000/')

let comuni = ref([
  {
    name: "Napoli",
    coordinates: [40.8522, 14.2681],
    search_text: "Napoli"
  },
  {
    name: "San Sebastiano al Vesuvio",
    coordinates: [40.8439852, 14.3544226],
    search_text: "San Sebastiano"
  },
  {
    name: "Massa di Somma",
    coordinates: [40.8455419, 14.3659948],
    search_text: "Massa di Somma"
  },
  {
    name: "Torre del Greco",
    coordinates: [40.7863759, 14.3539744],
    search_text: "Torre del Greco"
  },
  {
    name: "Scafati",
    coordinates: [40.7637079, 14.4997287],
    search_text: "Scafati"
  },
  {
    name: "Cercola",
    coordinates: [40.8622339, 14.3399324],
    search_text: "Cercola"
  },
  {
    name: "Boscotrecase",
    coordinates: [40.7727937, 14.4510311],
    search_text: "Boscotrecase"
  },
  {
    name: "Terzigno",
    coordinates: [40.7999227, 14.4390794],
    search_text: "Terzigno"
  },
  {
    name: "Poggiomarino",
    coordinates: [40.8027593, 14.5199671],
    search_text: "Poggiomarino"
  },
  {
    name: "Pollena",
    coordinates: [40.8593657, 14.3464187],
    search_text: "Pollena"
  },
  {
    name: "Pompei",
    coordinates: [40.7466178, 14.4730826],
    search_text: "Pompei"
  },
  {
    name: "Ercolano",
    coordinates: [40.8153357, 14.3433472],
    search_text: "Ercolano"
  },
])

// import arcades from "./arcades.json"

let zoom = ref(11)
let center = ref([40.822317, 14.3588341])
</script>

<style>
#main-map {
  height: 85vh;
  width: 100vw;
}

</style>