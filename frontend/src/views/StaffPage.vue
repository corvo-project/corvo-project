<template>
  <div class="container py-5" id="staff">
    <div class="text-center mb-4">
      <h1>Staff</h1>
      <p class="text-muted mb-0">Meet the people behind CorVo.</p>
    </div>

    <div class="row g-4 align-items-top mb-5" v-for="member in staff" :key="member.name">
      <div class="col-12 col-md-3 text-center text-md-end">
        <img
          :src="member.img"
          :alt="member.name"
          class="img-thumbnail staff-photo"
        >
      </div>
      <div class="col-12 col-md-9 text-center text-md-start">
        <h3 class="h5 mb-1">{{ member.name }}</h3>
        <div class="text-muted mb-2">{{ member.role }}</div>
        <p class="mb-0">{{ member.bio }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
const staff = [
  {
    name: 'Claudia Principe',
    role: 'Project Lead',
    img: '/foto/principe.jpg',
    bio: 'Claudia Principe is a retired Research Director and current Research Associate at the Pisa Institute of Geosciences and Earth Resources of the Italian National Research Council (IGG-CNR), where she created and directed the laboratories for archaeomagnetic measurements and microstratigraphic coring. She is one of the two CNR representatives within IAVCEI and one of the Italian delegates in the INHIGEO-IUGG commission. Since June 2024, she has been vice president of the Migliarino-San Rossore-Massaciuccoli Regional Natural Park. Her research interests have always been linked to physical volcanology. She is an expert in chrono-stratigraphy and geological mapping of volcanic areas for volcanic hazard and geothermal potential assessment, as well as in historical volcanology, history of volcanology and geo-archaeology for the reconstruction of paleo-environments. She is author of more than 180 scientific articles and geological maps concerning over 30 volcanoes around the world.'
  },
  {
    name: 'Costanza Marini',
    role: 'Researcher in Linguistics',
    img: '/foto/marini.jpg',
    bio: 'Costanza Marini is a third-year postdoc at the Department of Humanities of the University of Pavia. She holds a PhD in Linguistics from the Universities of Pavia and Bergamo with a dissertation at the intersection of lexical semantics and digital lexicography on the interactions between aspect, Aktionsart, and polysemy in Croatian aspectual verb pairs. Her interests also include language teaching, linguistic landscapes and discourse studies. She is currently working on conspiracy theories and media bias from a corpus-based multilingual perspective.'
  },
  {
    name: 'Alessio Palmero Aprosio',
    role: 'Professor in Information Technology',
    img: '/foto/palmeroaprosio.jpg',
    bio: 'Alessio Palmero Aprosio is an associate professor at the University of Trento in the field of Artificial Intelligence and Computational Linguistics. He has been a researcher at Fondazione Bruno Kessler for 12 years and is currently a research fellow there. He works on Natural Language Processing, semantic technologies, and knowledge representation. His work focuses on bridging language, data, and intelligent systems to enhance human-computer interaction.'
  }
]
</script>

<style scoped>
.staff-photo {
  max-width: 160px;
}
</style>
