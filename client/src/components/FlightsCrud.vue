<script setup>
import axios from "axios"
import { ref, onMounted } from "vue"

// =========================
// Данные
// =========================
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

// =========================
// Загрузка данных
// =========================
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

// =========================
// CRUD
// =========================
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

// =========================
// Утилиты
// =========================
function timeFmt(t) {
  return new Date(t).toLocaleString("ru-RU")
}

function priceFmt(p) {
  return new Intl.NumberFormat("ru-RU").format(p)
}
</script>


<template>
<div class="container py-3">

  <!-- Статистика -->
  <div class="p-3 mb-3 bg-light border rounded text-center">
    <div><b>Всего рейсов:</b> {{ stats.count || 0 }}</div>
    <div><b>Средняя цена:</b> {{ priceFmt(stats.avg_price || 0) }} руб.</div>
  </div>

  <!-- Форма добавления -->
  <div v-if="user.is_superuser" class="border rounded p-3 mb-4">
    <h5 class="mb-3">Добавить рейс</h5>

    <div class="row g-2">
      <div class="col-md-2"><input v-model="newFlight.name" class="form-control" placeholder="Номер"></div>
      <div class="col-md-3"><input v-model="newFlight.route" class="form-control" placeholder="Маршрут"></div>

      <div class="col-md-3">
        <select v-model="newFlight.airline" class="form-select">
          <option value="">Авиакомпания</option>
          <option v-for="a in airlines" :value="a.id">{{ a.name }}</option>
        </select>
      </div>

      <div class="col-md-2"><input type="number" v-model="newFlight.price" class="form-control" placeholder="Цена"></div>

      <div class="col-md-2 d-grid">
        <button class="btn btn-primary" @click="addFlight">Добавить</button>
      </div>

      <div class="col-md-3"><input type="datetime-local" v-model="newFlight.departure_time" class="form-control"></div>
      <div class="col-md-3"><input type="datetime-local" v-model="newFlight.arrival_time" class="form-control"></div>
    </div>
  </div>

  <!-- Список -->
  <div class="border rounded p-3">
    <h5 class="mb-3">Список рейсов</h5>

    <div v-if="loading" class="text-center p-4">Загрузка...</div>

    <div v-else-if="flights.length === 0" class="text-center text-muted p-4">
      Рейсов нет
    </div>

    <div v-else class="list-group">
      <div v-for="f in flights" :key="f.id" class="list-group-item">
        <div class="d-flex justify-content-between">
          <div>
            <b>{{ f.name }}</b> — {{ f.route }}<br>
            <small class="text-muted">
              {{ f.airline_name }} • {{ timeFmt(f.departure_time) }} → {{ timeFmt(f.arrival_time) }}  
              • {{ priceFmt(f.price) }} ₽
            </small>
          </div>

          <div v-if="user.is_superuser" class="d-flex gap-2">
            <button class="btn btn-sm btn-warning" data-bs-toggle="modal" data-bs-target="#editModal" @click="startEdit(f)">✏</button>
            <button class="btn btn-sm btn-danger" @click="removeFlight(f)">✖</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Модальное окно редактирования -->
  <div class="modal fade" id="editModal">
    <div class="modal-dialog">
      <div class="modal-content">

        <div class="modal-header">
          <h5 class="modal-title">Редактировать рейс</h5>
          <button class="btn-close" data-bs-dismiss="modal"></button>
        </div>

        <div class="modal-body">

          <input v-model="editFlight.name" class="form-control mb-2" placeholder="Номер">
          <input v-model="editFlight.route" class="form-control mb-2" placeholder="Маршрут">

          <select v-model="editFlight.airline" class="form-select mb-2">
            <option v-for="a in airlines" :value="a.id">{{ a.name }}</option>
          </select>

          <input type="number" v-model="editFlight.price" class="form-control mb-2" placeholder="Цена">

          <input type="datetime-local" v-model="editFlight.departure_time" class="form-control mb-2">
          <input type="datetime-local" v-model="editFlight.arrival_time" class="form-control">

        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button class="btn btn-primary" data-bs-dismiss="modal" @click="saveFlight">Сохранить</button>
        </div>

      </div>
    </div>
  </div>

</div>
</template>

<style scoped>
.list-group-item {
  border-radius: 6px;
  margin-bottom: 6px;
}
</style>
