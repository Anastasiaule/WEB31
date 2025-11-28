<script setup>
import { ref, onBeforeMount } from 'vue'
import axios from 'axios'
import { RouterLink } from 'vue-router'
import {useRouter} from "vue-router";
import {useUserStore} from '@/stores/user_store';
import {storeToRefs} from "pinia";
const username = ref();
const password = ref();

const router = useRouter()
const userStore = useUserStore()
const {
    userInfo,
} = storeToRefs(userStore)

async function onFormSend() {
    userStore.login(username.value, password.value)
}
const quickStats = ref([
  { icon: '🏢', title: 'Авиакомпаний', value: '0', color: 'text-info' },
  { icon: '🛫', title: 'Рейсов', value: '0', color: 'text-success' },
  { icon: '👥', title: 'Пассажиров', value: '0', color: 'text-warning' },
  { icon: '🎫', title: 'Билетов', value: '0', color: 'text-danger' }
])

const navCards = ref([
  {
    icon: '🏢',
    title: 'Авиакомпании',
    description: 'Управление авиакомпаниями и их логотипами',
    link: '/airlines'
  },
  {
    icon: '🛫',
    title: 'Рейсы',
    description: 'Создание и управление авиарейсами',
    link: '/flights'
  },
  {
    icon: '👥',
    title: 'Пассажиры',
    description: 'Управление данными пассажиров',
    link: '/passengers'
  },
  {
    icon: '💰',
    title: 'Тарифы',
    description: 'Настройка тарифов и коэффициентов',
    link: '/rates'
  },
  {
    icon: '🎫',
    title: 'Билеты',
    description: 'Бронирование и управление билетами',
    link: '/tickets'
  },
  {
    icon: '📊',
    title: 'Статистика',
    description: 'Детальная аналитика системы',
    link: '/stats'
  }
])

const airlines = ref([])
const recentFlights = ref([])
const loadingAirlines = ref(false)
const loadingFlights = ref(false)

onBeforeMount(async () => {
  await fetchQuickStats()
  await fetchAirlines()
  await fetchRecentFlights()
})

async function fetchQuickStats() {
  try {
    const [airlinesRes, flightsRes, passengersRes, ticketsRes] = await Promise.all([
      axios.get('/api/airlines/stats/'),
      axios.get('/api/flights/stats/'),
      axios.get('/api/passengers/stats/'),
      axios.get('/api/tickets/stats/')
    ])
    
    quickStats.value[0].value = airlinesRes.data.count
    quickStats.value[1].value = flightsRes.data.count
    quickStats.value[2].value = passengersRes.data.count
    quickStats.value[3].value = ticketsRes.data.count
  } catch (error) {
    console.error('Error fetching quick stats:', error)
  }
}

async function fetchAirlines() {
  loadingAirlines.value = true
  try {
    const response = await axios.get('/api/airlines/')
    airlines.value = response.data.slice(0, 12) // Показываем только первые 12
  } catch (error) {
    console.error('Error fetching airlines:', error)
  } finally {
    loadingAirlines.value = false
  }
}

async function fetchRecentFlights() {
  loadingFlights.value = true
  try {
    const response = await axios.get('/api/flights/')
    recentFlights.value = response.data.slice(0, 5) // Показываем только 5 последних
  } catch (error) {
    console.error('Error fetching flights:', error)
  } finally {
    loadingFlights.value = false
  }
}
</script>
<template>
    <div v-if="userInfo">
        <h4>Привет, {{userInfo.username}}</h4>
    </div>
  <div class="home-page">
    <!-- Hero Section -->
    <div class="hero-section bg-primary text-white py-5 mb-5 rounded-bottom">
      <div class="container text-center">
        <h1 class="display-4 fw-bold mb-3">✈️ AirManager</h1>
        <p class="lead">Управление авиаперевозками в реальном времени</p>
      </div>
    </div>

    <div class="container">
      <!-- Quick Stats -->
      <div class="row mb-5">
        <div class="col-md-3 mb-3" v-for="stat in quickStats" :key="stat.title">
          <div class="card h-100 shadow-sm border-0">
            <div class="card-body text-center">
              <div class="stat-icon display-6 mb-2" :class="stat.color">{{ stat.icon }}</div>
              <h3 class="fw-bold text-primary">{{ stat.value }}</h3>
              <p class="text-muted mb-0">{{ stat.title }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Cards -->
      <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4 mb-5">
        <div class="col" v-for="card in navCards" :key="card.title">
          <RouterLink :to="card.link" class="text-decoration-none">
            <div class="card h-100 shadow-hover border-0">
              <div class="card-body text-center p-4">
                <div class="nav-icon display-1 mb-3 text-primary">{{ card.icon }}</div>
                <h4 class="card-title fw-bold">{{ card.title }}</h4>
                <p class="card-text text-muted">{{ card.description }}</p>
                <small class="text-primary fw-bold">Перейти →</small>
              </div>
            </div>
          </RouterLink>
        </div>
      </div>

      <!-- Airlines Carousel -->
      <div class="card shadow-sm border-0 mb-5">
        <div class="card-header bg-white border-0 py-3">
          <h4 class="mb-0">🏢 Наши авиакомпании</h4>
        </div>
        <div class="card-body">
          <div v-if="loadingAirlines" class="text-center py-4">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted">Загрузка авиакомпаний...</p>
          </div>
          <div v-else class="row row-cols-2 row-cols-md-4 row-cols-lg-6 g-3">
            <div class="col" v-for="airline in airlines" :key="airline.id">
              <div class="card h-100 border-0 text-center">
                <div class="card-body p-3">
                  <div v-if="airline.picture" class="airline-logo mb-2">
                    <img :src="airline.picture" :alt="airline.name" class="img-fluid rounded" style="max-height: 60px;">
                  </div>
                  <div v-else class="airline-placeholder mb-2">
                    <span class="display-6">🏢</span>
                  </div>
                  <h6 class="card-title small fw-bold">{{ airline.name }}</h6>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Flights -->
      <div class="card shadow-sm border-0">
        <div class="card-header bg-white border-0 py-3">
          <h4 class="mb-0">🛫 Последние рейсы</h4>
        </div>
        <div class="card-body">
          <div v-if="loadingFlights" class="text-center py-4">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted">Загрузка рейсов...</p>
          </div>
          <div v-else class="list-group list-group-flush">
            <div v-for="flight in recentFlights" :key="flight.id" class="list-group-item border-0 px-0">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="mb-1 fw-bold">{{ flight.name }}</h6>
                  <p class="mb-1 text-muted small">{{ flight.route }}</p>
                  <small class="text-muted">
                    ✈️ {{ new Date(flight.departure_time).toLocaleString() }} • 
                    💺 {{ flight.price }} руб.
                  </small>
                </div>
                <span class="badge bg-primary rounded-pill">{{ flight.airline_name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-if="userInfo && !userInfo.is_authenticated" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Пожалуйста, авторизуйтесь</h5>
         
        </div>
        <div class="modal-body text-center">
         <div v-if="userInfo && !userInfo.is_authenticated" class="container">
        <form
            @submit.stop.prevent="onFormSend"
            style="display: flex; gap: 8px; align-items: center; justify-content: center; padding: 8px; width: 100%">

            <input v-model="username" type="text" placeholder="username" required class="input-group-text" style="flex: auto;">
            <input v-model="password" type="password" placeholder="password" required class="input-group-text"  style="flex: auto;">

            <button type="submit" class="btn btn-primary">Отправить</button>
        </form>
    </div>
        </div>
      </div>
    </div>
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