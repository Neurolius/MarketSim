<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import useProfileStore from "@/stores/profileStore";
import { storeToRefs } from "pinia";

const router = useRouter();

const profileStore = useProfileStore();
const { isAuthenticated } = storeToRefs(profileStore);

const username = ref("");
const password = ref("");
const errorMessage = ref("");

async function handleLogin() {
  try {
    await profileStore.login(username.value, password.value);
    if (isAuthenticated.value) {
      router.push({ name: "dashboard" });
    }
  } catch (error) {
    if (error.response && error.response.status === 403) {
      errorMessage.value = "Неверный юзернейм или пароль";
    } else {
      errorMessage.value =
        "Произошла ошибка при входе. Пожалуйста, попробуйте снова.";
    }
  }
}

function handleRegister() {
  router.push({ name: "register" });
}
</script>

<template>
  <div class="login-page">
    <h1 class="header-login">Login</h1>
    <form @submit.prevent.stop="handleLogin" class="login-form">
      <div>
        <label for="username">Юзернейм:</label>
        <input type="text" v-model="username" id="username" required />
      </div>
      <div>
        <label for="password">Пароль:</label>
        <input type="password" v-model="password" id="password" required />
      </div>

      <button type="submit">Войти</button>
    </form>

    <button @click="handleRegister" type="submit">Регистрация</button>
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
