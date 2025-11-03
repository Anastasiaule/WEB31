[file name]: TicketsCrud.vue
[file content begin]
<script setup>
import axios from 'axios';
import { ref, onBeforeMount, computed } from 'vue';

const tickets = ref([]);
const flights = ref([]);
const passengers = ref([]);
const rates = ref([]);
const ticketToAdd = ref({ flight: '', passenger: '', rate: '', seat: '' });
const ticketToEdit = ref({});
const loading = ref(false);

// Статистика
const stats = ref({});

onBeforeMount(async () => {
  await fetchTickets();
  await fetchFlights();
  await fetchPassengers();
  await fetchRates();
  await fetchStats();
})

async function fetchTickets() {
  loading.value = true;
  const r = await axios.get('/api/tickets/');
  tickets.value = r.data;
  loading.value = false;
}

async function fetchStats() {
  const r = await axios.get("/api/tickets/stats/");
  stats.value = r.data;
}

async function fetchFlights() {
  const r = await axios.get('/api/flights/');
  flights.value = r.data;
}

async function fetchPassengers() {
  const r = await axios.get('/api/passengers/');
  passengers.value = r.data;
}

async function fetchRates() {
  const r = await axios.get('/api/rates/');
  rates.value = r.data;
}

async function onTicketAdd() {
  await axios.post("/api/tickets/", ticketToAdd.value);
  await fetchTickets();
  await fetchStats();
  ticketToAdd.value = { flight: '', passenger: '', rate: '', seat: '' };
}

async function onRemoveClick(ticket) {
  if (confirm(`Удалить билет для "${ticket.passenger_name}"?`)) {
    await axios.delete(`/api/tickets/${ticket.id}/`);
    await fetchTickets();
    await fetchStats();
  }
}

function onTicketEditClick(ticket) {
  ticketToEdit.value = { ...ticket };
}

async function onUpdateTicket() {
  await axios.put(`/api/tickets/${ticketToEdit.value.id}/`, ticketToEdit.value);
  await fetchTickets();
}

// Компьютед свойства
const todayTickets = computed(() => {
  const today = new Date().toDateString();
  return tickets.value.filter(ticket => 
    new Date(ticket.booking_date).toDateString() === today
  ).length;
});

const ticketsWithSeats = computed(() => {
  return tickets.value.filter(ticket => ticket.seat).length;
});
</script>

