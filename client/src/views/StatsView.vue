[file name]: StatsView.vue
[file content begin]
<template>
  <div class="stats-page">
    <div class="container">
      <h2 class="mb-4">📊 Статистика системы</h2>
      
      <!-- Основная статистика -->
      <div class="row mb-5">
        <div class="col-md-3 mb-3" v-for="stat in mainStats" :key="stat.title">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="stat-icon display-6 mb-2" :class="stat.color">{{ stat.icon }}</div>
              <h3 class="fw-bold text-primary">{{ stat.value }}</h3>
              <p class="text-muted mb-0">{{ stat.title }}</p>
              <small class="text-muted" v-if="stat.subtitle">{{ stat.subtitle }}</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Детальная статистика по разделам -->
      <div class="row">
        <!-- Авиакомпании -->
        <div class="col-md-6 mb-4">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-header bg-white border-0">
              <h5 class="mb-0">🏢 Статистика авиакомпаний</h5>
            </div>
            <div class="card-body">
              <div v-if="loadingAirlines" class="text-center py-3">
                <div class="spinner-border spinner-border-sm text-primary"></div>
              </div>
              <div v-else>
                <div class="stat-item d-flex justify-content-between py-2 border-bottom">
                  <span>Всего авиакомпаний:</span>
                  <strong class="text-primary">{{ airlineStats.count }}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Рейсы -->
        <div class="col-md-6 mb-4">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-header bg-white border-0">
              <h5 class="mb-0">🛫 Статистика рейсов</h5>
            </div>
            <div class="card-body">
              <div v-if="loadingFlights" class="text-center py-3">
                <div class="spinner-border spinner-border-sm text-primary"></div>
              </div>
              <div v-else>
                <div class="stat-item d-flex justify-content-between py-2 border-bottom">
                  <span>Всего рейсов:</span>
                  <strong class="text-primary">{{ flightStats.count }}</strong>
                </div>
                <div class="stat-item d-flex justify-content-between py-2 border-bottom">
                  <span>Средняя цена:</span>
                  <strong class="text-success">{{ flightStats.avg_price?.toFixed(2) }} руб.</strong>
                </div>
                <div class="stat-item d-flex justify-content-between py-2 border-bottom">
                  <span>Минимальная цена:</span>
                  <strong class="text-warning">{{ flightStats.min_price }} руб.</strong>
                </div>
                <div class="stat-item d-flex justify-content-between py-2">
                  <span>Максимальная цена:</span>
                  <strong class="text-danger">{{ flightStats.max_price }} руб.</strong>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Пассажиры -->
        <div class="col-md-6 mb-4">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-header bg-white border-0">
              <h5 class="mb-0">👥 Статистика пассажиров</h5>
            </div>
            <div class="card-body">
              <div v-if="loadingPassengers" class="text-center py-3">
                <div class="spinner-border spinner-border-sm text-primary"></div>
              </div>
              <div v-else>
                <div class="stat-item d-flex justify-content-between py-2 border-bottom">
                  <span>Всего пассажиров:</span>
                  <strong class="text-primary">{{ passengerStats.count }}</strong>
                </div>
                <div class="stat-item d-flex justify-content-between py-2 border-bottom">
                  <span>С телефоном:</span>
                  <strong class="text-success">{{ passengerStats.with_phone }}</strong>
                </div>
                <div class="stat-item d-flex justify-content-between py-2 border-bottom">
                  <span>Без телефона:</span>
                  <strong class="text-warning">{{ passengerStats.without_phone }}</strong>
                </div>
                <div class="stat-item d-flex justify-content-between py-2">
                  <span>С фото:</span>
                  <strong class="text-info">{{ passengerStats.with_photo }}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Тарифы -->
        <div class="col-md-6 mb-4">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-header bg-white border-0">
              <h5 class="mb-0">💰 Статистика тарифов</h5>
            </div>
            <div class="card-body">
              <div v-if="loadingRates" class="text-center py-3">
                <div class="spinner-border spinner-border-sm text-primary"></div>
              </div>
              <div v-else>
                <div class="stat-item d-flex justify-content-between py-2 border-bottom">
                  <span>Всего тарифов:</span>
                  <strong class="text-primary">{{ rateStats.count }}</strong>
                </div>
                <div class="stat-item d-flex justify-content-between py-2 border-bottom">
                  <span>Средний коэффициент:</span>
                  <strong class="text-success">{{ rateStats.avg_multiplier?.toFixed(2) }}x</strong>
                </div>
                <div class="stat-item d-flex justify-content-between py-2 border-bottom">
                  <span>Минимальный коэффициент:</span>
                  <strong class="text-warning">{{ rateStats.min_multiplier }}x</strong>
                </div>
                <div class="stat-item d-flex justify-content-between py-2">
                  <span>Максимальный коэффициент:</span>
                  <strong class="text-danger">{{ rateStats.max_multiplier }}x</strong>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Билеты -->
        <div class="col-md-6 mb-4">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-header bg-white border-0">
              <h5 class="mb-0">🎫 Статистика билетов</h5>
            </div>
            <div class="card-body">
              <div v-if="loadingTickets" class="text-center py-3">
                <div class="spinner-border spinner-border-sm text-primary"></div>
              </div>
              <div v-else>
                <div class="stat-item d-flex justify-content-between py-2 border-bottom">
                  <span>Всего билетов:</span>
                  <strong class="text-primary">{{ ticketStats.count }}</strong>
                </div>
                <div class="stat-item d-flex justify-content-between py-2 border-bottom">
                  <span>Билетов сегодня:</span>
                  <strong class="text-success">{{ ticketStats.today_count }}</strong>
                </div>
                <div class="stat-item d-flex justify-content-between py-2 border-bottom">
                  <span>С указанным местом:</span>
                  <strong class="text-info">{{ ticketStats.with_seat }}</strong>
                </div>
                <div class="stat-item d-flex justify-content-between py-2">
                  <span>Без указанного места:</span>
                  <strong class="text-warning">{{ ticketStats.without_seat }}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeMount } from 'vue'
