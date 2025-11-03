[file name]: FlightsCrud.vue
[file content begin]
<script setup>
import axios from 'axios'
import { ref, onBeforeMount, computed } from 'vue'

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

// Статистика
const stats = ref({});

// ======================
// API-запросы
// ======================

onBeforeMount(async () => {
  await fetchFlights()
  await fetchAirlines()
  await fetchStats()
})

async function fetchStats() {
  const r = await axios.get("/api/flights/stats/");
  stats.value = r.data;
}

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
  if (confirm(`Удалить рейс "${flight.name}"?`)) {
    await axios.delete(`/api/flights/${flight.id}/`)
    await fetchFlights()
    await fetchStats()
  }
}

function onFlightEditClick(flight) {
  flightToEdit.value = { ...flight }
}

async function onUpdateFlight() {
  await axios.put(`/api/flights/${flightToEdit.value.id}/`, flightToEdit.value)
  await fetchFlights()
}

// Компьютед свойства
const activeFlights = computed(() => {
  const now = new Date();
  return flights.value.filter(flight => new Date(flight.departure_time) > now).length;
});

const upcomingFlights = computed(() => {
  const now = new Date();
  const next24h = new Date(now.getTime() + 24 * 60 * 60 * 1000);
  return flights.value.filter(flight => {
    const depTime = new Date(flight.departure_time);
    return depTime > now && depTime <= next24h;
  }).length;
});

const formatCurrency = (price) => {
  return new Intl.NumberFormat('ru-RU').format(price);
};

