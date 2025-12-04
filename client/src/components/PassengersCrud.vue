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
  <div class="container py-3">

    <!-- Статистика -->
    <div class="alert alert-info text-center mb-4">
      👥 Всего: <b>{{ stats.count || 0 }}</b> •
      📞 С телефоном: <b>{{ stats.with_phone || 0 }}</b> •
      🖼️ С фото: <b>{{ stats.with_photo || 0 }}</b> •
      📝 Без телефона: <b>{{ stats.without_phone || 0 }}</b>
    </div>

    <!-- Добавление -->
    <div class="card mb-4">
      <div class="card-header">Добавить пассажира</div>
      <div class="card-body">
        <form @submit.prevent="addPassenger">

          <input v-model="newPassenger.full_name" class="form-control mb-2" placeholder="ФИО" required>
          <input v-model="newPassenger.passport" class="form-control mb-2" placeholder="Паспорт" required>
          <input v-model="newPassenger.phone" class="form-control mb-2" placeholder="Телефон">

          <input type="file" class="form-control mb-2" ref="addFile" @change="onAddFileChange">

          <img v-if="addPreview" :src="addPreview" class="img-thumbnail mb-2" style="max-height:70px">

          <button class="btn btn-primary w-100">Добавить</button>
        </form>
      </div>
    </div>

    <!-- Список -->
    <div class="card">
      <div class="card-header">Пассажиры</div>

      <div class="card-body">

        <div v-if="loading" class="text-center py-3">
          Загрузка...
        </div>

        <div v-else-if="passengers.length === 0" class="text-center text-muted py-4">
          Пассажиров нет
        </div>

        <div v-else class="list-group">
          <div
            v-for="p in passengers"
            :key="p.id"
            class="list-group-item d-flex justify-content-between align-items-center"
          >

            <div>
              <b>{{ p.full_name }}</b><br>
              <small class="text-muted">Паспорт: {{ p.passport }}</small><br>
              <small class="text-muted">Телефон: {{ p.phone || '—' }}</small>

              <div class="mt-2" v-if="p.picture">
                <img
                  :src="p.picture"
                  class="img-thumbnail"
                  style="max-height:60px; cursor:pointer"
                  @click="openImage(p.picture)"
                >
              </div>
            </div>

            <div>
              <button class="btn btn-sm btn-warning me-2"
                      data-bs-toggle="modal"
                      data-bs-target="#editModal"
                      @click="startEdit(p)">
                ✏️
              </button>

              <button class="btn btn-sm btn-danger" @click="removePassenger(p)">
                🗑️
              </button>
            </div>

          </div>
        </div>

      </div>
    </div>

    <!-- Модалка редактирования -->
    <div class="modal fade" id="editModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">

          <div class="modal-header">
            <h5>Редактировать</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>

          <div class="modal-body">

            <input v-model="editPassenger.full_name" class="form-control mb-2">
            <input v-model="editPassenger.passport" class="form-control mb-2">
            <input v-model="editPassenger.phone" class="form-control mb-2">

            <input type="file" class="form-control mb-2" ref="editFile" @change="onEditFileChange">

            <img v-if="editPreview" :src="editPreview" class="img-thumbnail" style="max-height:90px">

          </div>

          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button class="btn btn-primary" data-bs-dismiss="modal" @click="saveEdit">Сохранить</button>
          </div>

        </div>
      </div>
    </div>

    <!-- Просмотр фото -->
    <div v-if="showImage" class="modal fade show d-block" style="background:rgba(0,0,0,0.8)">
      <div class="d-flex justify-content-center align-items-center vh-100">
        <img :src="imageUrl" class="img-fluid rounded" style="max-height:90vh">
      </div>
      <button class="btn btn-light position-fixed top-0 end-0 m-3" @click="showImage = false">
        ✖
      </button>
    </div>

  </div>
</template>
<style scoped>
.img-thumbnail {
  cursor: pointer;
}
</style>
