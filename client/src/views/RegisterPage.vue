<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import useProfileStore from "@/stores/profileStore";

const router = useRouter();
const profileStore = useProfileStore();

const username = ref("");
const password = ref("");
const errorMessage = ref("");

async function handleRegister() {
  try {
    await profileStore.register(username.value, password.value);
    router.push({ name: "dashboard" });
  } catch (error) {
    console.error("Error ", error);
    errorMessage.value =
      "Произошла ошибка при регистрации. Пожалуйста, попробуйте снова.";
  }
}
function handleLogin() {
  router.push({ name: "login" });
}
</script>

<template>
  <div class="login-page">
    <h1 class="header-login">Регистрация</h1>
    <form @submit.prevent.stop="handleRegister" class="login-form">
      <div>
        <label for="username">Имя пользователя:</label>
        <input type="text" id="username" v-model="username" required />
      </div>

      <div>
        <label for="password">Пароль:</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">Зарегистрироваться</button>
    </form>

    <button @click="handleLogin" type="submit">На страницу входа</button>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
  </div>
</template>

<style scoped>
.header-login {
  text-align: center;
  font-size: 45px;
}
.login-form {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.error-message {
  color: red;
  text-align: center;
}
.login-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
}
</style>
