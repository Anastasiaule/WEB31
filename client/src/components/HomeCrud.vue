<script setup>
import { ref, onBeforeMount } from 'vue'
import axios from 'axios'
import { RouterLink } from 'vue-router'
import { useRouter } from "vue-router"
import { useUserStore } from '@/stores/user_store'
import { storeToRefs } from "pinia"

const username = ref()
const password = ref()
const router = useRouter()
const userStore = useUserStore()
const { userInfo } = storeToRefs(userStore)

const quickStats = ref([
  { icon: '🏢', title: 'Авиакомпаний', value: '0' },
  { icon: '🛫', title: 'Рейсов', value: '0' },
  { icon: '👥', title: 'Пассажиров', value: '0' },
  { icon: '🎫', title: 'Билетов', value: '0' }
])

const navCards = ref([
  {
    icon: '🏢',
    title: 'Авиакомпании',
    description: 'Управление авиакомпаниями',
    link: '/airlines'
  },
  {
    icon: '🛫',
    title: 'Рейсы',
    description: 'Создание и управление рейсами',
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
    description: 'Настройка тарифов',
    link: '/rates'
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

async function onFormSend() {
  userStore.login(username.value, password.value)
}

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
    airlines.value=response.data
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
    recentFlights.value = response.data.slice(0, 5)
  } catch (error) {
    console.error('Error fetching flights:', error)
  } finally {
    loadingFlights.value = false
  }
}

// экспорт в ексель
async function exportData(type) {
  try {
    let url = ''
    let filename = ''
    
    if (type === 'flights') {
      url = '/api/flights/export-excel/'
      filename = 'рейсы'
    } else if (type === 'passengers') {
      url = '/api/passengers/export-excel/'
      filename = 'пассажиры'
    } else if (type === 'tickets') {
      url = '/api/tickets/export-excel/'
      filename = 'билеты'
    }
    
    alert(`Начинаем экспорт ${filename}...`)
    
    // гет запрос
    const response = await axios.get(url, {
      responseType: 'blob'
    })
    
    // скачивание файлика
    const urlBlob = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = urlBlob
    
    // имя файлика ексель
    const contentDisposition = response.headers['content-disposition']
    if (contentDisposition && contentDisposition.includes('filename=')) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    
    // освобождаем юрл
    window.URL.revokeObjectURL(urlBlob)
    
    alert(`Экспорт ${filename} успешно завершен!`)
    
  } catch (error) {
    console.error('Ошибка при экспорте:', error)
    alert('Ошибка при экспорте данных.')
  }
}
</script>

<template>
<div class="container py-4">
  

  <div v-if="userInfo" class="card mb-4">
    <div class="card-body text-center">
      <h4 class="mb-0">👋 Добро пожаловать на борт, {{ userInfo.username }}</h4>
    </div>
  </div>

  <!-- экспорт ексель-->
  <div class="card mb-4">
    <div class="card-header bg-light">
      <h5 class="mb-0">Экспорт данных в Excel</h5>
    </div>
    <div class="card-body">
      <div class="row">
        <div class="col-md-4 mb-3">
          <button @click="exportData('flights')" class="btn btn-success w-100">
            🛫 Экспорт рейсов
          </button>
        </div>
        <div class="col-md-4 mb-3">
          <button @click="exportData('passengers')" class="btn btn-primary w-100">
            👥 Экспорт пассажиров
          </button>
        </div>
        <div class="col-md-4 mb-3">
          <button @click="exportData('tickets')" class="btn btn-warning w-100">
            🎫 Экспорт билетиков
          </button>
        </div>
      </div>
      <small class="text-muted">Нажмите кнопочку, чтобы скачать данные в Excel :о</small>
    </div>
  </div>
  
  <div class="stats-card mb-4">
    <h5 class="mb-3">Общая статистика</h5>
    <div class="row text-center">
      <div class="col-md-3 mb-3" v-for="stat in quickStats" :key="stat.title">
        <div class="stat-item">
          <div class="stat-icon">{{ stat.icon }}</div>
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.title }}</div>
        </div>
      </div>
    </div>
  </div>

  <!-- кнопки перехода -->
  <div class="card mb-4">
    <div class="card-header bg-light">
      <h5 class="mb-0">Быстрый доступ</h5>
    </div>
    <div class="card-body">
      <div class="row row-cols-1 row-cols-md-2 row-cols-lg-4 g-3">
        <div class="col" v-for="card in navCards" :key="card.title">
          <RouterLink :to="card.link" class="nav-card text-decoration-none">
            <div class="nav-icon">{{ card.icon }}</div>
            <h6 class="nav-title">{{ card.title }}</h6>
            <p class="nav-desc">{{ card.description }}</p>
            <small class="nav-link">Перейти →</small>
          </RouterLink>
        </div>
      </div>
    </div>
  </div>

  <!-- авиакомпании -->
  <div class="card mb-4">
    <div class="card-header bg-light">
      <h5 class="mb-0">🏢 Наши авиакомпании</h5>
    </div>
    <div class="card-body">
      <div v-if="loadingAirlines" class="text-center py-4">
        <div class="spinner-border spinner-border-sm text-primary"></div>
        <p class="mt-2 text-muted">Загрузка...</p>
      </div>
      <div v-else class="row row-cols-2 row-cols-md-4 row-cols-lg-6 g-3">
        <div class="col" v-for="airline in airlines" :key="airline.id">
          <div class="airline-card text-center p-2">
            <div v-if="airline.picture" class="airline-logo mb-2">
              <img :src="airline.picture" :alt="airline.name" class="img-fluid rounded">
            </div>
            <div v-else class="airline-placeholder mb-2">
              <span>🏢</span>
            </div>
            <h6 class="airline-name">{{ airline.name }}</h6>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- последние рейсы -->
  <div class="card">
    <div class="card-header bg-light">
      <h5 class="mb-0">🛫 Последние рейсы</h5>
    </div>
    <div class="card-body">
      <div v-if="loadingFlights" class="text-center py-4">
        <div class="spinner-border spinner-border-sm text-primary"></div>
        <p class="mt-2 text-muted">Загрузка...</p>
      </div>
      <div v-else class="list-group list-group-flush">
        <div v-for="flight in recentFlights" :key="flight.id" class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h6 class="mb-1"><strong>{{ flight.name }}</strong> — {{ flight.route }}</h6>
              <small class="text-muted">
                ✈️ {{ new Date(flight.departure_time).toLocaleString() }} • 
                💺 {{ flight.price }} руб.
              </small>
            </div>
            <span class="badge bg-primary">{{ flight.airline_name }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- модалка авторизации -->
  <div v-if="userInfo && !userInfo.is_authenticated" class="modal fade show d-block" style="background: rgba(0,0,0,0.5)">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Пожалуйста, авторизуйтесь</h5>
        </div>
        <div class="modal-body">
          <form @submit.stop.prevent="onFormSend" class="row g-3">
            <div class="col-md-6">
              <input v-model="username" type="text" class="form-control form-control-sm" placeholder="Логин" required>
            </div>
            <div class="col-md-6">
              <input v-model="password" type="password" class="form-control form-control-sm" placeholder="Пароль" required>
            </div>
            <div class="col-12">
              <button type="submit" class="btn btn-primary btn-sm w-100">Войти</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>

</div>
</template>

<style scoped>
.stats-card {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 20px;
}

.stat-item {
  padding: 15px;
}

.stat-icon {
  font-size: 2rem;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #0d6efd;
  margin-bottom: 5px;
}

.stat-label {
  color: #6c757d;
  font-size: 0.9rem;
}

.nav-card {
  display: block;
  padding: 20px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  text-align: center;
  transition: all 0.3s ease;
}

.nav-card:hover {
  background-color: #f8f9fa;
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.nav-icon {
  font-size: 2.5rem;
  margin-bottom: 10px;
  color: #0d6efd;
}

.nav-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: #212529;
}

.nav-desc {
  font-size: 0.85rem;
  color: #6c757d;
  margin-bottom: 10px;
}

.nav-link {
  color: #0d6efd;
  font-weight: 500;
}

.airline-card {
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
}

.airline-logo img {
  max-height: 50px;
  transition: transform 0.3s ease;
}

.airline-logo:hover img {
  transform: scale(1.05);
}

.airline-placeholder {
  font-size: 2rem;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.airline-name {
  font-size: 0.85rem;
  font-weight: 600;
  margin: 0;
}

.list-group-item {
  border: 1px solid #dee2e6;
  border-radius: 6px;
  margin-bottom: 8px;
  padding: 12px 15px;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

.badge {
  font-size: 0.8rem;
  padding: 0.4rem 0.6rem;
}

.btn {
  padding: 10px 20px;
}
</style>