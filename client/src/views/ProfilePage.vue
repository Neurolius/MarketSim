<script setup>
import HeaderNavbar from "@/components/HeaderNavbar.vue";
import useProfileStore from "@/stores/profileStore";

const profileStore = useProfileStore();
const username = profileStore.userName;
</script>

<template>
  <div><HeaderNavbar /></div>
  <div>Данные профиля и настройки</div>
  <div>Имя пользователя: {{ username }}</div>
</template>

<style scoped></style>
