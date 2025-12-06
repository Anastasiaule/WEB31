<script setup>
import axios from "axios";
import { ref, onBeforeMount, computed } from "vue";

const tickets = ref([]);
const flights = ref([]);
const passengers = ref([]);
const rates = ref([]);
const ticketToAdd = ref({ flight: "", passenger: "", rate: "", seat: "" });
const ticketToEdit = ref({});
const loading = ref(false);
const stats = ref({});

// Фильтры
const showFilters = ref(false);
const filters = ref({
  passenger: "",
  flight: "",
  rate: "",
  seat: "",
  date: ""
});

onBeforeMount(async () => {
  await fetchFlights();
  await fetchPassengers();
  await fetchRates();
  await fetchTickets();
  await fetchStats();
});

async function fetchTickets() {
  loading.value = true;
  tickets.value = (await axios.get("/api/tickets/")).data;
  loading.value = false;
}

async function fetchStats() {
  stats.value = (await axios.get("/api/tickets/stats/")).data;
}

async function fetchFlights() {
  flights.value = (await axios.get("/api/flights/")).data;
}

async function fetchPassengers() {
  passengers.value = (await axios.get("/api/passengers/")).data;
}

async function fetchRates() {
  rates.value = (await axios.get("/api/rates/")).data;
}

async function addTicket() {
  await axios.post("/api/tickets/", ticketToAdd.value);
  ticketToAdd.value = { flight: "", passenger: "", rate: "", seat: "" };
  await fetchTickets();
  await fetchStats();
}

async function removeTicket(ticket) {
  if (confirm(`Удалить билет для "${ticket.passenger_name}"?`)) {
    await axios.delete(`/api/tickets/${ticket.id}/`);
    await fetchTickets();
    await fetchStats();
  }
}

function editTicketOpen(ticket) {
  ticketToEdit.value = { ...ticket };
}

async function updateTicket() {
  await axios.put(`/api/tickets/${ticketToEdit.value.id}/`, ticketToEdit.value);
  await fetchTickets();
}

// Фильтрация
const filteredTickets = computed(() => {
  return tickets.value.filter(t => {
    if (filters.value.passenger && !t.passenger_name.toLowerCase().includes(filters.value.passenger.toLowerCase())) return false
    if (filters.value.flight && !t.flight_name.toLowerCase().includes(filters.value.flight.toLowerCase())) return false
    if (filters.value.rate && !t.rate_name.toLowerCase().includes(filters.value.rate.toLowerCase())) return false
    if (filters.value.seat && !t.seat.toLowerCase().includes(filters.value.seat.toLowerCase())) return false
    if (filters.value.date) {
      const ticketDate = new Date(t.booking_date).toISOString().split('T')[0];
      if (ticketDate !== filters.value.date) return false
    }
    return true
  })
})

function clearFilters() {
  filters.value = {
    passenger: "",
    flight: "",
    rate: "",
    seat: "",
    date: ""
  }
}

// Компьютед свойства
const todayTickets = computed(() => {
  const today = new Date().toDateString();
  return tickets.value.filter(t => new Date(t.booking_date).toDateString() === today).length;
});
</script>

