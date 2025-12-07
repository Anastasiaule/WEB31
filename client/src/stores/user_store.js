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
            // гет запрос для получения инфы о пользователе
            let r = await axios.get("/api/user/info/")
            // Обновляем данные пользователя в store
            userInfo.value = r.data;
        } catch (error) {
            userInfo.value = {
                is_authenticated: false,
            };
        }
    }

    // Функция авторизации
    async function login(username, password) {
        //пост запрос с логином и паролем
        let r = await axios.post("/api/user/login/", {
            username: username,
            password: password,
        })
        // чекаем статус после отправки
        await checkLogin();
    }

    // Функция выхода
    async function logout() {
        try {
            // запрос на выход (выхода нет, скоро рассвет, ключ поверни и полетели)
            await axios.post("/api/user/logout/");
        } catch (error) {
            // Если ошибка, то просто ошибка
            console.error("Logout error:", error);
        } finally {
            userInfo.value = {
                is_authenticated: false,
            };
        }
    }

    onBeforeMount(async () => {
        await checkLogin();
    })

    return {
        userInfo, 
        checkLogin, 
        login,  
        logout,   
    }
})