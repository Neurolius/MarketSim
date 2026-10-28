<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import useProfileStore from '@/stores/profileStore'
import { storeToRefs } from 'pinia'
import AppIcon from '@/components/AppIcon.vue'

const router = useRouter()

const profileStore = useProfileStore()
const { isAuthenticated } = storeToRefs(profileStore)

const username = ref('')
const password = ref('')
const errorMessage = ref('')

async function handleLogin() {
  try {
    await profileStore.login(username.value, password.value)
    if (isAuthenticated.value) {
      router.push({ name: 'dashboard' })
    }
  } catch (error) {
    if (error.response && error.response.status === 403) {
      errorMessage.value = 'Неверный юзернейм или пароль'
    } else {
      errorMessage.value = 'Произошла ошибка при входе. Пожалуйста, попробуйте снова.'
    }
  }
}
</script>

<template>
  <div class="auth-layout">
    <div class="auth-brand"><span class="auth-logo">MS</span>MarketSim</div>

    <form class="auth-card" @submit.prevent.stop="handleLogin">
      <div>
        <h1 class="auth-title">Вход</h1>
        <p class="auth-subtitle">Симулятор биржи для обучения трейдингу</p>
      </div>

      <div v-if="errorMessage" class="alert alert-error" role="alert">
        <AppIcon name="alert" />
        <span>{{ errorMessage }}</span>
      </div>

      <div class="form">
        <div class="form-field">
          <label class="form-label" for="username">Имя пользователя</label>
          <input
            id="username"
            v-model="username"
            class="form-input"
            :class="{ 'is-invalid': errorMessage }"
            type="text"
            autocomplete="username"
            required
          />
        </div>
        <div class="form-field">
          <label class="form-label" for="password">Пароль</label>
          <input
            id="password"
            v-model="password"
            class="form-input"
            :class="{ 'is-invalid': errorMessage }"
            type="password"
            autocomplete="current-password"
            required
          />
        </div>
        <button class="btn btn-primary btn-lg btn-block" type="submit">Войти</button>
      </div>

      <p class="auth-footer">
        Нет аккаунта?
        <router-link :to="{ name: 'register' }">Зарегистрироваться</router-link>
      </p>
    </form>

    <!-- котировки: заменить на данные из API -->
    <div class="auth-ticker" aria-label="Котировки">
      <span>SBER <span class="price-change is-up">+2,07%</span></span>
      <span>BTC <span class="price-change is-up">+1,35%</span></span>
      <span>GAZP <span class="price-change is-down">−0,92%</span></span>
      <span>USD/RUB <span class="price-change is-down">−0,15%</span></span>
    </div>
  </div>
</template>
