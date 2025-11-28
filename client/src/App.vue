<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';

import {computed, onBeforeMount, ref} from 'vue';
import {useUserStore} from '@/stores/user_store';
import {storeToRefs} from "pinia";
const userStore = useUserStore()

const username = ref();
const password = ref();
const {
    userInfo,
} = storeToRefs(userStore)
async function onFormSend() {
    userStore.login(username.value, password.value)
}
async function handleLogout() {
    await userStore.logout();
}
onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})
</script>
<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container">
        <a class="navbar-brand" href="#">Авиасистема</a>
        <div class="navbar-nav">
          <router-link to="/" class="nav-link">Главная</router-link>
          <router-link to="/airlines" class="nav-link">Авиакомпании</router-link>
          <router-link to="/flights" class="nav-link">Рейсы</router-link>
          <router-link to="/passengers" class="nav-link">Пассажиры</router-link>
          <router-link to="/rates" class="nav-link">Тарифы</router-link>
          <router-link to="/tickets" class="nav-link">Билеты</router-link>
        </div>
      </div>

      <ul class="navbar-nav">
<li class="nav-item dropdown">
  <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
    Пользователь
  </a>
  <ul class="dropdown-menu">
    <li><a class="dropdown-item" href="/admin">Админка</a></li>
    <li><a class="dropdown-item" href="#" @click="handleLogout">Выйти</a></li>
  </ul>
</li>
</ul>
    </nav>
    <router-view />
  </div>
</template>



<style>
.router-link-active {
  font-weight: bold;
}
</style>