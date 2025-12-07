<script setup>
import axios from "axios";
import { ref, onMounted, computed } from "vue";

const airlines = ref([]);
const stats = ref({});
const loading = ref(true);

const user = ref({
  is_superuser: false,
  is_authenticated: false,
});

const newAirlineName = ref("");
const newAirlineFile = ref(null);
const newPreview = ref("");
const editAirline = ref({});
const editFile = ref(null);
const editPreview = ref("");
const modalImage = ref("");
const showImage = ref(false);

const showFilters = ref(false);
const filters = ref({
  name: "",
  hasLogo: ""
});

onMounted(async () => {
  await loadUser();
  await loadAirlines();
  await loadStats();
});

async function loadUser() {
  try {
    const r = await axios.get("/api/user/info/");
    user.value = r.data;
  } catch {
    user.value = { is_superuser: false, is_authenticated: false };
  }
}

async function loadAirlines() {
  loading.value = true;
  const r = await axios.get("/api/airlines/");
  airlines.value = r.data;
  loading.value = false;
}

async function loadStats() {
  const r = await axios.get("/api/airlines/stats/");
  stats.value = r.data;
}

function handleAddFile(e) {
  const file = e.target.files[0];
  newAirlineFile.value = file;
  newPreview.value = file ? URL.createObjectURL(file) : "";
}

async function addAirline() {
  const fd = new FormData();
  fd.append("name", newAirlineName.value);
  if (newAirlineFile.value) fd.append("picture", newAirlineFile.value);

  await axios.post("/api/airlines/", fd);
  newAirlineName.value = "";
  newAirlineFile.value = null;
  newPreview.value = "";
  await loadAirlines();
  await loadStats();
}

async function removeAirline(a) {
  if (!confirm(`Удалить "${a.name}"?`)) return;
  await axios.delete(`/api/airlines/${a.id}/`);
  await loadAirlines();
  await loadStats();
}

function startEdit(a) {
  editAirline.value = { ...a };
  editPreview.value = a.picture;
  editFile.value = null;
}

function handleEditFile(e) {
  const file = e.target.files[0];
  editFile.value = file;
  editPreview.value = file ? URL.createObjectURL(file) : editAirline.value.picture;
}

async function saveEdit() {
  const fd = new FormData();
  fd.append("name", editAirline.value.name);
  if (editFile.value) fd.append("picture", editFile.value);

  await axios.put(`/api/airlines/${editAirline.value.id}/`, fd);
  await loadAirlines();
}

function openImage(url) {
  modalImage.value = url;
  showImage.value = true;
}

// Фильтрация
const filteredAirlines = computed(() => {
  return airlines.value.filter(a => {
    if (filters.value.name && !a.name.toLowerCase().includes(filters.value.name.toLowerCase())) return false
    
    if (filters.value.hasLogo === "yes" && !a.picture) return false
    if (filters.value.hasLogo === "no" && a.picture) return false
    
    return true
  })
})

