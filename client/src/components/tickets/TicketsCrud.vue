<script setup>
import axios from 'axios';
import { ref, onBeforeMount } from 'vue';

const tickets = ref([]);
const flights = ref([]);
const passengers = ref([]);
const rates = ref([]);
const ticketToAdd = ref({ flight: '', passenger: '', rate: '', seat: '' });
const ticketToEdit = ref({});

onBeforeMount(async () => {
  await fetchTickets();
  await fetchFlights();
  await fetchPassengers();
  await fetchRates();
})

async function fetchTickets() {
  const r = await axios.get('/api/tickets/');
  tickets.value = r.data;
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
  ticketToAdd.value = { flight: '', passenger: '', rate: '', seat: '' };
}

async function onRemoveClick(ticket) {
  await axios.delete(`/api/tickets/${ticket.id}/`);
  await fetchTickets();
}

async function onTicketEditClick(ticket) {
  ticketToEdit.value = { ...ticket };
}

async function onUpdateTicket() {
  await axios.put(`/api/tickets/${ticketToEdit.value.id}/`, ticketToEdit.value);
  await fetchTickets();
}
</script>

<template>
  <form @submit.prevent="onTicketAdd" class="mb-4 p-3 border rounded">
    <div class="row g-2">
      <div class="col-md-3">
        <select class="form-select" v-model="ticketToAdd.flight" required>
          <option value="">Рейс</option>
          <option v-for="flight in flights" :value="flight.id">{{ flight.name }} - {{ flight.route }}</option>
        </select>
      </div>
      <div class="col-md-3">
        <select class="form-select" v-model="ticketToAdd.passenger" required>
          <option value="">Пассажир</option>
          <option v-for="passenger in passengers" :value="passenger.id">{{ passenger.full_name }}</option>
        </select>
      </div>
      <div class="col-md-2">
        <select class="form-select" v-model="ticketToAdd.rate" required>
          <option value="">Тариф</option>
          <option v-for="rate in rates" :value="rate.id">{{ rate.name }}</option>
        </select>
      </div>
      <div class="col-md-2">
        <input type="text" class="form-control" v-model="ticketToAdd.seat" placeholder="Место" />
      </div>
      <div class="col-md-2">
        <button class="btn btn-primary w-100" type="submit">Добавить</button>
      </div>
    </div>
  </form>

  <div class="list-group">
    <div v-for="item in tickets" :key="item.id" class="list-group-item">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <strong>{{ item.passenger_name }}</strong> → {{ item.flight_name }}<br>
          <small class="text-muted">Тариф: {{ item.rate_name }} • Место: {{ item.seat || 'не указано' }} • {{ new Date(item.booking_date).toLocaleString() }}</small>
        </div>
        <div>
          <button class="btn btn-warning btn-sm me-2" @click="onTicketEditClick(item)" data-bs-toggle="modal" data-bs-target="#editTicketModal">
            ✏️
          </button>
          <button class="btn btn-danger btn-sm" @click="onRemoveClick(item)">🗑️</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Модальное окно редактирования билета -->
  <div class="modal fade" id="editTicketModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать билет</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="row g-3">
            <div class="col-md-6">
              <label>Рейс</label>
              <select class="form-select" v-model="ticketToEdit.flight">
                <option v-for="flight in flights" :value="flight.id">{{ flight.name }} - {{ flight.route }}</option>
              </select>
            </div>
            <div class="col-md-6">
              <label>Пассажир</label>
              <select class="form-select" v-model="ticketToEdit.passenger">
                <option v-for="passenger in passengers" :value="passenger.id">{{ passenger.full_name }}</option>
              </select>
            </div>
            <div class="col-md-6">
              <label>Тариф</label>
              <select class="form-select" v-model="ticketToEdit.rate">
                <option v-for="rate in rates" :value="rate.id">{{ rate.name }}</option>
              </select>
            </div>
            <div class="col-md-6">
              <label>Место</label>
              <input type="text" class="form-control" v-model="ticketToEdit.seat" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateTicket">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>