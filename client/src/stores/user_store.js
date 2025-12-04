import {defineStore} from "pinia";        
import {onBeforeMount, ref} from "vue";  
import axios from "axios";   

export const useUserStore = defineStore("userStore", () => {
    // переменная для инфы о пользователе
    const userInfo = ref({
        is_authenticated: false,  // По умолчанию не авторизовано
    })
    
    // проверка авторизации
    async function checkLogin() {
        try {
            // Отправляем GET запрос для получения инфы о пользователе
            let r = await axios.get("/api/user/info/")
            // Обновляем данные пользователя в store
            userInfo.value = r.data;
        } catch (error) {
            // Если ошибка-сбрасываем
            userInfo.value = {
                is_authenticated: false,
            };
        }
    }

    // Функция авторизации
    async function login(username, password) {
        // Отправляем POST запрос с логином и паролем
        let r = await axios.post("/api/user/login/", {
            username: username,
            password: password,
        })
        // чекаем статус после успешной отправки
        await checkLogin();
    }

    // Функция выхода из системы
    async function logout() {
        try {
            // Отправляем запрос для выхода
            await axios.post("/api/user/logout/");
        } catch (error) {
            // Если ошибка, то просто ошибка
            console.error("Logout error:", error);
        } finally {
            // В любом случае сбрасываем данные пользователя на фронтенде
            userInfo.value = {
                is_authenticated: false,
            };
        }
    }

    // Хук жизненного цикла Vue - выполняется перед монтированием компонента
    onBeforeMount(async () => {
        // При загрузке приложения проверяем, авторизован ли пользователь
        await checkLogin();
    })

    // Возвращаем наружу все переменные и функции
    return {
        userInfo,      // Реактивные данные пользователя
        checkLogin,    // Функция проверки авторизации
        login,         // Функция входа
        logout,        // Функция выхода
    }
})