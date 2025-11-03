<script setup>
import axios from 'axios';
import { ref, onBeforeMount } from 'vue';

const rates = ref([]);
const rateToAdd = ref({ name: '', multiplier: 1.0 });
const rateToEdit = ref({});

onBeforeMount(() => {
  fetchRates();
})

async function fetchRates() {
  const r = await axios.get('/api/rates/');
  rates.value = r.data;
}

async function onRateAdd() {
  await axios.post("/api/rates/", rateToAdd.value);
  await fetchRates();
  rateToAdd.value = { name: '', multiplier: 1.0 };
}

async function onRemoveClick(rate) {
  await axios.delete(`/api/rates/${rate.id}/`);
  await fetchRates();
}

async function onRateEditClick(rate) {
  rateToEdit.value = { ...rate };
}

async function onUpdateRate() {
  await axios.put(`/api/rates/${rateToEdit.value.id}/`, rateToEdit.value);
  await fetchRates();
}
</script>

<template>
  <form @submit.prevent="onRateAdd" class="mb-4 p-3 border rounded">
    <div class="row g-2">
      <div class="col-md-5">
        <input type="text" class="form-control" v-model="rateToAdd.name" placeholder="Название тарифа" required />
      </div>
      <div class="col-md-4">
        <input type="number" step="0.1" class="form-control" v-model="rateToAdd.multiplier" placeholder="Коэффициент" required />
      </div>
      <div class="col-md-3">
        <button class="btn btn-primary w-100" type="submit">Добавить</button>
      </div>
    </div>
  </form>

  <div class="list-group">
    <div v-for="item in rates" :key="item.id" class="list-group-item">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <strong>{{ item.name }}</strong><br>
          <small class="text-muted">Коэффициент: {{ item.multiplier }}x</small>
        </div>
        <div>
          <button class="btn btn-warning btn-sm me-2" @click="onRateEditClick(item)" data-bs-toggle="modal" data-bs-target="#editRateModal">
            ✏️
          </button>
          <button class="btn btn-danger btn-sm" @click="onRemoveClick(item)">🗑️</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Модальное окно редактирования тарифа -->
  <div class="modal fade" id="editRateModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать тариф</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label>Название тарифа</label>
            <input type="text" class="form-control" v-model="rateToEdit.name" />
          </div>
          <div class="mb-3">
            <label>Коэффициент</label>
            <input type="number" step="0.1" class="form-control" v-model="rateToEdit.multiplier" />
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateRate">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>