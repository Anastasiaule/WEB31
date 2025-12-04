<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import { RouterLink } from "vue-router"
import { useUserStore } from "@/stores/user_store"
import { storeToRefs } from "pinia"

// Авторизация
const username = ref("")
const password = ref("")

const userStore = useUserStore()
const { userInfo } = storeToRefs(userStore)

function login() {
  userStore.login(username.value, password.value)
}

// Быстрая статистика
const quickStats = ref([
  { icon: "🏢", title: "Авиакомпаний", value: "0" },
  { icon: "🛫", title: "Рейсов", value: "0" },
  { icon: "👥", title: "Пассажиров", value: "0" },
  { icon: "🎫", title: "Билетов", value: "0" },
])

// Навигация
const navCards = ref([
  { icon: "🏢", title: "Авиакомпании", link: "/airlines" },
  { icon: "🛫", title: "Рейсы", link: "/flights" },
  { icon: "👥", title: "Пассажиры", link: "/passengers" },
  { icon: "💰", title: "Тарифы", link: "/rates" },
  { icon: "🎫", title: "Билеты", link: "/tickets" },
])

// Авиакомпании + последние рейсы
const airlines = ref([])
const recentFlights = ref([])

const loadingAirlines = ref(false)
const loadingFlights = ref(false)

onMounted(async () => {
  await loadStats()
  await loadAirlines()
  await loadFlights()
})

// ======================
// Загрузка данных
// ======================
async function loadStats() {
  try {
    const [a, f, p, t] = await Promise.all([
      axios.get("/api/airlines/stats/"),
      axios.get("/api/flights/stats/"),
      axios.get("/api/passengers/stats/"),
      axios.get("/api/tickets/stats/"),
    ])
    quickStats.value[0].value = a.data.count
    quickStats.value[1].value = f.data.count
    quickStats.value[2].value = p.data.count
    quickStats.value[3].value = t.data.count
  } catch {}
}

async function loadAirlines() {
  loadingAirlines.value = true
  try {
    const r = await axios.get("/api/airlines/")
    airlines.value = r.data.slice(0, 12)
  } finally {
    loadingAirlines.value = false
  }
}

async function loadFlights() {
  loadingFlights.value = true
  try {
    const r = await axios.get("/api/flights/")

    // упрощённая нормализация airline_name
    recentFlights.value = r.data.slice(0, 5).map(f => ({
      ...f,
      airline_name:
        f.airline_name ||
        f.airline?.name ||
        airlines.value.find(a => a.id === f.airline)?.name ||
        "—",
    }))
  } finally {
    loadingFlights.value = false
  }
}
</script>

<template>
  <!-- Приветствие -->
  <div v-if="userInfo">
    <h4>Привет, {{ userInfo.username }}</h4>
  </div>

  <div class="container py-4">

    <!-- Статистика -->
    <div class="row mb-4">
      <div class="col-md-3" v-for="stat in quickStats" :key="stat.title">
        <div class="p-3 bg-light border rounded text-center mb-3">
          <div class="display-6">{{ stat.icon }}</div>
          <h3 class="mt-2">{{ stat.value }}</h3>
          <div class="text-muted">{{ stat.title }}</div>
        </div>
      </div>
    </div>

    <!-- Навигация -->
    <div class="row g-3 mb-5">
      <div class="col-md-4" v-for="card in navCards" :key="card.title">
        <RouterLink :to="card.link" class="text-decoration-none">
          <div class="p-4 border rounded text-center bg-white hover-card">
            <div class="display-4 mb-2">{{ card.icon }}</div>
            <h5>{{ card.title }}</h5>
          </div>
        </RouterLink>
      </div>
    </div>

    <!-- Авиакомпании -->
    <div class="mb-5">
      <h4 class="mb-3">🏢 Наши авиакомпании</h4>

      <div v-if="loadingAirlines" class="text-center p-3">Загрузка...</div>

      <div v-else class="row g-3">
        <div class="col-6 col-md-3 col-lg-2" v-for="a in airlines" :key="a.id">
          <div class="border rounded p-2 text-center bg-white">
            <img
              v-if="a.picture"
              :src="a.picture"
              class="img-fluid mb-2"
              style="max-height: 50px"
            />
            <div v-else class="display-6 mb-1">🏢</div>
            <small class="fw-bold">{{ a.name }}</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Последние рейсы -->
    <div>
      <h4 class="mb-3">🛫 Последние рейсы</h4>

      <div v-if="loadingFlights" class="text-center p-3">Загрузка...</div>

      <div v-else class="list-group">
        <div
          class="list-group-item d-flex justify-content-between"
          v-for="f in recentFlights"
          :key="f.id"
        >
          <div>
            <b>{{ f.name }}</b> — {{ f.route }} <br />
            <small class="text-muted">
              {{ new Date(f.departure_time).toLocaleString() }}
              • {{ f.price }} руб.
            </small>
          </div>
          <span class="badge bg-primary">{{ f.airline_name }}</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Модальное окно авторизации -->
  <div
    v-if="userInfo && !userInfo.is_authenticated"
    class="modal fade show d-block"
    style="background: rgba(0,0,0,0.5);"
  >
    <div class="modal-dialog">
      <div class="modal-content p-3">

        <h5 class="mb-3">Пожалуйста, авторизуйтесь</h5>

        <form @submit.prevent="login" class="d-flex flex-column gap-2">
          <input v-model="username" class="form-control" placeholder="username" />
          <input v-model="password" type="password" class="form-control" placeholder="password" />
          <button class="btn btn-primary">Войти</button>
        </form>

      </div>
    </div>
  </div>
</template>

<style scoped>
.hover-card {
  transition: 0.2s;
}
.hover-card:hover {
  background: #f8f9fa;
  transform: translateY(-3px);
}
</style>