<template>
<div class="container py-4">
  <!-- Статистика -->
  <div class="stats-card mb-4">
    <h5 class="mb-3">Статистика билетов</h5>
    <div class="row text-center">
      <div class="col"><span class="stats-label">Всего:</span> <span class="stats-value">{{ stats.count || 0 }}</span></div>
      <div class="col"><span class="stats-label">Сегодня:</span> <span class="stats-value">{{ stats.today_count || 0 }}</span></div>
      <div class="col"><span class="stats-label">С местами:</span> <span class="stats-value">{{ stats.with_seat || 0 }}</span></div>
      <div class="col"><span class="stats-label">Без мест:</span> <span class="stats-value">{{ stats.without_seat || 0 }}</span></div>
      <div class="col"><span class="stats-label">Отфильтровано:</span> <span class="stats-value">{{ filteredTickets.length }}</span></div>
    </div>
  </div>

  <!-- Форма добавления -->
  <div class="card mb-4">
    <div class="card-header bg-light">
      <h5 class="mb-0">Добавить билет</h5>
    </div>
    <div class="card-body">
      <div class="row g-3">
        <div class="col-md-3">
          <select class="form-select form-select-sm" v-model="ticketToAdd.flight" required>
            <option value="">Выберите рейс</option>
            <option v-for="f in flights" :value="f.id">{{ f.name }} - {{ f.route }}</option>
          </select>
        </div>
        <div class="col-md-3">
          <select class="form-select form-select-sm" v-model="ticketToAdd.passenger" required>
            <option value="">Выберите пассажира</option>
            <option v-for="p in passengers" :value="p.id">{{ p.full_name }}</option>
          </select>
        </div>
        <div class="col-md-2">
          <select class="form-select form-select-sm" v-model="ticketToAdd.rate" required>
            <option value="">Выберите тариф</option>
            <option v-for="r in rates" :value="r.id">{{ r.name }} ({{ r.multiplier }}×)</option>
          </select>
        </div>
        <div class="col-md-2">
          <input type="text" class="form-control form-control-sm" v-model="ticketToAdd.seat" placeholder="Место">
        </div>
        <div class="col-md-2">
          <button class="btn btn-primary btn-sm w-100" @click="addTicket">Добавить</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Таблица билетов -->
  <div class="card">
    <div class="card-header bg-light d-flex justify-content-between align-items-center">
      <h5 class="mb-0">Список билетов</h5>
      <button class="btn btn-sm btn-outline-secondary" @click="showFilters = !showFilters">
        Фильтры
      </button>
    </div>
    
    <!-- Фильтры -->
    <div v-if="showFilters" class="card-body border-bottom">
      <div class="row g-2 mb-2">
        <div class="col-md-2">
          <input v-model="filters.passenger" class="form-control form-control-sm" placeholder="Пассажир">
        </div>
        <div class="col-md-2">
          <input v-model="filters.flight" class="form-control form-control-sm" placeholder="Рейс">
        </div>
        <div class="col-md-2">
          <input v-model="filters.rate" class="form-control form-control-sm" placeholder="Тариф">
        </div>
        <div class="col-md-2">
          <input v-model="filters.seat" class="form-control form-control-sm" placeholder="Место">
        </div>
        <div class="col-md-2">
          <input v-model="filters.date" type="date" class="form-control form-control-sm" placeholder="Дата">
        </div>
        <div class="col-md-2">
          <button class="btn btn-sm btn-outline-danger w-100" @click="clearFilters">×</button>
        </div>
      </div>
    </div>
    
    <div class="card-body">
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border spinner-border-sm text-primary"></div>
        <p class="mt-2 text-muted">Загрузка...</p>
      </div>
      
      <table v-else class="table table-hover table-sm">
        <thead>
          <tr>
            <th>ID</th>
            <th>Пассажир</th>
            <th>Рейс</th>
            <th>Тариф</th>
            <th>Место</th>
            <th>Дата</th>
            <th class="text-end">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in filteredTickets" :key="t.id">
            <td>{{ t.id }}</td>
            <td>{{ t.passenger_name }}</td>
            <td>{{ t.flight_name }}</td>
            <td>{{ t.rate_name }}</td>
            <td>{{ t.seat || '—' }}</td>
            <td>{{ new Date(t.booking_date).toLocaleDateString() }}</td>
            <td class="text-end">
              <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-warning" data-bs-toggle="modal" data-bs-target="#editTicketModal" @click="editTicketOpen(t)">Изменить</button>
                <button class="btn btn-outline-danger" @click="removeTicket(t)">Удалить</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- Модальное окно редактирования -->
  <div class="modal fade" id="editTicketModal">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать билет</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Рейс</label>
              <select class="form-select" v-model="ticketToEdit.flight">
                <option v-for="f in flights" :value="f.id">{{ f.name }} - {{ f.route }}</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label">Пассажир</label>
              <select class="form-select" v-model="ticketToEdit.passenger">
                <option v-for="p in passengers" :value="p.id">{{ p.full_name }}</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label">Тариф</label>
              <select class="form-select" v-model="ticketToEdit.rate">
                <option v-for="r in rates" :value="r.id">{{ r.name }} ({{ r.multiplier }}×)</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label">Место</label>
              <input type="text" class="form-control" v-model="ticketToEdit.seat">
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="updateTicket">Сохранить</button>
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

.table {
  margin-bottom: 0;
}

.table th {
  font-weight: 600;
  background-color: #f8f9fa;
}
</style>