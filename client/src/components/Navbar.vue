<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4 shadow-sm">
    <div class="container">
      <RouterLink to="/" class="navbar-brand fw-bold">✈️ AirManager</RouterLink>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item"><RouterLink class="nav-link" to="/">Главная</RouterLink></li>
          <li class="nav-item"><RouterLink class="nav-link" to="/airlines">Авиакомпании</RouterLink></li>
          <li class="nav-item"><RouterLink class="nav-link" to="/flights">Рейсы</RouterLink></li>
          <li class="nav-item"><RouterLink class="nav-link" to="/passengers">Пассажиры</RouterLink></li>
          <li class="nav-item"><RouterLink class="nav-link" to="/rates">Тарифы</RouterLink></li>
          <li class="nav-item"><RouterLink class="nav-link" to="/tickets">Билеты</RouterLink></li>
          <li class="nav-item"><RouterLink class="nav-link" to="/stats">Статистика</RouterLink></li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>
