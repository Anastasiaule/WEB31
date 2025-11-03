<script setup>
import axios from 'axios';
import { ref, onBeforeMount } from 'vue';

const passengers = ref([]);
const passengerToAdd = ref({ full_name: '', passport: '', phone: '' });
const passengerToEdit = ref({});

const passengerPictureRef = ref();
const passengerAddImageUrl = ref();

const passengerEditPictureRef = ref();
const passengerEditImageUrl = ref();

// Для просмотра фото
const imageModalUrl = ref('');
const showImageModal = ref(false);

onBeforeMount(() => {
  fetchPassengers();
});

async function fetchPassengers() {
  const r = await axios.get('/api/passengers/');
  passengers.value = r.data;
}

// === Добавление пассажира ===
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
  passengerToAdd.value = { full_name: '', passport: '', phone: '' };
  passengerPictureRef.value.value = '';
  passengerAddImageUrl.value = '';
}

// === Удаление ===
async function onRemoveClick(passenger) {
  await axios.delete(`/api/passengers/${passenger.id}/`);
  await fetchPassengers();
}

// === Редактирование ===
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

// === Просмотр фото ===
function openImageModal(url) {
  imageModalUrl.value = url;
  showImageModal.value = true;
}
</script>

<template>
  <!-- === Форма добавления === -->
  <form @submit.prevent="onPassengerAdd" class="mb-4 p-3 border rounded">
    <div class="row g-2 align-items-end">
      <div class="col-md-3">
        <label class="form-label">ФИО</label>
        <input type="text" class="form-control" v-model="passengerToAdd.full_name" placeholder="ФИО" required />
      </div>
      <div class="col-md-2">
        <label class="form-label">Паспорт</label>
        <input type="text" class="form-control" v-model="passengerToAdd.passport" placeholder="Паспорт" required />
      </div>
      <div class="col-md-2">
        <label class="form-label">Телефон</label>
        <input type="text" class="form-control" v-model="passengerToAdd.phone" placeholder="Телефон" />
      </div>
      <div class="col-md-2">
        <label class="form-label">Фото</label>
        <input class="form-control" type="file" ref="passengerPictureRef" @change="passengerAddPictureChange">
      </div>
      <div class="col-md-1">
        <img v-if="passengerAddImageUrl" :src="passengerAddImageUrl" style="max-height: 60px;">
      </div>
      <div class="col-md-2">
        <button class="btn btn-primary w-100" type="submit">Добавить</button>
      </div>
    </div>
  </form>

  <!-- === Список пассажиров === -->
  <div class="list-group">
    <div v-for="item in passengers" :key="item.id" class="list-group-item">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <strong>{{ item.full_name }}</strong><br>
          <small class="text-muted">Паспорт: {{ item.passport }} • Тел: {{ item.phone || 'не указан' }}</small>
        </div>
        <div class="d-flex align-items-center">
          <div v-if="item.picture" class="me-3">
            <img 
              :src="item.picture" 
              style="max-height: 60px; cursor: zoom-in;"
              @click="openImageModal(item.picture)"
            >
          </div>
          <div>
            <button class="btn btn-warning btn-sm me-2" 
                    @click="onPassengerEditClick(item)" 
                    data-bs-toggle="modal" 
                    data-bs-target="#editPassengerModal">
              ✏️
            </button>
            <button class="btn btn-danger btn-sm" @click="onRemoveClick(item)">🗑️</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- === Модальное окно редактирования === -->
  <div class="modal fade" id="editPassengerModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать пассажира</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label>ФИО</label>
            <input type="text" class="form-control" v-model="passengerToEdit.full_name" />
          </div>
          <div class="mb-3">
            <label>Паспорт</label>
            <input type="text" class="form-control" v-model="passengerToEdit.passport" />
          </div>
          <div class="mb-3">
            <label>Телефон</label>
            <input type="text" class="form-control" v-model="passengerToEdit.phone" />
          </div>

          <div class="mb-3">
            <label>Изменить фото</label>
            <input class="form-control" type="file" ref="passengerEditPictureRef" @change="passengerEditPictureChange">
          </div>

          <div v-if="passengerEditImageUrl" class="text-center">
            <img :src="passengerEditImageUrl" style="max-height: 100px;">
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdatePassenger">Сохранить</button>
        </div>
      </div>
    </div>
  </div>


  <div v-if="showImageModal" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.8);">
    <div class="d-flex justify-content-center align-items-center vh-100">
      <img :src="imageModalUrl" class="img-fluid rounded shadow-lg" style="max-height: 90vh;">
    </div>
    <button class="btn btn-light position-fixed top-0 end-0 m-3" @click="showImageModal = false">✖</button>
  </div>
</template>
