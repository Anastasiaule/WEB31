<script setup>

import axios from 'axios'
import { ref, onBeforeMount, computed } from 'vue'
import Cookies from 'js-cookie'

const flights = ref([])
const airlines = ref([])
const loading = ref(false)
const flightToAdd = ref({
  name: '',
  route: '',
  airline: '',
  price: 0,
  departure_time: '',
  arrival_time: ''
})
const flightToEdit = ref({})

// Статистика
const stats = ref({})

// Информация о пользователе
const user = ref({ is_superuser: false, is_authenticated: false })

// ======================
// API-запросы
// ======================
onBeforeMount(async () => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken")
  axios.defaults.withCredentials = true

  try {
    const r = await axios.get("/api/user/info/")
    if (r.data && typeof r.data.is_superuser !== 'undefined') user.value = r.data
  } catch (err) {
    console.error("Не удалось получить данные пользователя:", err)
  }

  await fetchAirlines()
  await fetchFlights()
  await fetchStats()
})

async function fetchStats() {
  const r = await axios.get("/api/flights/stats/")
  stats.value = r.data
}

async function fetchFlights() {
  loading.value = true
  const r = await axios.get('/api/flights/')

  // 🔥 ИСПРАВЛЕНО: теперь airline_name всегда корректный
  flights.value = r.data.map(f => ({
    ...f,
    airline_name:
      f.airline_name ||                 // если DRF уже прислал поле
      (f.airline && airlines.value.find(a => a.id === f.airline)?.name) || // если airline = id
      (f.airline?.name) ||              // если airline = объект
      '—'
  }))

  loading.value = false
}

async function fetchAirlines() {
  const r = await axios.get('/api/airlines/')
  airlines.value = r.data
}

// ======================
// CRUD
// ======================
async function onFlightAdd() {
  if (!user.value.is_superuser) return
  await axios.post('/api/flights/', flightToAdd.value)
  await fetchFlights()
  await fetchStats()

  flightToAdd.value = {
    name: '',
    route: '',
    airline: '',
    price: 0,
    departure_time: '',
    arrival_time: ''
  }
}

async function onRemoveClick(flight) {
  if (!user.value.is_superuser) return
  if (confirm(`Удалить рейс "${flight.name}"?`)) {
    await axios.delete(`/api/flights/${flight.id}/`)
    await fetchFlights()
    await fetchStats()
  }
}

function onFlightEditClick(flight) {
  if (!user.value.is_superuser) return
  flightToEdit.value = { ...flight }
}

async function onUpdateFlight() {
  if (!user.value.is_superuser) return
  await axios.put(`/api/flights/${flightToEdit.value.id}/`, flightToEdit.value)
  await fetchFlights()
}

// ======================
// Вычисления
// ======================
const activeFlights = computed(() => {
  const now = new Date()
  return flights.value.filter(f => new Date(f.departure_time) > now).length
})

const upcomingFlights = computed(() => {
  const now = new Date()
  const next24h = new Date(now.getTime() + 24 * 60 * 60 * 1000)
  return flights.value.filter(f => {
    const dep = new Date(f.departure_time)
    return dep > now && dep <= next24h
  }).length
})

const formatCurrency = p => new Intl.NumberFormat('ru-RU').format(p)
const formatDateTime = d =>
  new Date(d).toLocaleString('ru-RU', {
    day:'2-digit', month:'2-digit', year:'numeric',
    hour:'2-digit', minute:'2-digit'
  })

const getFlightStatus = f => {
  const now = new Date()
  const dep = new Date(f.departure_time)
  const arr = new Date(f.arrival_time)
  if (now > arr) return { text: 'Завершен', class: 'secondary' }
  if (now > dep && now < arr) return { text: 'В пути', class: 'success' }
  if (dep - now <= 86400000) return { text: 'Скоро', class: 'warning' }
  return { text: 'По расписанию', class: 'primary' }
}
</script>