function clearFilters() {
  filters.value = {
    name: "",
    hasLogo: ""
  }
}
</script>
<template>
<div class="container py-4">
  <!-- Статистика -->
  <div class="stats-card mb-4">
    <h5 class="mb-3">Статистика авиакомпаний</h5>
    <div class="row text-center">
      <div class="col"><span class="stats-label">Всего:</span> <span class="stats-value">{{ stats.count || 0 }}</span></div>
      <div class="col"><span class="stats-label">С лого:</span> <span class="stats-value">{{ airlines.filter(a => a.picture).length }}</span></div>
      <div class="col"><span class="stats-label">Без лого:</span> <span class="stats-value">{{ (stats.count || 0) - airlines.filter(a => a.picture).length }}</span></div>
      <div class="col"><span class="stats-label">Отфильтровано:</span> <span class="stats-value">{{ filteredAirlines.length }}</span></div>
    </div>
  </div>

  <!-- Форма добавления для админа -->
  <div v-if="user.is_superuser" class="card mb-4">
    <div class="card-header bg-light">
      <h5 class="mb-0">Добавить авиакомпанию</h5>
    </div>
    <div class="card-body">
      <div class="row g-3">
        <div class="col-md-6">
          <input v-model="newAirlineName" class="form-control form-control-sm" placeholder="Название компании">
        </div>
        <div class="col-md-4">
          <input type="file" class="form-control form-control-sm" accept="image/*" @change="handleAddFile">
        </div>
        <div class="col-md-2">
          <button class="btn btn-primary btn-sm w-100" @click="addAirline">Добавить</button>
        </div>
      </div>
      <div v-if="newPreview" class="mt-3">
        <img :src="newPreview" class="img-thumbnail" style="max-height: 60px;">
      </div>
    </div>
  </div>

  <!-- Список авиакомпаний -->
  <div class="card">
    <div class="card-header bg-light d-flex justify-content-between align-items-center">
      <h5 class="mb-0">Список авиакомпаний</h5>
      <button class="btn btn-sm btn-outline-secondary" @click="showFilters = !showFilters">
        Фильтры
      </button>
    </div>
    
    <!-- Фильтры -->
    <div v-if="showFilters" class="card-body border-bottom">
      <div class="row g-2 mb-2">
        <div class="col-md-5">
          <input v-model="filters.name" class="form-control form-control-sm" placeholder="Название">
        </div>
        <div class="col-md-4">
          <select v-model="filters.hasLogo" class="form-select form-select-sm">
            <option value="">Все</option>
            <option value="yes">С логотипом</option>
            <option value="no">Без логотипа</option>
          </select>
        </div>
        <div class="col-md-3">
          <button class="btn btn-sm btn-outline-danger w-100" @click="clearFilters">×</button>
        </div>
      </div>
    </div>
    
    <div class="card-body">
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border spinner-border-sm text-primary"></div>
        <p class="mt-2 text-muted">Загрузка...</p>
      </div>
      
      <div v-else-if="filteredAirlines.length === 0" class="text-center text-muted py-4">
        Нет авиакомпаний
      </div>
      
      <div v-else class="row row-cols-1 row-cols-md-2 g-3">
        <div class="col" v-for="a in filteredAirlines" :key="a.id">
          <div class="card h-100">
            <div class="card-body d-flex align-items-center">
              <div class="flex-grow-1">
                <h6 class="card-title mb-1"><strong>{{ a.name }}</strong></h6>
                <div v-if="a.picture" class="mt-2">
                  <img :src="a.picture" @click="openImage(a.picture)" 
                       class="img-thumbnail" style="max-height: 50px; cursor: pointer;">
                </div>
                <small v-else class="text-muted">Нет логотипа</small>
              </div>
              
              <div v-if="user.is_superuser" class="btn-group btn-group-sm ms-3">
                <button class="btn btn-outline-warning" data-bs-toggle="modal" data-bs-target="#editModal" @click="startEdit(a)">Изменить</button>
                <button class="btn btn-outline-danger" @click="removeAirline(a)">Удалить</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- модалка редактирования -->
  <div class="modal fade" id="editModal">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать авиакомпанию</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label class="form-label">Название</label>
            <input v-model="editAirline.name" class="form-control">
          </div>
          <div class="mb-3">
            <label class="form-label">Логотип</label>
            <input type="file" class="form-control" accept="image/*" @change="handleEditFile">
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

  <!-- модалка изображения -->
  <div v-if="showImage" class="modal fade show d-block" style="background: rgba(0,0,0,0.8)">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-body text-center">
          <img :src="modalImage" class="img-fluid">
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

.card {
  border: 1px solid #dee2e6;
  border-radius: 8px;
}

.card-title {
  font-size: 1rem;
}

.img-thumbnail {
  border-radius: 6px;
  border: 1px solid #dee2e6;
}
</style>