<script setup>
import axios from "axios";
import { ref, onBeforeMount } from "vue";

const passengers = ref([]);
const loading = ref(false);

const stats = ref({});
const showImage = ref(false);
const imageUrl = ref("");

const newPassenger = ref({
  full_name: "",
  passport: "",
  phone: ""
});

const editPassenger = ref({});
const addFile = ref(null);
const editFile = ref(null);
const addPreview = ref("");
const editPreview = ref("");

onBeforeMount(() => {
  fetchPassengers();
  fetchStats();
});

async function fetchPassengers() {
  loading.value = true;
  const r = await axios.get("/api/passengers/");
  passengers.value = r.data;
  loading.value = false;
}

async function fetchStats() {
  const r = await axios.get("/api/passengers/stats/");
  stats.value = r.data;
}

function onAddFileChange() {
  if (addFile.value.files[0]) {
    addPreview.value = URL.createObjectURL(addFile.value.files[0]);
  }
}

async function addPassenger() {
  const fd = new FormData();
  fd.append("full_name", newPassenger.value.full_name);
  fd.append("passport", newPassenger.value.passport);
  fd.append("phone", newPassenger.value.phone);

  if (addFile.value.files[0]) {
    fd.append("picture", addFile.value.files[0]);
  }

  await axios.post("/api/passengers/", fd);
  await fetchPassengers();
  await fetchStats();

  newPassenger.value = { full_name: "", passport: "", phone: "" };
  addFile.value.value = "";
  addPreview.value = "";
}

function startEdit(p) {
  editPassenger.value = { ...p };
  editPreview.value = p.picture || "";
  if (editFile.value) editFile.value.value = "";
}

function onEditFileChange() {
  if (editFile.value.files[0]) {
    editPreview.value = URL.createObjectURL(editFile.value.files[0]);
  }
}

async function saveEdit() {
  const fd = new FormData();
  fd.append("full_name", editPassenger.value.full_name);
  fd.append("passport", editPassenger.value.passport);
  fd.append("phone", editPassenger.value.phone);

  if (editFile.value.files[0]) {
    fd.append("picture", editFile.value.files[0]);
  }

  await axios.put(`/api/passengers/${editPassenger.value.id}/`, fd);
  await fetchPassengers();
}

async function removePassenger(p) {
  if (confirm(`Удалить пассажира "${p.full_name}"?`)) {
    await axios.delete(`/api/passengers/${p.id}/`);
    await fetchPassengers();
    await fetchStats();
  }
}

function openImage(url) {
  imageUrl.value = url;
  showImage.value = true;
}
</script>
<template>
<div class="container py-4">
  <!-- Статистика -->
  <div class="stats-card mb-4">
    <h5 class="mb-3">Статистика пассажиров</h5>
    <div class="row text-center">
      <div class="col"><span class="stats-label">Всего:</span> <span class="stats-value">{{ stats.count || 0 }}</span></div>
      <div class="col"><span class="stats-label">С телефоном:</span> <span class="stats-value">{{ stats.with_phone || 0 }}</span></div>
      <div class="col"><span class="stats-label">С фото:</span> <span class="stats-value">{{ stats.with_photo || 0 }}</span></div>
      <div class="col"><span class="stats-label">Без телефона:</span> <span class="stats-value">{{ stats.without_phone || 0 }}</span></div>
    </div>
  </div>

  <!-- Форма добавления -->
  <div class="card mb-4">
    <div class="card-header bg-light">
      <h5 class="mb-0">Добавить пассажира</h5>
    </div>
    <div class="card-body">
      <div class="row g-3">
        <div class="col-md-4">
          <input v-model="newPassenger.full_name" class="form-control form-control-sm" placeholder="ФИО" required>
        </div>
        <div class="col-md-3">
          <input v-model="newPassenger.passport" class="form-control form-control-sm" placeholder="Паспорт" required>
        </div>
        <div class="col-md-3">
          <input v-model="newPassenger.phone" class="form-control form-control-sm" placeholder="Телефон">
        </div>
        <div class="col-md-2">
          <input type="file" class="form-control form-control-sm" ref="addFile" @change="onAddFileChange">
        </div>
        <div v-if="addPreview" class="col-12">
          <img :src="addPreview" class="img-thumbnail" style="max-height:70px">
        </div>
        <div class="col-12">
          <button class="btn btn-primary btn-sm" @click="addPassenger">Добавить</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Список пассажиров -->
  <div class="card">
    <div class="card-header bg-light">
      <h5 class="mb-0">Список пассажиров</h5>
    </div>
    <div class="card-body">
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border spinner-border-sm text-primary"></div>
        <p class="mt-2 text-muted">Загрузка...</p>
      </div>
      
      <div v-else-if="passengers.length === 0" class="text-center text-muted py-4">
        Пассажиров нет
      </div>
      
      <div v-else class="list-group list-group-flush">
        <div v-for="p in passengers" :key="p.id" class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
              <div v-if="p.picture" class="me-3">
                <img :src="p.picture" @click="openImage(p.picture)" 
                     class="img-thumbnail passenger-photo" style="cursor: pointer;">
              </div>
              <div>
                <h6 class="mb-1"><strong>{{ p.full_name }}</strong></h6>
                <small class="text-muted">Паспорт: {{ p.passport }}</small><br>
                <small class="text-muted">Телефон: {{ p.phone || '—' }}</small>
              </div>
            </div>
            
            <div class="btn-group btn-group-sm">
              <button class="btn btn-outline-warning" data-bs-toggle="modal" data-bs-target="#editModal" 
                      @click="startEdit(p)">Изменить</button>
              <button class="btn btn-outline-danger" @click="removePassenger(p)">Удалить</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Модальное окно редактирования -->
  <div class="modal fade" id="editModal">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать пассажира</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label class="form-label">ФИО</label>
            <input v-model="editPassenger.full_name" class="form-control">
          </div>
          <div class="mb-3">
            <label class="form-label">Паспорт</label>
            <input v-model="editPassenger.passport" class="form-control">
          </div>
          <div class="mb-3">
            <label class="form-label">Телефон</label>
            <input v-model="editPassenger.phone" class="form-control">
          </div>
          <div class="mb-3">
            <label class="form-label">Фото</label>
            <input type="file" class="form-control" ref="editFile" @change="onEditFileChange">
          </div>
          <div v-if="editPreview" class="mt-3">
            <img :src="editPreview" class="img-thumbnail" style="max-height: 100px;">
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="saveEdit">Сохранить</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Модальное окно просмотра фото -->
  <div v-if="showImage" class="modal fade show d-block" style="background: rgba(0,0,0,0.8)">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-body text-center p-0">
          <img :src="imageUrl" class="img-fluid rounded">
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="showImage = false">Закрыть</button>
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

.list-group-item {
  border: 1px solid #dee2e6;
  border-radius: 6px;
  margin-bottom: 8px;
  padding: 12px 15px;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

.passenger-photo {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 50%;
}

.img-thumbnail {
  border-radius: 6px;
  border: 1px solid #dee2e6;
}
</style>