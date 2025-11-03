<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { ref, onBeforeMount } from 'vue';

const airlines = ref([]);
const airlineToAdd = ref({ name: '' });
const airlineToEdit = ref({});
const airlinePictureRef = ref();
const airlineAddImageUrl = ref();


// Для модального просмотра изображения
const imageModalUrl = ref('');
const showImageModal = ref(false);

const airlineEditPictureRef = ref();
const airlineEditImageUrl = ref();

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
  fetchAirlines();
});

async function fetchAirlines() {
  const r = await axios.get('/api/airlines/');
  airlines.value = r.data;
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
  airlineToAdd.value.name = '';
  airlinePictureRef.value.value = '';
  airlineAddImageUrl.value = '';
}

// === УДАЛЕНИЕ ===
async function onRemoveClick(airline) {
  await axios.delete(`/api/airlines/${airline.id}/`);
  await fetchAirlines();
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
</script>

<template>


  <!-- === ДОБАВЛЕНИЕ === -->
  <form @submit.prevent="onAirlineAdd">
    <div class="row mb-3">
      <div class="col">
        <input type="text" class="form-control" v-model="airlineToAdd.name" placeholder="Название авиакомпании" required />
      </div>
      <div class="col-auto">
        <input class="form-control" type="file" ref="airlinePictureRef" @change="airlineAddPictureChange">
      </div>
      <div class="col-auto">
        <img v-if="airlineAddImageUrl" :src="airlineAddImageUrl" style="max-height: 60px;">
      </div>
      <div class="col-auto">
        <button class="btn btn-primary" type="submit">Добавить</button>
      </div>
    </div>
  </form>

  <!-- === СПИСОК === -->
  <div class="list-group">
    <div v-for="item in airlines" :key="item.id" class="list-group-item d-flex justify-content-between align-items-center">
      <span>{{ item.name }}</span>
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
                  @click="onAirlineEditClick(item)" 
                  data-bs-toggle="modal" 
                  data-bs-target="#editAirlineModal">
            ✏️
          </button>
          <button class="btn btn-danger btn-sm" @click="onRemoveClick(item)">🗑️</button>
        </div>
      </div>
    </div>
  </div>

  <!-- === МОДАЛКА РЕДАКТИРОВАНИЯ === -->
  <div class="modal fade" id="editAirlineModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать авиакомпанию</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input type="text" class="form-control mb-3" v-model="airlineToEdit.name" />
          
          <label>Изменить картинку:</label>
          <input class="form-control" type="file" ref="airlineEditPictureRef" @change="airlineEditPictureChange">

          <div v-if="airlineEditImageUrl" class="mt-2 text-center">
            <img :src="airlineEditImageUrl" style="max-height: 100px;">
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="onUpdateAirline">Сохранить</button>
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
