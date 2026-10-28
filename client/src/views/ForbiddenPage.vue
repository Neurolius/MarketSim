<script setup>
import HeaderNavbar from '@/components/HeaderNavbar.vue'
import EmptyState from '@/components/EmptyState.vue'
</script>

<template>
  <HeaderNavbar />
  <main class="page">
    <section class="card">
      <EmptyState
        icon="lock"
        title="Доступ запрещён (403)"
        text="Эта страница доступна только суперпользователю."
        danger
      >
        <router-link :to="{ name: 'dashboard' }" class="btn btn-secondary">На дашборд</router-link>
      </EmptyState>
    </section>
  </main>
</template>
