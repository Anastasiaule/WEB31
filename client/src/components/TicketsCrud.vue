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

// Компьютед свойства
const todayTickets = computed(() => {
  const today = new Date().toDateString();
  return tickets.value.filter(t => new Date(t.booking_date).toDateString() === today).length;
});
</script>

<template>
  <div class="container mt-4">

    <!-- Статистика -->
    <div class="mb-4 p-3 border rounded bg-light">
      <div class="row text-center small">
        <div class="col"><strong>Всего:</strong> {{ stats.count || 0 }}</div>
        <div class="col"><strong>Сегодня:</strong> {{ stats.today_count || 0 }}</div>
        <div class="col"><strong>С местами:</strong> {{ stats.with_seat || 0 }}</div>
        <div class="col"><strong>Без мест:</strong> {{ stats.without_seat || 0 }}</div>
      </div>
    </div>

    <!-- Форма добавления -->
    <div class="mb-4 p-3 border rounded">
      <h5>Добавить билет</h5>
      <form @submit.prevent="addTicket" class="row g-3">
        <div class="col-md-3">
          <select class="form-select" v-model="ticketToAdd.flight" required>
            <option value="">Выберите рейс</option>
            <option v-for="f in flights" :value="f.id">{{ f.name }} - {{ f.route }}</option>
          </select>
        </div>
        <div class="col-md-3">
          <select class="form-select" v-model="ticketToAdd.passenger" required>
            <option value="">Выберите пассажира</option>
            <option v-for="p in passengers" :value="p.id">{{ p.full_name }}</option>
          </select>
        </div>
        <div class="col-md-2">
          <select class="form-select" v-model="ticketToAdd.rate" required>
            <option value="">Выберите тариф</option>
            <option v-for="r in rates" :value="r.id">{{ r.name }} ({{ r.multiplier }}×)</option>
          </select>
        </div>
        <div class="col-md-2">
          <input type="text" class="form-control" v-model="ticketToAdd.seat" placeholder="Место" />
        </div>
        <div class="col-md-2">
          <button class="btn btn-primary w-100">Добавить</button>
        </div>
      </form>
    </div>

    <!-- Таблица билетов -->
    <div class="border rounded p-3">
      <h5>Список билетов</h5>
      <div v-if="loading" class="text-center py-3">Загрузка…</div>
      <table v-else class="table table-striped align-middle">
        <thead>
          <tr>
            <th>ID</th>
            <th>Пассажир</th>
            <th>Рейс</th>
            <th>Тариф</th>
            <th>Место</th>
            <th>Дата</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in tickets" :key="t.id">
            <td>{{ t.id }}</td>
            <td>{{ t.passenger_name }}</td>
            <td>{{ t.flight_name }}</td>
            <td>{{ t.rate_name }}</td>
            <td>{{ t.seat || '—' }}</td>
            <td>{{ new Date(t.booking_date).toLocaleDateString() }}</td>
            <td>
              <button class="btn btn-sm btn-outline-secondary me-2"
                      data-bs-toggle="modal" data-bs-target="#editTicketModal"
                      @click="editTicketOpen(t)">Изменить</button>
              <button class="btn btn-sm btn-outline-danger" @click="removeTicket(t)">Удалить</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Модалка редактирования -->
    <div class="modal fade" id="editTicketModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header"><h5>Редактировать билет</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-md-6">
                <select class="form-select" v-model="ticketToEdit.flight">
                  <option v-for="f in flights" :value="f.id">{{ f.name }} - {{ f.route }}</option>
                </select>
              </div>
              <div class="col-md-6">
                <select class="form-select" v-model="ticketToEdit.passenger">
                  <option v-for="p in passengers" :value="p.id">{{ p.full_name }}</option>
                </select>
              </div>
              <div class="col-md-6">
                <select class="form-select" v-model="ticketToEdit.rate">
                  <option v-for="r in rates" :value="r.id">{{ r.name }} ({{ r.multiplier }}×)</option>
                </select>
              </div>
              <div class="col-md-6">
                <input type="text" class="form-control" v-model="ticketToEdit.seat" placeholder="Место" />
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button class="btn btn-primary" data-bs-dismiss="modal" @click="updateTicket">Сохранить</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.table th { font-weight: 600; }
</style>
