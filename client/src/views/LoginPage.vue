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
    } else {
      errorMessage.value = "Неверный юзернейм или пароль";
    }
  } catch (error) {
    errorMessage.value = error.message;
  }
}
</script>

<template>
  <div>
    <h1>Login</h1>
    <form @submit.prevent.stop="handleLogin">
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
    <p v-if="errorMessage" style="color: red">{{ errorMessage }}</p>
  </div>
</template>

<style scoped></style>
