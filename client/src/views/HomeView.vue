<script setup>

import FlightsCrud from '@/components/HomeCrud.vue'
</script>
<template>
  <div class="container mt-4">
    <h2>Главная</h2>
    <FlightsCrud />
  </div>
</template>
<style scoped>
.hero-section {
  background: linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%);
}

.shadow-hover {
  transition: all 0.3s ease;
}

.shadow-hover:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
}

.stat-icon {
  opacity: 0.8;
}

.nav-icon {
  opacity: 0.9;
  transition: transform 0.3s ease;
}

.card:hover .nav-icon {
  transform: scale(1.1);
}

.airline-logo img {
  transition: transform 0.3s ease;
}

.airline-logo:hover img {
  transform: scale(1.05);
}
</style>