import axios from 'axios'

const mainStats = ref([
  { icon: '🏢', title: 'Авиакомпаний', value: 0, color: 'text-info' },
  { icon: '🛫', title: 'Рейсов', value: 0, color: 'text-success' },
  { icon: '👥', title: 'Пассажиров', value: 0, color: 'text-warning' },
  { icon: '🎫', title: 'Билетов', value: 0, color: 'text-danger' }
])

const airlineStats = ref({})
const flightStats = ref({})
const passengerStats = ref({})
const rateStats = ref({})
const ticketStats = ref({})

const loadingAirlines = ref(false)
const loadingFlights = ref(false)
const loadingPassengers = ref(false)
const loadingRates = ref(false)
const loadingTickets = ref(false)

onBeforeMount(async () => {
  await fetchAllStats()
})

async function fetchAllStats() {
  await Promise.all([
    fetchMainStats(),
    fetchAirlinesStats(),
    fetchFlightsStats(),
    fetchPassengersStats(),
    fetchRatesStats(),
    fetchTicketsStats()
  ])
}

async function fetchMainStats() {
  try {
    const [airlinesRes, flightsRes, passengersRes, ticketsRes] = await Promise.all([
      axios.get('/api/airlines/stats/'),
      axios.get('/api/flights/stats/'),
      axios.get('/api/passengers/stats/'),
      axios.get('/api/tickets/stats/')
    ])
    
    mainStats.value[0].value = airlinesRes.data.count
    mainStats.value[1].value = flightsRes.data.count
    mainStats.value[2].value = passengersRes.data.count
    mainStats.value[3].value = ticketsRes.data.count
  } catch (error) {
    console.error('Error fetching main stats:', error)
  }
}

async function fetchAirlinesStats() {
  loadingAirlines.value = true
  try {
    const response = await axios.get('/api/airlines/stats/')
    airlineStats.value = response.data
  } catch (error) {
    console.error('Error fetching airline stats:', error)
  } finally {
    loadingAirlines.value = false
  }
}

async function fetchFlightsStats() {
  loadingFlights.value = true
  try {
    const response = await axios.get('/api/flights/stats/')
    flightStats.value = response.data
  } catch (error) {
    console.error('Error fetching flight stats:', error)
  } finally {
    loadingFlights.value = false
  }
}

async function fetchPassengersStats() {
  loadingPassengers.value = true
  try {
    const response = await axios.get('/api/passengers/stats/')
    passengerStats.value = response.data
  } catch (error) {
    console.error('Error fetching passenger stats:', error)
  } finally {
    loadingPassengers.value = false
  }
}

async function fetchRatesStats() {
  loadingRates.value = true
  try {
    const response = await axios.get('/api/rates/stats/')
    rateStats.value = response.data
  } catch (error) {
    console.error('Error fetching rate stats:', error)
  } finally {
    loadingRates.value = false
  }
}

async function fetchTicketsStats() {
  loadingTickets.value = true
  try {
    const response = await axios.get('/api/tickets/stats/')
    ticketStats.value = response.data
  } catch (error) {
    console.error('Error fetching ticket stats:', error)
  } finally {
    loadingTickets.value = false
  }
}
</script>

<style scoped>
.stat-item {
  transition: background-color 0.2s ease;
}

.stat-item:hover {
  background-color: #f8f9fa;
  border-radius: 4px;
  padding-left: 8px;
  padding-right: 8px;
}

.card {
  transition: transform 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
}
</style>
[file content end]