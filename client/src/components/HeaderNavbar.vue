<script setup>
import { useRouter } from "vue-router";
import useProfileStore from "@/stores/profileStore";

const router = useRouter();
const profileStore = useProfileStore();
async function handleExit() {
  await profileStore.logout();
  router.push({ name: "login" });
}
</script>

<template>
  <div>
    <div class="header-navbar">
      <div>logo</div>
      <router-link to="/dashboard">Главная</router-link>
      <router-link to="/portfolios">Список портфелей</router-link>
      <router-link to="/instruments">Список инструментов</router-link>
      <router-link to="/profile">Профиль</router-link>
      <form @submit.prevent.stop="handleExit">
        <button type="submit">Выход</button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.header-navbar {
  display: flex;
  justify-content: space-between;
}
a {
  text-decoration: none;
  color: black;
  cursor: pointer;
}
</style>
