<script setup>
import axios from "axios";
import { ref, onMounted } from "vue";

const airlines = ref([]);
const stats = ref({});
const loading = ref(true);

const user = ref({
  is_superuser: false,
  is_authenticated: false,
});

// Добавление
const newAirlineName = ref("");
const newAirlineFile = ref(null);
const newPreview = ref("");

// Редактирование
const editAirline = ref({});
const editFile = ref(null);
const editPreview = ref("");

// Просмотр изображения
const modalImage = ref("");
const showImage = ref(false);

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

// === Добавление ===
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

// === Удаление ===
async function removeAirline(a) {
  if (!confirm(`Удалить "${a.name}"?`)) return;
  await axios.delete(`/api/airlines/${a.id}/`);
  await loadAirlines();
  await loadStats();
}

// === Редактирование ===
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

// === Модалка изображения ===
function openImage(url) {
  modalImage.value = url;
  showImage.value = true;
}
</script>

<template>
  <div class="container py-4" style="max-width: 900px">

    <div class="alert alert-info text-center mb-4">
       Всего: <b>{{ stats.count || 0 }}</b> •
       С лого <b>{{ airlines.filter(a => a.picture).length }}</b> •
       без лого: <b>{{ (stats.count || 0) - airlines.filter(a => a.picture).length }}</b> 
    </div>
    <!-- === ДОБАВЛЕНИЕ (для суперюзера) === -->
    <div v-if="user.is_superuser" class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <h5 class="mb-3">Добавить авиакомпанию</h5>

        <input class="form-control mb-2" v-model="newAirlineName" placeholder="Название" />

        <input class="form-control mb-2" type="file" accept="image/*" @change="handleAddFile" />

        <div v-if="newPreview" class="text-center mb-3">
          <img :src="newPreview" class="img-fluid rounded" style="max-height: 100px;" />
        </div>

        <button class="btn btn-primary w-100" @click="addAirline">Добавить</button>
      </div>
    </div>

    <!-- === СПИСОК === -->
    <div class="card border-0 shadow-sm">
      <div class="card-body">

        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border"></div>
          <p class="mt-2">Загрузка...</p>
        </div>

        <div v-else-if="airlines.length === 0" class="text-center text-muted py-5">
          <h5>Нет авиакомпаний</h5>
        </div>

        <div v-else>
          <div v-for="a in airlines" :key="a.id" class="border rounded p-3 mb-3">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <strong>{{ a.name }}</strong>
                <div class="mt-2">
                  <img
                    v-if="a.picture"
                    :src="a.picture"
                    @click="openImage(a.picture)"
                    style="height: 60px; cursor: zoom-in;"
                    class="rounded border"
                  />
                  <span v-else class="text-muted small">Нет логотипа</span>
                </div>
              </div>

              <div v-if="user.is_superuser" class="ms-3">
                <button class="btn btn-sm btn-warning me-2" data-bs-toggle="modal" data-bs-target="#editModal" @click="startEdit(a)">✏</button>
                <button class="btn btn-sm btn-danger" @click="removeAirline(a)">✖</button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- === МОДАЛКА РЕДАКТИРОВАНИЯ === -->
    <div class="modal fade" id="editModal">
      <div class="modal-dialog">
        <div class="modal-content border-0">
          <div class="modal-header bg-warning">
            <h5 class="modal-title">Редактирование</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>

          <div class="modal-body">

            <input class="form-control mb-2" v-model="editAirline.name" />

            <input class="form-control mb-2" type="file" accept="image/*" @change="handleEditFile" />

            <div v-if="editPreview" class="text-center">
              <img :src="editPreview" style="max-height: 120px" class="img-fluid rounded" />
            </div>

          </div>

          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
            <button class="btn btn-primary" data-bs-dismiss="modal" @click="saveEdit">Сохранить</button>
          </div>
        </div>
      </div>
    </div>

    <!-- === МОДАЛКА ИЗОБРАЖЕНИЯ === -->
    <div
      v-if="showImage"
      class="position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center"
      style="background: rgba(0,0,0,0.8); z-index: 2000;"
    >
      <img :src="modalImage" class="img-fluid rounded shadow" style="max-height: 90vh" />
      <button class="btn btn-light position-fixed top-0 end-0 m-3" @click="showImage = false">✖</button>
    </div>

  </div>
</template>

<style scoped>
.card {
  border-radius: 10px;
}
</style>
