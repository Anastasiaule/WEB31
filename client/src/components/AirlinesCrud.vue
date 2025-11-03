[file name]: AirlinesCrud.vue
[file content begin]
<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { ref, onBeforeMount, computed } from 'vue';

const airlines = ref([]);
const airlineToAdd = ref({ name: '' });
const airlineToEdit = ref({});
const airlinePictureRef = ref();
const airlineAddImageUrl = ref();
const airlineEditPictureRef = ref();
const airlineEditImageUrl = ref();
const loading = ref(false);

// Статистика
const stats = ref({});

// Модальное окно изображения
const imageModalUrl = ref('');
const showImageModal = ref(false);

onBeforeMount(async () => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
  await fetchAirlines();
  await fetchStats();
});

async function fetchAirlines() {
  loading.value = true;
  const r = await axios.get('/api/airlines/');
  airlines.value = r.data;
  loading.value = false;
}

async function fetchStats() {
  const r = await axios.get("/api/airlines/stats/");
  stats.value = r.data;
}

// === ДОБАВЛЕНИЕ ===
function airlineAddPictureChange() {
  if (airlinePictureRef.value.files[0]) {
    airlineAddImageUrl.value = URL.createObjectURL(airlinePictureRef.value.files[0]);
  }
}

async function onAirlineAdd() {
  const formData = new FormData();
  
  if (airlinePictureRef.value.files[0]) {
    formData.append('picture', airlinePictureRef.value.files[0]);
  }
  formData.append('name', airlineToAdd.value.name);

  await axios.post("/api/airlines/", formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  
  await fetchAirlines();
  await fetchStats();
  airlineToAdd.value.name = '';
  airlinePictureRef.value.value = '';
  airlineAddImageUrl.value = '';
}

// === УДАЛЕНИЕ ===
async function onRemoveClick(airline) {
  if (confirm(`Удалить авиакомпанию "${airline.name}"?`)) {
    await axios.delete(`/api/airlines/${airline.id}/`);
    await fetchAirlines();
    await fetchStats();
  }
}

// === РЕДАКТИРОВАНИЕ ===
function onAirlineEditClick(airline) {
  airlineToEdit.value = { ...airline };
  airlineEditImageUrl.value = airline.picture || '';
  if (airlineEditPictureRef.value) airlineEditPictureRef.value.value = '';
}

function airlineEditPictureChange() {
  if (airlineEditPictureRef.value.files[0]) {
    airlineEditImageUrl.value = URL.createObjectURL(airlineEditPictureRef.value.files[0]);
  }
}

async function onUpdateAirline() {
  const formData = new FormData();
  formData.append('name', airlineToEdit.value.name);

  if (airlineEditPictureRef.value.files[0]) {
    formData.append('picture', airlineEditPictureRef.value.files[0]);
  }

  await axios.put(`/api/airlines/${airlineToEdit.value.id}/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

  await fetchAirlines();
}

// === ПРОСМОТР ИЗОБРАЖЕНИЯ ===
function openImageModal(url) {
  imageModalUrl.value = url;
  showImageModal.value = true;
}

// Компьютед свойства для дополнительной статистики
const airlinesWithLogo = computed(() => {
  return airlines.value.filter(a => a.picture).length;
});
</script>

<template>
  <div>
    <!-- Статистика -->
    <div class="alert alert-info mb-4">
      <div class="row text-center">
        <div class="col-md-3">
          <strong>🏢 Всего:</strong> {{ stats.count || 0 }}
        </div>
        <div class="col-md-3">
          <strong>🖼️ С логотипом:</strong> {{ airlinesWithLogo }}
        </div>
        <div class="col-md-3">
          <strong>📊 Без логотипа:</strong> {{ stats.count - airlinesWithLogo }}
        </div>
        <div class="col-md-3">
          <strong>🎯 Активных:</strong> {{ stats.count || 0 }}
        </div>
      </div>
    </div>

    <!-- Форма добавления -->
    <div class="card shadow-sm mb-4 border-0">
      <div class="card-header bg-primary text-white py-3">
        <h5 class="mb-0">➕ Добавить авиакомпанию</h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="onAirlineAdd">
          <div class="row g-3 align-items-end">
            <div class="col-md-4">
              <label class="form-label">Название авиакомпании</label>
              <input type="text" class="form-control" v-model="airlineToAdd.name" 
                     placeholder="Введите название" required />
            </div>
            <div class="col-md-3">
              <label class="form-label">Логотип</label>
              <input class="form-control" type="file" ref="airlinePictureRef" 
                     @change="airlineAddPictureChange" accept="image/*">
            </div>
            <div class="col-md-2">
              <div v-if="airlineAddImageUrl" class="text-center">
                <img :src="airlineAddImageUrl" class="img-thumbnail" style="max-height: 60px;">
                <small class="text-muted d-block">Предпросмотр</small>
              </div>
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

    <!-- Список авиакомпаний -->
    <div class="card shadow-sm border-0">
      <div class="card-header bg-white py-3">
        <h5 class="mb-0">🏢 Список авиакомпаний</h5>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center p-4">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="mt-2 text-muted">Загрузка авиакомпаний...</p>
        </div>

        <div v-else-if="airlines.length === 0" class="text-center p-5 text-muted">
          <div class="display-1 mb-3">🏢</div>
          <h5>Авиакомпаний пока нет</h5>
          <p>Добавьте первую авиакомпанию используя форму выше</p>
        </div>

        <div v-else class="row row-cols-1 row-cols-md-2 g-4">
          <div v-for="item in airlines" :key="item.id" class="col">
            <div class="card h-100 shadow-sm border-0">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                  <div class="flex-grow-1">
                    <h6 class="card-title fw-bold text-primary mb-2">{{ item.name }}</h6>
                    <div class="d-flex align-items-center">
                      <div v-if="item.picture" class="me-3">
                        <img 
                          :src="item.picture" 
                          class="img-thumbnail rounded"
                          style="max-height: 60px; cursor: zoom-in;" 
                          @click="openImageModal(item.picture)"
                        >
                      </div>
                      <div v-else class="text-muted small">
                        <span class="text-warning">🖼️ Логотип не загружен</span>
                      </div>
                    </div>
                  </div>
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-warning" 
                            @click="onAirlineEditClick(item)" 
                            data-bs-toggle="modal" 
                            data-bs-target="#editAirlineModal">
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
    <div class="modal fade" id="editAirlineModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-warning text-dark">
            <h5 class="modal-title">✏️ Редактировать авиакомпанию</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Название авиакомпании</label>
              <input type="text" class="form-control" v-model="airlineToEdit.name" />
            </div>
            
            <div class="mb-3">
              <label class="form-label">Изменить логотип</label>
              <input class="form-control" type="file" ref="airlineEditPictureRef" 
                     @change="airlineEditPictureChange" accept="image/*">
            </div>

            <div v-if="airlineEditImageUrl" class="text-center p-3 border rounded">
              <p class="text-muted small mb-2">Предпросмотр логотипа:</p>
              <img :src="airlineEditImageUrl" class="img-fluid rounded" style="max-height: 120px;">
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">❌ Отмена</button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateAirline">
              💾 Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно просмотра изображения -->
    <div v-if="showImageModal" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.9);">
      <div class="d-flex justify-content-center align-items-center vh-100">
        <img :src="imageModalUrl" class="img-fluid rounded shadow-lg" style="max-height: 90vh;">
      </div>
      <button class="btn btn-light position-fixed top-0 end-0 m-3 rounded-circle" 
              @click="showImageModal = false" style="width: 50px; height: 50px;">
        ✖
      </button>
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

.btn-group-sm > .btn {
  border-radius: 8px;
  margin-left: 4px;
}

.img-thumbnail {
  border-radius: 8px;
  transition: transform 0.2s ease;
}

.img-thumbnail:hover {
  transform: scale(1.05);
}
</style>
[file content end]