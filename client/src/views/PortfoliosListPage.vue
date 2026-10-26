<script setup>
import HeaderNavbar from '@/components/HeaderNavbar.vue'
import PortfolioCard from '@/components/PortfolioCard.vue'
</script>

<template>
  <HeaderNavbar />
  <div>
    Список портфелей
    <div>Карточки портфелей</div>
    <div>
      CRUD портфеля и при нажатии на карточку подробные детали(позиции) и возможность продажи и
      сделки этого портфеля
    </div>
    <PortfolioCard />
  </div>
</template>

<style scoped></style>