const formatDateTime = (dateString) => {
  return new Date(dateString).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getFlightStatus = (flight) => {
  const now = new Date();
  const depTime = new Date(flight.departure_time);
  const arrTime = new Date(flight.arrival_time);
  
  if (now > arrTime) return { text: 'Завершен', class: 'secondary' };
  if (now > depTime && now < arrTime) return { text: 'В пути', class: 'success' };
  if (depTime - now <= 24 * 60 * 60 * 1000) return { text: 'Скоро', class: 'warning' };
  return { text: 'По расписанию', class: 'primary' };
};
</script>

<template>
  <div>
    <!-- Статистика -->
    <div class="alert alert-info mb-4">
      <div class="row text-center">
        <div class="col-md-3">
          <strong>🛫 Всего рейсов:</strong> {{ stats.count || 0 }}
        </div>
        <div class="col-md-3">
          <strong>⏰ Активных:</strong> {{ activeFlights }}
        </div>
        <div class="col-md-3">
          <strong>📅 В ближайшие 24ч:</strong> {{ upcomingFlights }}
        </div>
        <div class="col-md-3">
          <strong>💰 Средняя цена:</strong> {{ formatCurrency(stats.avg_price || 0) }} руб.
        </div>
      </div>
      <div class="row text-center mt-2">
        <div class="col-md-6">
          <strong>📉 Минимальная цена:</strong> {{ formatCurrency(stats.min_price || 0) }} руб.
        </div>
        <div class="col-md-6">
          <strong>📈 Максимальная цена:</strong> {{ formatCurrency(stats.max_price || 0) }} руб.
        </div>
      </div>
    </div>

    <!-- Форма добавления рейса -->
    <div class="card shadow-sm mb-4 border-0">
      <div class="card-header bg-primary text-white py-3">
        <h5 class="mb-0">➕ Добавить рейс</h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="onFlightAdd">
          <div class="row g-3 align-items-end">
            <div class="col-md-2">
              <label class="form-label">Номер рейса</label>
              <input type="text" class="form-control" v-model="flightToAdd.name" 
                     placeholder="SU-1234" required />
            </div>
            <div class="col-md-3">
              <label class="form-label">Маршрут</label>
              <input type="text" class="form-control" v-model="flightToAdd.route" 
                     placeholder="Москва - Сочи" />
            </div>
            <div class="col-md-2">
              <label class="form-label">Авиакомпания</label>
              <select class="form-select" v-model="flightToAdd.airline" required>
                <option value="">Выберите авиакомпанию</option>
                <option v-for="a in airlines" :key="a.id" :value="a.id">{{ a.name }}</option>
              </select>
            </div>
            <div class="col-md-1">
              <label class="form-label">Цена</label>
              <input type="number" class="form-control" v-model="flightToAdd.price" 
                     placeholder="0" min="0" step="100" />
            </div>
            <div class="col-md-2">
              <label class="form-label">Вылет</label>
              <input type="datetime-local" class="form-control" v-model="flightToAdd.departure_time" />
            </div>
            <div class="col-md-2">
              <label class="form-label">Прилёт</label>
              <input type="datetime-local" class="form-control" v-model="flightToAdd.arrival_time" />
            </div>
            <div class="col-md-auto">
              <button class="btn btn-primary w-100" type="submit">
                <span>➕ Добавить</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Список рейсов -->
    <div class="card shadow-sm border-0">
      <div class="card-header bg-white py-3">
        <h5 class="mb-0">🛫 Список рейсов</h5>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center p-5">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="mt-2 text-muted">Загрузка рейсов...</p>
        </div>

        <div v-else-if="flights.length === 0" class="text-center p-5 text-muted">
          <div class="display-1 mb-3">🛫</div>
          <h5>Рейсов пока нет</h5>
          <p>Добавьте первый рейс используя форму выше</p>
        </div>

        <div v-else class="row row-cols-1 g-4">
          <div v-for="item in flights" :key="item.id" class="col">
            <div class="card h-100 shadow-sm border-0 flight-card">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <div class="flex-grow-1">
                    <div class="d-flex align-items-center mb-2">
                      <h6 class="card-title fw-bold text-primary mb-0 me-3">
                        {{ item.name }}
                      </h6>
                      <span class="badge" :class="`bg-${getFlightStatus(item).class}`">
                        {{ getFlightStatus(item).text }}
                      </span>
                    </div>
                    <p class="card-text text-muted mb-2">
                      <strong>🛣️ {{ item.route }}</strong>
                    </p>
                    <div class="flight-details small text-muted">
                      <div class="row g-3">
                        <div class="col-md-4">
                          <div class="detail-item">
                            <strong>🏢 Авиакомпания:</strong> 
                            <span class="ms-1">{{ item.airline_name || '—' }}</span>
                          </div>
                        </div>
                        <div class="col-md-4">
                          <div class="detail-item">
                            <strong>💰 Цена:</strong> 
                            <span class="ms-1 text-success fw-bold">{{ formatCurrency(item.price) }} руб.</span>
                          </div>
                        </div>
                        <div class="col-md-4">
                          <div class="detail-item">
                            <strong>✈️ Вылет:</strong> 
                            <span class="ms-1">{{ formatDateTime(item.departure_time) }}</span>
                          </div>
                        </div>
                        <div class="col-md-4">
                          <div class="detail-item">
                            <strong>🛬 Прилёт:</strong> 
                            <span class="ms-1">{{ formatDateTime(item.arrival_time) }}</span>
                          </div>
                        </div>
                        <div class="col-md-4">
                          <div class="detail-item">
                            <strong>⏱️ Длительность:</strong> 
                            <span class="ms-1">
                              {{
                                Math.round(
                                  (new Date(item.arrival_time) - new Date(item.departure_time)) / 
                                  (60 * 60 * 1000)
                                )
                              }} ч.
                            </span>
                          </div>
                        </div>
                        <div class="col-md-4">
                          <div class="detail-item">
                            <strong>🎫 Статус:</strong> 
                            <span class="ms-1 badge" :class="`bg-${getFlightStatus(item).class}`">
                              {{ getFlightStatus(item).text }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="btn-group btn-group-sm ms-3">
                    <button class="btn btn-outline-warning"
                            data-bs-toggle="modal"
                            data-bs-target="#editFlightModal"
                            @click="onFlightEditClick(item)">
                      ✏️
                    </button>
                    <button class="btn btn-outline-danger" @click="onRemoveClick(item)">
                      🗑️
                    </button>
                  </div>
                </div>
                
                <!-- Progress bar for flight status -->
                <div v-if="getFlightStatus(item).text !== 'Завершен'" class="flight-progress mt-3">
                  <div class="progress" style="height: 6px;">
                    <div class="progress-bar" 
                         :class="`bg-${getFlightStatus(item).class}`"
                         :style="{
                           width: getFlightStatus(item).text === 'В пути' ? '50%' : 
                                 getFlightStatus(item).text === 'Скоро' ? '25%' : '10%'
                         }">
                    </div>
                  </div>
                </div>
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
          <div class="modal-header bg-warning text-dark">
            <h5 class="modal-title">✏️ Редактировать рейс</h5>
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
              <div class="col-md-6">
                <label class="form-label">Цена</label>
                <div class="input-group">
                  <input type="number" class="form-control" v-model="flightToEdit.price" />
                  <span class="input-group-text">руб.</span>
                </div>
              </div>
              <div class="col-md-6">
                <label class="form-label">Время вылета</label>
                <input type="datetime-local" class="form-control" v-model="flightToEdit.departure_time" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Время прилёта</label>
                <input type="datetime-local" class="form-control" v-model="flightToEdit.arrival_time" />
              </div>
              
              <!-- Preview of flight details -->
              <div v-if="flightToEdit.name" class="col-12 mt-3">
                <div class="card border-info">
                  <div class="card-header bg-info text-white py-2">
                    <small>👀 Предпросмотр изменений</small>
                  </div>
                  <div class="card-body py-2">
                    <div class="row small text-muted">
                      <div class="col-md-4">
                        <strong>Рейс:</strong> {{ flightToEdit.name }}
                      </div>
                      <div class="col-md-4">
                        <strong>Маршрут:</strong> {{ flightToEdit.route }}
                      </div>
                      <div class="col-md-4">
                        <strong>Цена:</strong> {{ formatCurrency(flightToEdit.price) }} руб.
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">❌ Отмена</button>
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
.flight-card {
  border-radius: 12px;
  transition: all 0.3s ease;
  border-left: 4px solid #0d6efd;
}

.flight-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}

.detail-item {
  padding: 4px 0;
  border-bottom: 1px solid #f8f9fa;
}

.detail-item:last-child {
  border-bottom: none;
}

.flight-progress .progress {
  border-radius: 10px;
  background-color: #e9ecef;
}

.flight-progress .progress-bar {
  border-radius: 10px;
  transition: width 0.5s ease;
}

.btn-group-sm > .btn {
  border-radius: 8px;
  margin-left: 4px;
}

.card-title {
  color: #0d6efd;
  font-size: 1.1rem;
}

.flight-details {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .flight-details .row {
    margin: 0;
  }
  
  .flight-details .col-md-4 {
    margin-bottom: 8px;
  }
  
  .btn-group {
    margin-top: 10px;
  }
}

/* Status badges */
.badge.bg-primary { background-color: #0d6efd !important; }
.badge.bg-success { background-color: #198754 !important; }
.badge.bg-warning { background-color: #ffc107 !important; color: #000; }
.badge.bg-secondary { background-color: #6c757d !important; }
</style>
[file content end]