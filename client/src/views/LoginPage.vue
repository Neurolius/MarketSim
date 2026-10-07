<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const username = ref("");
const password = ref("");
const router = useRouter();

async function handleLogin() {
  router.push({ name: "home" });
}
</script>

<template>
  <div>
    <h1>Login</h1>
    <form @submit.prevent="handleLogin">
      <div>
        <label for="username">Юзернейм:</label>
        <input type="text" id="username" required />
      </div>
      <div>
        <label for="password">Пароль:</label>
        <input type="password" id="password" required />
      </div>

      <button type="submit">Войти</button>
    </form>
  </div>
</template>

<style scoped></style>
