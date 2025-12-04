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
<div class="container py-4">
  <!-- Статистика -->
  <div class="stats-card mb-4">
    <h5 class="mb-3">Статистика тарифов</h5>
    <div class="row text-center">
      <div class="col"><span class="stats-label">Всего:</span> <span class="stats-value">{{ stats.count || 0 }}</span></div>
      <div class="col"><span class="stats-label">Премиум:</span> <span class="stats-value">{{ premiumRates }}</span></div>
      <div class="col"><span class="stats-label">Скидочные:</span> <span class="stats-value">{{ discountRates }}</span></div>
      <div class="col"><span class="stats-label">Средний ×:</span> <span class="stats-value">{{ stats.avg_multiplier?.toFixed(2) || "0.00" }}</span></div>
    </div>
  </div>

  <!-- Форма добавления (только для админа) -->
  <div v-if="user.is_superuser" class="card mb-4">
    <div class="card-header bg-light">
      <h5 class="mb-0">Добавить тариф</h5>
    </div>
    <div class="card-body">
      <div class="row g-3">
        <div class="col-md-5">
          <input v-model="rateToAdd.name" type="text" class="form-control form-control-sm" placeholder="Название тарифа">
        </div>
        <div class="col-md-4">
          <input v-model="rateToAdd.multiplier" type="number" step="0.1" min="0.1" 
                 class="form-control form-control-sm" placeholder="Коэффициент">
        </div>
        <div class="col-md-3">
          <button class="btn btn-primary btn-sm w-100" @click="addRate">Добавить</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Таблица тарифов -->
  <div class="card">
    <div class="card-header bg-light">
      <h5 class="mb-0">Список тарифов</h5>
    </div>
    <div class="card-body">
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border spinner-border-sm text-primary"></div>
        <p class="mt-2 text-muted">Загрузка...</p>
      </div>
      
      <table v-else class="table table-hover table-sm">
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
              <span v-if="r.multiplier > 1" class="badge bg-danger">Премиум</span>
              <span v-else-if="r.multiplier < 1" class="badge bg-success">Скидочный</span>
              <span v-else class="badge bg-primary">Стандартный</span>
            </td>
            <td v-if="user.is_superuser" class="text-end">
              <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-warning" data-bs-toggle="modal" data-bs-target="#editModal" @click="editRateOpen(r)">Изменить</button>
                <button class="btn btn-outline-danger" @click="removeRate(r)">Удалить</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- Модальное окно редактирования -->
  <div class="modal fade" id="editModal">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать тариф</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label class="form-label">Название</label>
            <input v-model="rateToEdit.name" type="text" class="form-control">
          </div>
          <div class="mb-3">
            <label class="form-label">Коэффициент</label>
            <input v-model="rateToEdit.multiplier" type="number" step="0.1" min="0.1" class="form-control">
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="updateRate">Сохранить</button>
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

.badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}
</style>
