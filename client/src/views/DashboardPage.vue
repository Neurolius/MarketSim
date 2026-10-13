<script setup>
import HeaderNavbar from "@/components/HeaderNavbar.vue";
</script>

<template>
  <div><HeaderNavbar /></div>
  <div class="main">
    <div>
      Общая стоимость портфелей
      <div>//График стоимости</div>
    </div>
    <div>
      <div>Последние сделки</div>
      <div>//Таблица последних сделок</div>
    </div>
    <div>
      <div>Лучшие инструменты</div>
      <div>Карточки лучших инструментов</div>
    </div>
  </div>
</template>

<style scoped>
.main {
  display: flex;
  justify-content: space-between;
}
</style>
