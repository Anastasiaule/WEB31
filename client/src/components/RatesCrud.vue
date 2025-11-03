[file name]: RatesCrud.vue
[file content begin]
<script setup>
import axios from 'axios';
import { ref, onBeforeMount, computed } from 'vue';

const rates = ref([]);
const rateToAdd = ref({ name: '', multiplier: 1.0 });
const rateToEdit = ref({});
const loading = ref(false);

// Статистика
const stats = ref({});

onBeforeMount(async () => {
  await fetchRates();
  await fetchStats();
})

async function fetchRates() {
  loading.value = true;
  const r = await axios.get('/api/rates/');
  rates.value = r.data;
  loading.value = false;
}

async function fetchStats() {
  const r = await axios.get("/api/rates/stats/");
  stats.value = r.data;
}

async function onRateAdd() {
  await axios.post("/api/rates/", rateToAdd.value);
  await fetchRates();
  await fetchStats();
  rateToAdd.value = { name: '', multiplier: 1.0 };
}

async function onRemoveClick(rate) {
  if (confirm(`Удалить тариф "${rate.name}"?`)) {
    await axios.delete(`/api/rates/${rate.id}/`);
    await fetchRates();
    await fetchStats();
  }
}

function onRateEditClick(rate) {
  rateToEdit.value = { ...rate };
}

async function onUpdateRate() {
  await axios.put(`/api/rates/${rateToEdit.value.id}/`, rateToEdit.value);
  await fetchRates();
}

// Компьютед свойства
const premiumRates = computed(() => {
  return rates.value.filter(rate => rate.multiplier > 1.0).length;
});

const discountRates = computed(() => {
  return rates.value.filter(rate => rate.multiplier < 1.0).length;
});
</script>

<template>
  <div>
    <!-- Статистика -->
    <div class="alert alert-info mb-4">
      <div class="row text-center">
        <div class="col-md-3">
          <strong>💰 Всего тарифов:</strong> {{ stats.count || 0 }}
        </div>
        <div class="col-md-3">
          <strong>📈 Премиум (×>1):</strong> {{ premiumRates }}
        </div>
        <div class="col-md-3">
          <strong>📉 Скидочные (×<1):</strong> {{ discountRates }}
        </div>
        <div class="col-md-3">
          <strong>⚡ Средний коэффициент:</strong> {{ stats.avg_multiplier?.toFixed(2) || '0.00' }}x
        </div>
      </div>
    </div>

    <!-- Форма добавления -->
    <div class="card shadow-sm mb-4 border-0">
      <div class="card-header bg-primary text-white py-3">
        <h5 class="mb-0">➕ Добавить тариф</h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="onRateAdd">
          <div class="row g-3 align-items-end">
            <div class="col-md-5">
              <label class="form-label">Название тарифа</label>
              <input type="text" class="form-control" v-model="rateToAdd.name" 
                     placeholder="Например: Бизнес-класс" required />
            </div>
            <div class="col-md-4">
              <label class="form-label">Коэффициент</label>
              <div class="input-group">
                <input type="number" step="0.1" min="0.1" class="form-control" 
                       v-model="rateToAdd.multiplier" placeholder="1.0" required />
                <span class="input-group-text">×</span>
              </div>
              <small class="form-text text-muted">
                <span v-if="rateToAdd.multiplier > 1" class="text-danger">📈 Премиум тариф</span>
                <span v-else-if="rateToAdd.multiplier < 1" class="text-success">📉 Скидочный тариф</span>
                <span v-else class="text-primary">⚡ Стандартный тариф</span>
              </small>
            </div>
            <div class="col-md-3">
              <button class="btn btn-primary w-100" type="submit">
                <span>➕ Добавить</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Список тарифов -->
    <div class="card shadow-sm border-0">
      <div class="card-header bg-white py-3">
        <h5 class="mb-0">💰 Список тарифов</h5>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center p-4">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="mt-2 text-muted">Загрузка тарифов...</p>
        </div>

        <div v-else-if="rates.length === 0" class="text-center p-5 text-muted">
          <div class="display-1 mb-3">💰</div>
          <h5>Тарифов пока нет</h5>
          <p>Добавьте первый тариф используя форму выше</p>
        </div>

        <div v-else class="row row-cols-1 row-cols-md-2 g-4">
          <div v-for="item in rates" :key="item.id" class="col">
            <div class="card h-100 shadow-sm border-0" 
                 :class="{
                   'border-warning': item.multiplier > 1,
                   'border-success': item.multiplier < 1,
                   'border-primary': item.multiplier === 1
                 }">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                  <div class="flex-grow-1">
                    <h6 class="card-title fw-bold mb-2">
                      <span :class="{
                        'text-danger': item.multiplier > 1,
                        'text-success': item.multiplier < 1,
                        'text-primary': item.multiplier === 1
                      }">
                        {{ item.name }}
                      </span>
                    </h6>
                    <div class="rate-info">
                      <div class="multiplier-badge mb-2">
                        <span class="badge" 
                              :class="{
                                'bg-danger': item.multiplier > 1,
                                'bg-success': item.multiplier < 1,
                                'bg-primary': item.multiplier === 1
                              }">
                          Коэффициент: {{ item.multiplier }}×
                        </span>
                      </div>
                      <small class="text-muted">
                        <span v-if="item.multiplier > 1">📈 Премиум тариф (+{{ ((item.multiplier - 1) * 100).toFixed(0) }}%)</span>
                        <span v-else-if="item.multiplier < 1">📉 Скидочный тариф ({{ ((1 - item.multiplier) * 100).toFixed(0) }}% скидка)</span>
                        <span v-else>⚡ Стандартный тариф</span>
                      </small>
                    </div>
                  </div>
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-warning" 
                            @click="onRateEditClick(item)" 
                            data-bs-toggle="modal" 
                            data-bs-target="#editRateModal">
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
    <div class="modal fade" id="editRateModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-warning text-dark">
            <h5 class="modal-title">✏️ Редактировать тариф</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Название тарифа</label>
              <input type="text" class="form-control" v-model="rateToEdit.name" />
            </div>
            <div class="mb-3">
              <label class="form-label">Коэффициент</label>
              <div class="input-group">
                <input type="number" step="0.1" min="0.1" class="form-control" v-model="rateToEdit.multiplier" />
                <span class="input-group-text">×</span>
              </div>
              <small class="form-text text-muted">
                <span v-if="rateToEdit.multiplier > 1" class="text-danger">📈 Премиум тариф</span>
                <span v-else-if="rateToEdit.multiplier < 1" class="text-success">📉 Скидочный тариф</span>
                <span v-else class="text-primary">⚡ Стандартный тариф</span>
              </small>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">❌ Отмена</button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateRate">
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

.multiplier-badge .badge {
  font-size: 0.75em;
  padding: 0.5em 0.75em;
  border-radius: 20px;
}

.btn-group-sm > .btn {
  border-radius: 8px;
  margin-left: 4px;
}

.rate-info {
  min-height: 60px;
}
</style>
[file content end]