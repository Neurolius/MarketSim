<script setup>
import { useRouter } from 'vue-router'
import useProfileStore from '@/stores/profileStore'

const router = useRouter()
const profileStore = useProfileStore()
const username = profileStore.userName

async function handleExit() {
  await profileStore.logout()
  router.push({ name: 'login' })
}

function handleProfile() {
  router.push({name: 'profile'})
}

</script>

<template>
  <header class="header-navbar">
    <div class="navbar-inner">
      <div class="logo">
        <router-link :to="{ name: 'dashboard'}">
          <span>MarketSim</span>
        </router-link>
      </div>
      <nav class="nav">
        <router-link :to="{ name: 'dashboard'}" class="nav-link">
          <span>Дашборд</span>
        </router-link>
        <router-link :to="{name: 'instruments'}" class="nav-link">
          <span>Инструменты</span>
        </router-link>
        <router-link :to="{ name: 'portfolios'}" class="nav-link">
          <span>Портфели</span>
        </router-link>
        <router-link :to="{ name: 'profile'}" class="nav-link">
          <span>Профиль</span>
        </router-link>
      </nav>
      <div class="profile-settings">
        <button class="admin-btn">Админ-панель</button>
        <button class="profile-btn" @click="handleProfile">{{ username }}</button>
        <button @click="handleExit" class="exit-btn">Выйти</button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header-navbar{
  background: #181818;
  color: #c7cfdd;
}

.navbar-inner{
  margin: 0 auto;
  min-height: 56px;
  padding: 0 24px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 24px;
}

.logo{
  font-weight: 700;
  font-size: 16px;
  color: #fff !important;
}

.nav{
  display: flex;
  gap: 4px;
  flex: 1 1 auto;
  overflow-x: auto;
}

.nav-link{
  color: #c7cfdd;
  padding: 0 12px;
  min-height: 40px;
  display: flex;
  align-items: center;
  border-radius: 6px;
  font-weight: 500;
  white-space: nowrap;
  text-decoration: none !important;
  transition:
    background-color 0.15s;
}

.nav-link:hover{
  background-color: #282828;
}

.nav-link.router-link-exact-active{
  background: #1c2740;
  color: #fff !important;
  box-shadow: inset 0 -2px 0 #1d4ed8;
}

.profile-settings{
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}

.admin-btn{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  min-height: 34px;
  border: 1px solid #3a4763;
  border-radius: 6px;
  background: transparent;
  color: #fff !important;
  font-weight: 500;
  font-size: 13px;
  text-decoration: none !important;
  cursor: pointer;
  transition:
    background-color 0.15s,
    border-color 0.15s;
}

.admin-btn:hover{
  background: #282828;
}

.profile-btn{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  min-height: 34px;
  border-radius: 6px;
  color: #fff !important;
  font-weight: 500;
  text-decoration: none !important;
  cursor: pointer;
  background: transparent;
  transition:
    background-color 0.15s;
  border: 1px solid #3a4763;
}

.profile-btn:hover{
  background: #282828;
}

.exit-btn{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  min-height: 34px;
  border: 1px solid #3a4763;
  border-radius: 6px;
  background: transparent;
  color: #fff !important;
  font-weight: 500;
  font-size: 13px;
  text-decoration: none !important;
  cursor: pointer;
  transition:
    background-color 0.15s,
    border-color 0.15s;
}

.exit-btn:hover{
  background: #282828;
}

</style>
