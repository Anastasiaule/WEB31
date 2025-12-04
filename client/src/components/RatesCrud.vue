<script setup>
import axios from "axios";
import { ref, onBeforeMount, computed } from "vue";

const rates = ref([]);
const loading = ref(false);

const rateToAdd = ref({ name: "", multiplier: 1.0 });
const rateToEdit = ref({});
const stats = ref({});

const user = ref({ is_superuser: false, is_authenticated: false });

onBeforeMount(async () => {
  // Получаем информацию о текущем пользователе
  try {
    const r = await axios.get("/api/user/info/");
    user.value = r.data;
  } catch (e) {
    console.log("Ошибка получения user:", e);
  }

  await fetchRates();
  await fetchStats();
});

async function fetchRates() {
  loading.value = true;
  const r = await axios.get("/api/rates/");
  rates.value = r.data;
  loading.value = false;
}

async function fetchStats() {
  const r = await axios.get("/api/rates/stats/");
  stats.value = r.data;
}

async function addRate() {
  if (!user.value.is_superuser) return;

  await axios.post("/api/rates/", rateToAdd.value);
  rateToAdd.value = { name: "", multiplier: 1.0 };

  await fetchRates();
  await fetchStats();
}

async function removeRate(rate) {
  if (!user.value.is_superuser) return;

  if (confirm(`Удалить тариф "${rate.name}"?`)) {
    await axios.delete(`/api/rates/${rate.id}/`);
    await fetchRates();
    await fetchStats();
  }
}

function editRateOpen(rate) {
  rateToEdit.value = { ...rate };
}

async function updateRate() {
  if (!user.value.is_superuser) return;

  await axios.put(`/api/rates/${rateToEdit.value.id}/`, rateToEdit.value);
  await fetchRates();
}

const premiumRates = computed(() =>
  rates.value.filter((i) => i.multiplier > 1).length
);

const discountRates = computed(() =>
  rates.value.filter((i) => i.multiplier < 1).length
);
</script>
<template>
  <div class="container mt-4">

    <!-- Статистика -->
    <div class="mb-4 p-3 border rounded bg-light">
      <div class="row text-center small">
        <div class="col">
          <strong>Всего:</strong> {{ stats.count || 0 }}
        </div>
        <div class="col">
          <strong>Премиум:</strong> {{ premiumRates }}
        </div>
        <div class="col">
          <strong>Скидочные:</strong> {{ discountRates }}
        </div>
        <div class="col">
          <strong>Средний ×:</strong> {{ stats.avg_multiplier?.toFixed(2) || "0.00" }}
        </div>
      </div>
    </div>

    <!-- Добавление тарифа -->
    <div v-if="user.is_superuser" class="mb-4 p-3 border rounded">
      <h5 class="mb-3">Добавить тариф</h5>

      <form @submit.prevent="addRate" class="row g-3">
        <div class="col-md-6">
          <label class="form-label">Название</label>
          <input v-model="rateToAdd.name" type="text" class="form-control" required>
        </div>

        <div class="col-md-4">
          <label class="form-label">Коэффициент</label>
          <input v-model="rateToAdd.multiplier" type="number" step="0.1" min="0.1"
                 class="form-control" required>
        </div>

        <div class="col-md-2 d-flex align-items-end">
          <button class="btn btn-primary w-100">Добавить</button>
        </div>
      </form>
    </div>

    <!-- Таблица тарифов -->
    <div class="border rounded p-3">
      <h5 class="mb-3">Список тарифов</h5>

      <div v-if="loading" class="text-center py-3">
        Загрузка…
      </div>

      <table v-else class="table table-striped align-middle">
        <thead>
          <tr>
            <th>Название</th>
            <th>Коэффициент</th>
            <th>Тип</th>
            <th v-if="user.is_superuser" class="text-end">Действия</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="r in rates" :key="r.id">
            <td>{{ r.name }}</td>
            <td>{{ r.multiplier }}×</td>

            <td>
              <span v-if="r.multiplier > 1" class="text-danger">Премиум</span>
              <span v-else-if="r.multiplier < 1" class="text-success">Скидочный</span>
              <span v-else class="text-primary">Стандартный</span>
            </td>

            <td v-if="user.is_superuser" class="text-end">
              <button class="btn btn-sm btn-outline-secondary me-2"
                      data-bs-toggle="modal"
                      data-bs-target="#editModal"
                      @click="editRateOpen(r)">
                Изменить
              </button>

              <button class="btn btn-sm btn-outline-danger"
                      @click="removeRate(r)">
                Удалить
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>


    <!-- Модалка редактирования -->
    <div class="modal fade" id="editModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">

          <div class="modal-header">
            <h5 class="modal-title">Редактировать тариф</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>

          <div class="modal-body">

            <label class="form-label">Название</label>
            <input v-model="rateToEdit.name" type="text" class="form-control mb-3">

            <label class="form-label">Коэффициент</label>
            <input v-model="rateToEdit.multiplier" type="number" step="0.1" min="0.1"
                   class="form-control">
          </div>

          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button class="btn btn-primary" data-bs-dismiss="modal" @click="updateRate">
              Сохранить
            </button>
          </div>

        </div>
      </div>
    </div>

  </div>
</template>
<style scoped>
.table th {
  font-weight: 600;
}

.border {
  background: #fff;
}
</style>
