<script setup>
import axios from 'axios'
import { ref, onBeforeMount } from 'vue'

// Состояния
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

// ======================
// API-запросы
// ======================

onBeforeMount(async () => {
  await fetchFlights()
  await fetchAirlines()
})
const stats = ref({});

async function fetchStats() {
  const r = await axios.get("/api/flights/stats/");
  stats.value = r.data;
}

onBeforeMount(async () => {
  await fetchFlights();
  await fetchStats();
});
async function fetchFlights() {
  loading.value = true
  const r = await axios.get('/api/flights/')
  flights.value = r.data
  loading.value = false
}

async function fetchAirlines() {
  const r = await axios.get('/api/airlines/')
  airlines.value = r.data
}

// ======================
// CRUD операции
// ======================

async function onFlightAdd() {
  await axios.post('/api/flights/', flightToAdd.value)
  await fetchFlights()
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
  if (confirm(`Удалить рейс ${flight.name}?`)) {
    await axios.delete(`/api/flights/${flight.id}/`)
    await fetchFlights()
  }
}

function onFlightEditClick(flight) {
  flightToEdit.value = { ...flight }
}

async function onUpdateFlight() {
  await axios.put(`/api/flights/${flightToEdit.value.id}/`, flightToEdit.value)
  await fetchFlights()
}
</script>

<template>
    <div class="alert alert-secondary">
  <strong>Статистика рейсов:</strong><br>
  Всего: {{ stats.count }}<br>
  Средняя цена: {{ stats.avg_price }}<br>
  Мин. цена: {{ stats.min_price }}<br>
  Макс. цена: {{ stats.max_price }}
</div>
  <div>
    <!-- Форма добавления рейса -->
    <form @submit.prevent="onFlightAdd" class="mb-4 p-3 border rounded bg-light shadow-sm">
      <h5 class="mb-3">Добавить новый рейс</h5>
      <div class="row g-2">
        <div class="col-md-2">
          <input type="text" class="form-control" v-model="flightToAdd.name" placeholder="Номер рейса" required />
        </div>
        <div class="col-md-3">
          <input type="text" class="form-control" v-model="flightToAdd.route" placeholder="Маршрут" />
        </div>
        <div class="col-md-2">
          <select class="form-select" v-model="flightToAdd.airline" required>
            <option value="">Авиакомпания</option>
            <option v-for="a in airlines" :key="a.id" :value="a.id">{{ a.name }}</option>
          </select>
        </div>
        <div class="col-md-1">
          <input type="number" class="form-control" v-model="flightToAdd.price" placeholder="Цена" min="0" />
        </div>
        <div class="col-md-2">
          <input type="datetime-local" class="form-control" v-model="flightToAdd.departure_time" placeholder="Вылет" />
        </div>
        <div class="col-md-2">
          <input type="datetime-local" class="form-control" v-model="flightToAdd.arrival_time" placeholder="Прилёт" />
        </div>
        <div class="col-md-auto">
          <button class="btn btn-primary w-100" type="submit">Добавить</button>
        </div>
      </div>
    </form>

    <!-- Список рейсов -->
    <div v-if="loading" class="text-center p-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-2">Загрузка рейсов...</p>
    </div>

    <div v-else class="row row-cols-1 row-cols-md-2 g-3">
      <div v-for="item in flights" :key="item.id" class="col">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <h5 class="card-title mb-1">{{ item.name }}</h5>
                <p class="card-text mb-1">
                  <strong>{{ item.route }}</strong><br />
                  ✈️ {{ new Date(item.departure_time).toLocaleString() }} → 🛬
                  {{ new Date(item.arrival_time).toLocaleString() }}
                </p>
                <small class="text-muted">{{ item.airline_name || '—' }} • {{ item.price }} руб.</small>
              </div>
              <div>
                <button
                  class="btn btn-sm btn-outline-warning me-1"
                  data-bs-toggle="modal"
                  data-bs-target="#editFlightModal"
                  @click="onFlightEditClick(item)"
                >
                  ✏️
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="onRemoveClick(item)">🗑️</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования рейса -->
    <div class="modal fade" id="editFlightModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">Редактировать рейс</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Номер рейса</label>
                <input type="text" class="form-control" v-model="flightToEdit.name" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Маршрут</label>
                <input type="text" class="form-control" v-model="flightToEdit.route" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Авиакомпания</label>
                <select class="form-select" v-model="flightToEdit.airline">
                  <option v-for="a in airlines" :key="a.id" :value="a.id">{{ a.name }}</option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label">Цена</label>
                <input type="number" class="form-control" v-model="flightToEdit.price" />
              </div>
              <div class="col-md-3">
                <label class="form-label">Время вылета</label>
                <input type="datetime-local" class="form-control" v-model="flightToEdit.departure_time" />
              </div>
              <div class="col-md-3">
                <label class="form-label">Время прилёта</label>
                <input type="datetime-local" class="form-control" v-model="flightToEdit.arrival_time" />
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateFlight">
              💾 Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  border-radius: 12px;
}
.card-title {
  color: #0d6efd;
}
</style>
