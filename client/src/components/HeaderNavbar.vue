<script setup>
import { ref } from "vue";

const balance = ref(10000);
</script>

<template>
  <div>
    <div class="header-navbar">
      <div>logo</div>
      <a href="/dashboard">Главная</a>
      <a href="/portfolios">Список портфелей</a>
      <a href="/instruments">Список инструментов</a>
      <a href="/profile">Профиль</a>
      <div>Баланс: {{ balance }}</div>
      <button>Выход</button>
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
