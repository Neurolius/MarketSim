<script setup>
import { useRouter } from 'vue-router'
import useProfileStore from '@/stores/profileStore'
import AppIcon from '@/components/AppIcon.vue'

const router = useRouter()
const profileStore = useProfileStore()
const username = profileStore.userName

async function handleExit() {
  await profileStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <header class="header-navbar">
    <div class="navbar-inner">
      <router-link :to="{ name: 'dashboard' }" class="navbar-brand">
        <span class="navbar-logo">MS</span>
        <span>MarketSim</span>
      </router-link>

      <nav class="navbar-links" aria-label="Основная навигация">
        <router-link :to="{ name: 'dashboard' }" class="navbar-link" active-class="is-active">
          Дашборд
        </router-link>
        <router-link :to="{ name: 'instruments' }" class="navbar-link" active-class="is-active">
          Инструменты
        </router-link>
        <router-link :to="{ name: 'portfolios' }" class="navbar-link" active-class="is-active">
          Портфели
        </router-link>
        <router-link :to="{ name: 'profile' }" class="navbar-link" active-class="is-active">
          Профиль
        </router-link>
        <router-link
          v-if="profileStore.isSuperuser"
          :to="{ name: 'instrument-types' }"
          class="navbar-link"
          active-class="is-active"
        >
          Типы инструментов
        </router-link>
      </nav>

      <div class="navbar-user">
        <a v-if="profileStore.isSuperuser" class="navbar-admin-btn" href="/admin">
          <AppIcon name="shield" />
          Админ-панель
        </a>
        <router-link :to="{ name: 'profile' }" class="navbar-username">
          <span class="avatar">{{ username?.slice(0, 2).toUpperCase() }}</span>
          {{ username }}
        </router-link>
        <button class="navbar-logout" type="button" @click="handleExit">
          <AppIcon name="logout" />
          Выйти
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header-navbar {
  background: var(--color-nav);
  color: var(--color-nav-text);
}

.navbar-inner {
  max-width: var(--page-max-width);
  margin: 0 auto;
  min-height: var(--navbar-height);
  padding: 0 var(--space-6);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-6);
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-text-inverse) !important;
  font-weight: 700;
  font-size: var(--font-size-lg);
  text-decoration: none !important;
}

.navbar-logo {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-md);
  background: var(--color-accent);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.navbar-links {
  display: flex;
  gap: var(--space-1);
  flex: 1 1 auto;
  overflow-x: auto;
}

.navbar-link {
  color: var(--color-nav-text) !important;
  padding: 0 var(--space-3);
  min-height: 40px;
  display: flex;
  align-items: center;
  border-radius: var(--radius-md);
  font-weight: 500;
  white-space: nowrap;
  text-decoration: none !important;
  transition: background-color 0.15s;
}

.navbar-link:hover {
  background: var(--color-nav-hover);
  color: #fff !important;
}

.navbar-link.is-active {
  background: var(--color-nav-hover);
  color: #fff !important;
  box-shadow: inset 0 -2px 0 var(--color-accent);
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-left: auto;
}

.navbar-admin-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  min-height: 34px;
  padding: 0 var(--space-3);
  border: 1px solid #3a4763;
  border-radius: var(--radius-md);
  color: #fff !important;
  font-weight: 500;
  font-size: var(--font-size-sm);
  text-decoration: none !important;
}

.navbar-admin-btn:hover {
  background: var(--color-nav-hover);
}

.navbar-username {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  color: #fff !important;
  font-weight: 500;
  text-decoration: none !important;
}

.navbar-logout {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  min-height: 34px;
  padding: 0 var(--space-3);
  background: transparent;
  border: 0;
  border-radius: var(--radius-md);
  color: var(--color-nav-text);
  font-size: var(--font-size-sm);
  cursor: pointer;
}

.navbar-logout:hover {
  background: var(--color-nav-hover);
  color: #fff;
}

@media (max-width: 760px) {
  .navbar-inner {
    padding: var(--space-2) var(--space-4);
    gap: var(--space-2);
  }

  .navbar-links {
    order: 3;
    flex-basis: 100%;
  }
}
</style>
