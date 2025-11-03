[file name]: PassengersCrud.vue
[file content begin]
<script setup>
import axios from 'axios';
import { ref, onBeforeMount, computed } from 'vue';

const passengers = ref([]);
const passengerToAdd = ref({ full_name: '', passport: '', phone: '' });
const passengerToEdit = ref({});
const passengerPictureRef = ref();
const passengerAddImageUrl = ref();
const passengerEditPictureRef = ref();
const passengerEditImageUrl = ref();
const loading = ref(false);

// Статистика
const stats = ref({});

// Модальное окно изображения
const imageModalUrl = ref('');
const showImageModal = ref(false);

onBeforeMount(async () => {
  await fetchPassengers();
  await fetchStats();
});

async function fetchPassengers() {
  loading.value = true;
  const r = await axios.get('/api/passengers/');
  passengers.value = r.data;
  loading.value = false;
}

async function fetchStats() {
  const r = await axios.get("/api/passengers/stats/");
  stats.value = r.data;
}

// === ДОБАВЛЕНИЕ ПАССАЖИРА ===
function passengerAddPictureChange() {
  if (passengerPictureRef.value.files[0]) {
    passengerAddImageUrl.value = URL.createObjectURL(passengerPictureRef.value.files[0]);
  }
}

async function onPassengerAdd() {
  const formData = new FormData();

  if (passengerPictureRef.value.files[0]) {
    formData.append('picture', passengerPictureRef.value.files[0]);
  }

  formData.append('full_name', passengerToAdd.value.full_name);
  formData.append('passport', passengerToAdd.value.passport);
  formData.append('phone', passengerToAdd.value.phone);

  await axios.post("/api/passengers/", formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

  await fetchPassengers();
  await fetchStats();
  passengerToAdd.value = { full_name: '', passport: '', phone: '' };
  passengerPictureRef.value.value = '';
  passengerAddImageUrl.value = '';
}

// === УДАЛЕНИЕ ===
async function onRemoveClick(passenger) {
  if (confirm(`Удалить пассажира "${passenger.full_name}"?`)) {
    await axios.delete(`/api/passengers/${passenger.id}/`);
    await fetchPassengers();
    await fetchStats();
  }
}

// === РЕДАКТИРОВАНИЕ ===
function onPassengerEditClick(passenger) {
  passengerToEdit.value = { ...passenger };
  passengerEditImageUrl.value = passenger.picture || '';
  if (passengerEditPictureRef.value) passengerEditPictureRef.value.value = '';
}

function passengerEditPictureChange() {
  if (passengerEditPictureRef.value.files[0]) {
    passengerEditImageUrl.value = URL.createObjectURL(passengerEditPictureRef.value.files[0]);
  }
}

async function onUpdatePassenger() {
  const formData = new FormData();
  formData.append('full_name', passengerToEdit.value.full_name);
  formData.append('passport', passengerToEdit.value.passport);
  formData.append('phone', passengerToEdit.value.phone);

  if (passengerEditPictureRef.value.files[0]) {
    formData.append('picture', passengerEditPictureRef.value.files[0]);
  }

  await axios.put(`/api/passengers/${passengerToEdit.value.id}/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

  await fetchPassengers();
}

// === ПРОСМОТР ФОТО ===
function openImageModal(url) {
  imageModalUrl.value = url;
  showImageModal.value = true;
}

// Компьютед свойства
const passengersWithPhoto = computed(() => {
  return passengers.value.filter(p => p.picture).length;
});
</script>

<template>
  <div>
    <!-- Статистика -->
    <div class="alert alert-info mb-4">
      <div class="row text-center">
        <div class="col-md-3">
          <strong>👥 Всего пассажиров:</strong> {{ stats.count || 0 }}
        </div>
        <div class="col-md-3">
          <strong>📞 С телефоном:</strong> {{ stats.with_phone || 0 }}
        </div>
        <div class="col-md-3">
          <strong>🖼️ С фото:</strong> {{ stats.with_photo || 0 }}
        </div>
        <div class="col-md-3">
          <strong>📝 Без телефона:</strong> {{ stats.without_phone || 0 }}
        </div>
      </div>
    </div>

    <!-- Форма добавления -->
    <div class="card shadow-sm mb-4 border-0">
      <div class="card-header bg-primary text-white py-3">
        <h5 class="mb-0">➕ Добавить пассажира</h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="onPassengerAdd">
          <div class="row g-3 align-items-end">
            <div class="col-md-3">
              <label class="form-label">ФИО</label>
              <input type="text" class="form-control" v-model="passengerToAdd.full_name" 
                     placeholder="Полное имя" required />
            </div>
            <div class="col-md-2">
              <label class="form-label">Паспорт</label>
              <input type="text" class="form-control" v-model="passengerToAdd.passport" 
                     placeholder="Номер паспорта" required />
            </div>
            <div class="col-md-2">
              <label class="form-label">Телефон</label>
              <input type="text" class="form-control" v-model="passengerToAdd.phone" 
                     placeholder="Номер телефона" />
            </div>
            <div class="col-md-2">
              <label class="form-label">Фото</label>
              <input class="form-control" type="file" ref="passengerPictureRef" 
                     @change="passengerAddPictureChange" accept="image/*">
            </div>
            <div class="col-md-2">
              <div v-if="passengerAddImageUrl" class="text-center">
                <img :src="passengerAddImageUrl" class="img-thumbnail" style="max-height: 60px;">
                <small class="text-muted d-block">Предпросмотр</small>
              </div>
            </div>
            <div class="col-md-1">
              <button class="btn btn-primary w-100" type="submit">
                <span>➕</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Список пассажиров -->
    <div class="card shadow-sm border-0">
      <div class="card-header bg-white py-3">
        <h5 class="mb-0">👥 Список пассажиров</h5>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center p-4">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="mt-2 text-muted">Загрузка пассажиров...</p>
        </div>

        <div v-else-if="passengers.length === 0" class="text-center p-5 text-muted">
          <div class="display-1 mb-3">👥</div>
          <h5>Пассажиров пока нет</h5>
          <p>Добавьте первого пассажира используя форму выше</p>
        </div>

        <div v-else class="row row-cols-1 row-cols-md-2 g-4">
          <div v-for="item in passengers" :key="item.id" class="col">
            <div class="card h-100 shadow-sm border-0">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                  <div class="flex-grow-1">
                    <h6 class="card-title fw-bold text-primary mb-2">{{ item.full_name }}</h6>
                    <div class="passenger-info small text-muted mb-2">
                      <div>📋 Паспорт: {{ item.passport }}</div>
                      <div>📞 Телефон: {{ item.phone || 'не указан' }}</div>
                    </div>
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
                        <span class="text-warning">🖼️ Фото не загружено</span>
                      </div>
                    </div>
                  </div>
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-warning" 
                            @click="onPassengerEditClick(item)" 
                            data-bs-toggle="modal" 
                            data-bs-target="#editPassengerModal">
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
    <div class="modal fade" id="editPassengerModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-warning text-dark">
            <h5 class="modal-title">✏️ Редактировать пассажира</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">ФИО</label>
              <input type="text" class="form-control" v-model="passengerToEdit.full_name" />
            </div>
            <div class="mb-3">
              <label class="form-label">Паспорт</label>
              <input type="text" class="form-control" v-model="passengerToEdit.passport" />
            </div>
            <div class="mb-3">
              <label class="form-label">Телефон</label>
              <input type="text" class="form-control" v-model="passengerToEdit.phone" />
            </div>

            <div class="mb-3">
              <label class="form-label">Изменить фото</label>
              <input class="form-control" type="file" ref="passengerEditPictureRef" 
                     @change="passengerEditPictureChange" accept="image/*">
            </div>

            <div v-if="passengerEditImageUrl" class="text-center p-3 border rounded">
              <p class="text-muted small mb-2">Предпросмотр фото:</p>
              <img :src="passengerEditImageUrl" class="img-fluid rounded" style="max-height: 120px;">
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">❌ Отмена</button>
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdatePassenger">
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

.passenger-info div {
  margin-bottom: 2px;
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