<template>
  <div>
    <!-- Статистика -->
    <div class="alert alert-info mb-4">
      <div class="row text-center">
        <div class="col-md-3">
          <strong>🎫 Всего билетов:</strong> {{ stats.count || 0 }}
        </div>
        <div class="col-md-3">
          <strong>📅 Сегодня:</strong> {{ stats.today_count || 0 }}
        </div>
        <div class="col-md-3">
          <strong>💺 С местами:</strong> {{ stats.with_seat || 0 }}
        </div>
        <div class="col-md-3">
          <strong>🚫 Без мест:</strong> {{ stats.without_seat || 0 }}
        </div>
      </div>
    </div>

    <!-- Форма добавления -->
    <div class="card shadow-sm mb-4 border-0">
      <div class="card-header bg-primary text-white py-3">
        <h5 class="mb-0">➕ Добавить билет</h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="onTicketAdd">
          <div class="row g-3 align-items-end">
            <div class="col-md-3">
              <label class="form-label">Рейс</label>
              <select class="form-select" v-model="ticketToAdd.flight" required>
                <option value="">Выберите рейс</option>
                <option v-for="flight in flights" :value="flight.id">
                  {{ flight.name }} - {{ flight.route }} ({{ flight.price }} руб.)
                </option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">Пассажир</label>
              <select class="form-select" v-model="ticketToAdd.passenger" required>
                <option value="">Выберите пассажира</option>
                <option v-for="passenger in passengers" :value="passenger.id">
                  {{ passenger.full_name }} ({{ passenger.passport }})
                </option>
              </select>
            </div>
            <div class="col-md-2">
              <label class="form-label">Тариф</label>
              <select class="form-select" v-model="ticketToAdd.rate" required>
                <option value="">Выберите тариф</option>
                <option v-for="rate in rates" :value="rate.id">
                  {{ rate.name }} ({{ rate.multiplier }}×)
                </option>
              </select>
            </div>
            <div class="col-md-2">
              <label class="form-label">Место</label>
              <input type="text" class="form-control" v-model="ticketToAdd.seat" 
                     placeholder="Например: 12A" />
            </div>
            <div class="col-md-2">
              <button class="btn btn-primary w-100" type="submit">
                <span>➕ Добавить</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Список билетов -->
    <div class="card shadow-sm border-0">
      <div class="card-header bg-white py-3">
        <h5 class="mb-0">🎫 Список билетов</h5>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center p-4">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="mt-2 text-muted">Загрузка билетов...</p>
        </div>

        <div v-else-if="tickets.length === 0" class="text-center p-5 text-muted">
          <div class="display-1 mb-3">🎫</div>
          <h5>Билетов пока нет</h5>
          <p>Добавьте первый билет используя форму выше</p>
        </div>

        <div v-else class="row row-cols-1 g-4">
          <div v-for="item in tickets" :key="item.id" class="col">
            <div class="card h-100 shadow-sm border-0">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                  <div class="flex-grow-1">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                      <h6 class="card-title fw-bold text-primary mb-0">
                        🎫 Билет #{{ item.id }}
                      </h6>
                      <small class="text-muted">
                        {{ new Date(item.booking_date).toLocaleDateString() }}
                      </small>
                    </div>
                    
                    <div class="row g-3">
                      <div class="col-md-4">
                        <div class="ticket-section">
                          <strong>👤 Пассажир</strong>
                          <div class="text-muted small">{{ item.passenger_name }}</div>
                        </div>
                      </div>
                      <div class="col-md-4">
                        <div class="ticket-section">
                          <strong>🛫 Рейс</strong>
                          <div class="text-muted small">{{ item.flight_name }}</div>
                        </div>
                      </div>
                      <div class="col-md-2">
                        <div class="ticket-section">
                          <strong>💰 Тариф</strong>
                          <div class="text-muted small">{{ item.rate_name }}</div>
                        </div>
                      </div>
                      <div class="col-md-2">
                        <div class="ticket-section">
                          <strong>💺 Место</strong>
                          <div class="text-muted small">{{ item.seat || '—' }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="btn-group btn-group-sm ms-3">
                    <button class="btn btn-outline-warning" 
                            @click="onTicketEditClick(item)" 
                            data-bs-toggle="modal" 
                            data-bs-target="#editTicketModal">
                      ✏️
                    </button>
                    <button class="btn btn-outline-danger" @click="onRemoveClick(item)">
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования -->
    <div class="modal fade" id="editTicketModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-warning text-dark">
            <h5 class="modal-title">✏️ Редактировать билет</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Рейс</label>
                <select class="form-select" v-model="ticketToEdit.flight">
                  <option v-for="flight in flights" :value="flight.id">
                    {{ flight.name }} - {{ flight.route }}
                  </option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Пассажир</label>
                <select class="form-select" v-model="ticketToEdit.passenger">
                  <option v-for="passenger in passengers" :value="passenger.id">
                    {{ passenger.full_name }}
                  </option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Тариф</label>
                <select class="form-select" v-model="ticketToEdit.rate">
                  <option v-for="rate in rates" :value="rate.id">
                    {{ rate.name }} ({{ rate.multiplier }}×)
                  </option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Место</label>
                <input type="text" class="form-control" v-model="ticketToEdit.seat" 
                       placeholder="Например: 12A" />
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">❌ Отмена</button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateTicket">
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
  transition: transform 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
}

.ticket-section {
  padding: 8px;
  border-radius: 8px;
  background-color: #f8f9fa;
}

.btn-group-sm > .btn {
  border-radius: 8px;
  margin-left: 4px;
}

.ticket-section strong {
  font-size: 0.85em;
  color: #495057;
}
</style>
[file content end]