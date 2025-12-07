<script setup>
import axios from "axios"
import { ref, onMounted, computed } from "vue"

const flights = ref([])
const airlines = ref([])
const stats = ref({})
const loading = ref(false)

const user = ref({ is_superuser: false })

const newFlight = ref({
  name: "",
  route: "",
  airline: "",
  price: "",
  departure_time: "",
  arrival_time: ""
})

const editFlight = ref({})

const showFilters = ref(false)
const filters = ref({
  name: "",
  route: "",
  airline: "",
  minPrice: "",
  maxPrice: ""
})

onMounted(async () => {
  await loadUser()
  await loadAirlines()
  await loadFlights()
  await loadStats()
})

async function loadUser() {
  try {
    const r = await axios.get("/api/user/info/")
    user.value = r.data
  } catch {}
}

async function loadAirlines() {
  const r = await axios.get("/api/airlines/")
  airlines.value = r.data
}

async function loadFlights() {
  loading.value = true
  const r = await axios.get("/api/flights/")
  flights.value = r.data
  loading.value = false
}

async function loadStats() {
  const r = await axios.get("/api/flights/stats/")
  stats.value = r.data
}

async function addFlight() {
  await axios.post("/api/flights/", newFlight.value)
  await loadFlights()
  await loadStats()

  newFlight.value = {
    name: "",
    route: "",
    airline: "",
    price: "",
    departure_time: "",
    arrival_time: ""
  }
}

function startEdit(f) {
  editFlight.value = { ...f }
}

async function saveFlight() {
  await axios.put(`/api/flights/${editFlight.value.id}/`, editFlight.value)
  await loadFlights()
}

async function removeFlight(f) {
  if (!confirm("Удалить рейс?")) return
  await axios.delete(`/api/flights/${f.id}/`)
  await loadFlights()
  await loadStats()
}

// айди авиакомпани
function getAirlineName(airlineId) {
  const airline = airlines.value.find(a => a.id === airlineId)
  return airline ? airline.name : "Неизвестная авиакомпания"
}

// Фильтрация
const filteredFlights = computed(() => {
  return flights.value.filter(f => {
    if (filters.value.name && !f.name.toLowerCase().includes(filters.value.name.toLowerCase())) return false
    if (filters.value.route && !f.route.toLowerCase().includes(filters.value.route.toLowerCase())) return false
    if (filters.value.airline && f.airline != filters.value.airline) return false
    if (filters.value.minPrice && f.price < parseInt(filters.value.minPrice)) return false
    if (filters.value.maxPrice && f.price > parseInt(filters.value.maxPrice)) return false
    return true
  })
})

function clearFilters() {
  filters.value = {
    name: "",
    route: "",
    airline: "",
    minPrice: "",
    maxPrice: ""
  }
}

function timeFmt(t) {
  return new Date(t).toLocaleString("ru-RU")
}

function priceFmt(p) {
  return new Intl.NumberFormat("ru-RU").format(p)
}
</script>