<template>
<div>
  <!-- Статистика -->
  <div class="alert alert-info mb-4">
    <div class="row text-center">
      <div class="col-md-3"><strong>🛫 Всего рейсов:</strong> {{ stats.count || 0 }}</div>
      <div class="col-md-3"><strong>⏰ Активных:</strong> {{ activeFlights }}</div>
      <div class="col-md-3"><strong>📅 В ближайшие 24ч:</strong> {{ upcomingFlights }}</div>
      <div class="col-md-3"><strong>💰 Средняя цена:</strong> {{ formatCurrency(stats.avg_price || 0) }} руб.</div>
    </div>
    <div class="row text-center mt-2">
      <div class="col-md-6"><strong>📉 Минимальная цена:</strong> {{ formatCurrency(stats.min_price || 0) }} руб.</div>
      <div class="col-md-6"><strong>📈 Максимальная цена:</strong> {{ formatCurrency(stats.max_price || 0) }} руб.</div>
    </div>
  </div>

  <!-- Форма добавления рейса (только суперюзер) -->
  <div v-if="user.is_superuser" class="card shadow-sm mb-4 border-0">
    <div class="card-header bg-primary text-white py-3">
      <h5 class="mb-0">➕ Добавить рейс</h5>
    </div>
    <div class="card-body">
      <form @submit.prevent="onFlightAdd">
        <div class="row g-3 align-items-end">
          <div class="col-md-2"><label class="form-label">Номер рейса</label><input type="text" class="form-control" v-model="flightToAdd.name" placeholder="SU-1234" required /></div>
          <div class="col-md-3"><label class="form-label">Маршрут</label><input type="text" class="form-control" v-model="flightToAdd.route" placeholder="Москва - Сочи" /></div>
          <div class="col-md-2"><label class="form-label">Авиакомпания</label>
            <select class="form-select" v-model="flightToAdd.airline" required>
              <option value="">Выберите авиакомпанию</option>
              <option v-for="a in airlines" :key="a.id" :value="a.id">{{ a.name }}</option>
            </select>
          </div>
          <div class="col-md-1"><label class="form-label">Цена</label><input type="number" class="form-control" v-model="flightToAdd.price" placeholder="0" min="0" step="100" /></div>
          <div class="col-md-2"><label class="form-label">Вылет</label><input type="datetime-local" class="form-control" v-model="flightToAdd.departure_time" /></div>
          <div class="col-md-2"><label class="form-label">Прилёт</label><input type="datetime-local" class="form-control" v-model="flightToAdd.arrival_time" /></div>
          <div class="col-md-auto"><button class="btn btn-primary w-100" type="submit">➕ Добавить</button></div>
        </div>
      </form>
    </div>
  </div>

  <!-- Список рейсов -->
  <div class="card shadow-sm border-0">
    <div class="card-header bg-white py-3"><h5 class="mb-0">🛫 Список рейсов</h5></div>
    <div class="card-body">
      <div v-if="loading" class="text-center p-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-2 text-muted">Загрузка рейсов...</p></div>
      <div v-else-if="flights.length === 0" class="text-center p-5 text-muted"><div class="display-1 mb-3">🛫</div><h5>Рейсов пока нет</h5><p>Добавьте первый рейс используя форму выше</p></div>
      <div v-else class="row row-cols-1 g-4">
        <div v-for="item in flights" :key="item.id" class="col">
          <div class="card h-100 shadow-sm border-0 flight-card">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start mb-3">
                <div class="flex-grow-1">
                  <div class="d-flex align-items-center mb-2">
                    <h6 class="card-title fw-bold text-primary mb-0 me-3">{{ item.name }}</h6>
                    <span class="badge" :class="`bg-${getFlightStatus(item).class}`">{{ getFlightStatus(item).text }}</span>
                  </div>
                  <p class="card-text text-muted mb-2"><strong>🛣️ {{ item.route }}</strong></p>
                  <div class="flight-details small text-muted">
                    <div class="row g-3">
                      <div class="col-md-4"><strong>🏢 Авиакомпания:</strong> {{ item.airline_name || '—' }}</div>
                      <div class="col-md-4"><strong>💰 Цена:</strong> <span class="text-success fw-bold">{{ formatCurrency(item.price) }} руб.</span></div>
                      <div class="col-md-4"><strong>✈️ Вылет:</strong> {{ formatDateTime(item.departure_time) }}</div>
                      <div class="col-md-4"><strong>🛬 Прилёт:</strong> {{ formatDateTime(item.arrival_time) }}</div>
                      <div class="col-md-4"><strong>⏱️ Длительность:</strong> {{ Math.round((new Date(item.arrival_time)-new Date(item.departure_time))/(60*60*1000)) }} ч.</div>
                      <div class="col-md-4"><strong>🎫 Статус:</strong> <span class="badge" :class="`bg-${getFlightStatus(item).class}`">{{ getFlightStatus(item).text }}</span></div>
                    </div>
                  </div>
                </div>
                <!-- Кнопки редактирования/удаления -->
                <div v-if="user.is_superuser" class="btn-group btn-group-sm ms-3">
                  <button class="btn btn-outline-warning" data-bs-toggle="modal" data-bs-target="#editFlightModal" @click="onFlightEditClick(item)">✏️</button>
                  <button class="btn btn-outline-danger" @click="onRemoveClick(item)">🗑️</button>
                </div>
              </div>
              <!-- Progress bar -->
              <div v-if="getFlightStatus(item).text !== 'Завершен'" class="flight-progress mt-3">
                <div class="progress" style="height: 6px;">
                  <div class="progress-bar" :class="`bg-${getFlightStatus(item).class}`" :style="{width: getFlightStatus(item).text==='В пути'?'50%':getFlightStatus(item).text==='Скоро'?'25%':'10%'}"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Модальное окно редактирования (только суперюзер) -->
  <div v-if="user.is_superuser" class="modal fade" id="editFlightModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header bg-warning text-dark">
          <h5 class="modal-title">✏️ Редактировать рейс</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="row g-3">
            <div class="col-md-6"><label class="form-label">Номер рейса</label><input type="text" class="form-control" v-model="flightToEdit.name" /></div>
            <div class="col-md-6"><label class="form-label">Маршрут</label><input type="text" class="form-control" v-model="flightToEdit.route" /></div>
            <div class="col-md-6"><label class="form-label">Авиакомпания</label>
              <select class="form-select" v-model="flightToEdit.airline">
                <option v-for="a in airlines" :key="a.id" :value="a.id">{{ a.name }}</option>
              </select>
            </div>
            <div class="col-md-6"><label class="form-label">Цена</label>
              <div class="input-group"><input type="number" class="form-control" v-model="flightToEdit.price" /><span class="input-group-text">руб.</span></div>
            </div>
            <div class="col-md-6"><label class="form-label">Время вылета</label><input type="datetime-local" class="form-control" v-model="flightToEdit.departure_time" /></div>
            <div class="col-md-6"><label class="form-label">Время прилёта</label><input type="datetime-local" class="form-control" v-model="flightToEdit.arrival_time" /></div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">❌ Отмена</button>
          <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateFlight">💾 Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</div>
</template>
