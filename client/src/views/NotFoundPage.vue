<script setup>
import HeaderNavbar from '@/components/HeaderNavbar.vue'
import EmptyState from '@/components/EmptyState.vue'
</script>

<template>
  <HeaderNavbar />
  <main class="page">
    <section class="card">
      <EmptyState
        icon="alert"
        title="Страница не найдена (404)"
        text="Инструмент или портфель удалён либо ссылка неверна."
        danger
      >
        <router-link :to="{ name: 'dashboard' }" class="btn btn-secondary">На дашборд</router-link>
      </EmptyState>
    </section>
  </main>
</template>