<template>
<div class="container py-4">
  <!-- Статистика -->
  <div class="stats-card mb-4">
    <h5 class="mb-3">Статистика рейсов</h5>
    <div class="row text-center">
      <div class="col"><span class="stats-label">Всего:</span> <span class="stats-value">{{ stats.count || 0 }}</span></div>
      <div class="col"><span class="stats-label">Средняя цена:</span> <span class="stats-value">{{ priceFmt(stats.avg_price || 0) }} ₽</span></div>
      <div class="col"><span class="stats-label">Отфильтровано:</span> <span class="stats-value">{{ filteredFlights.length }}</span></div>
    </div>
  </div>

  <!-- Форма добавления для админа -->
  <div v-if="user.is_superuser" class="card mb-4">
    <div class="card-header bg-light">
      <h5 class="mb-0">Добавить рейс</h5>
    </div>
    <div class="card-body">
      <div class="row g-3">
        <div class="col-md-3">
          <input v-model="newFlight.name" class="form-control form-control-sm" placeholder="Номер рейса">
        </div>
        <div class="col-md-4">
          <input v-model="newFlight.route" class="form-control form-control-sm" placeholder="Маршрут">
        </div>
        <div class="col-md-3">
          <select v-model="newFlight.airline" class="form-select form-select-sm">
            <option value="">Авиакомпания</option>
            <option v-for="a in airlines" :value="a.id">{{ a.name }}</option>
          </select>
        </div>
        <div class="col-md-2">
          <input type="number" v-model="newFlight.price" class="form-control form-control-sm" placeholder="Цена">
        </div>
        <div class="col-md-3">
          <input type="datetime-local" v-model="newFlight.departure_time" class="form-control form-control-sm">
        </div>
        <div class="col-md-3">
          <input type="datetime-local" v-model="newFlight.arrival_time" class="form-control form-control-sm">
        </div>
        <div class="col-md-2">
          <button class="btn btn-primary btn-sm w-100" @click="addFlight">Добавить</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Список рейсов -->
  <div class="card">
    <div class="card-header bg-light d-flex justify-content-between align-items-center">
      <h5 class="mb-0">Список рейсов</h5>
      <button class="btn btn-sm btn-outline-secondary" @click="showFilters = !showFilters">
        Фильтры
      </button>
    </div>
    
    <!-- Фильтры -->
    <div v-if="showFilters" class="card-body border-bottom">
      <div class="row g-2 mb-2">
        <div class="col-md-2">
          <input v-model="filters.name" class="form-control form-control-sm" placeholder="Номер рейса">
        </div>
        <div class="col-md-3">
          <input v-model="filters.route" class="form-control form-control-sm" placeholder="Маршрут">
        </div>
        <div class="col-md-2">
          <select v-model="filters.airline" class="form-select form-select-sm">
            <option value="">Все авиакомпании</option>
            <option v-for="a in airlines" :value="a.id">{{ a.name }}</option>
          </select>
        </div>
        <div class="col-md-2">
          <input v-model="filters.minPrice" type="number" class="form-control form-control-sm" placeholder="Цена от">
        </div>
        <div class="col-md-2">
          <input v-model="filters.maxPrice" type="number" class="form-control form-control-sm" placeholder="Цена до">
        </div>
        <div class="col-md-1">
          <button class="btn btn-sm btn-outline-danger w-100" @click="clearFilters">×</button>
        </div>
      </div>
    </div>
    
    <div class="card-body">
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border spinner-border-sm text-primary"></div>
        <p class="mt-2 text-muted">Загрузка...</p>
      </div>
      
      <div v-else-if="filteredFlights.length === 0" class="text-center text-muted py-4">
        Нет рейсов
      </div>
      
      <div v-else class="list-group list-group-flush">
        <div v-for="f in filteredFlights" :key="f.id" class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h6 class="mb-1"><strong>{{ f.name }}</strong> — {{ f.route }}</h6>
              <small class="text-muted">
                {{ getAirlineName(f.airline) }} • 
                Вылет: {{ timeFmt(f.departure_time) }} • 
                Прилет: {{ timeFmt(f.arrival_time) }} • 
                Цена: {{ priceFmt(f.price) }} ₽
              </small>
            </div>
            
            <div v-if="user.is_superuser" class="btn-group btn-group-sm">
              <button class="btn btn-outline-warning" data-bs-toggle="modal" data-bs-target="#editModal" @click="startEdit(f)">Изменить</button>
              <button class="btn btn-outline-danger" @click="removeFlight(f)">Удалить</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- модалка редактирования -->
  <div class="modal fade" id="editModal">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать рейс</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label class="form-label">Номер рейса</label>
            <input v-model="editFlight.name" class="form-control">
          </div>
          <div class="mb-3">
            <label class="form-label">Маршрут</label>
            <input v-model="editFlight.route" class="form-control">
          </div>
          <div class="mb-3">
            <label class="form-label">Авиакомпания</label>
            <select v-model="editFlight.airline" class="form-select">
              <option v-for="a in airlines" :value="a.id">{{ a.name }}</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label">Цена</label>
            <input type="number" v-model="editFlight.price" class="form-control">
          </div>
          <div class="mb-3">
            <label class="form-label">Время вылета</label>
            <input type="datetime-local" v-model="editFlight.departure_time" class="form-control">
          </div>
          <div class="mb-3">
            <label class="form-label">Время прилета</label>
            <input type="datetime-local" v-model="editFlight.arrival_time" class="form-control">
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="saveFlight">Сохранить</button>
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

.stats-label {
  color: #6c757d;
  font-size: 0.9rem;
}

.stats-value {
  font-weight: 600;
  color: #0d6efd;
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
</style>