<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import useProfileStore from '@/stores/profileStore'
import { storeToRefs } from 'pinia'

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
  <div class="login-page">
    <div class="login-card">
      <div class="login-card__header">
        <div class="login-card__title">Вход</div>
        <div class="login-card__subtitle">Симулятор биржи для обучения трейдингу</div>
      </div>
      <div v-if="errorMessage" class="login-card__error">
        {{ errorMessage }}
      </div>
      <form @submit.prevent.stop="handleLogin" class="login-form">
        <div>
          <label for="username" class="form-label">Имя пользователя</label>
          <input
            type="text"
            v-model="username"
            id="username"
            required
            class="form-input"
            :class="{ 'form-input--error': errorMessage }"
          />
        </div>
        <div>
          <label for="password" class="form-label">Пароль</label>
          <input
            type="password"
            v-model="password"
            id="password"
            required
            class="form-input"
            :class="{ 'form-input--error': errorMessage }"
          />
        </div>

        <button type="submit" class="login-btn">Войти</button>
      </form>
      <div class="login-card__footer">
        Нет аккаунта?
        <router-link to="/register" class="link">Зарегистрироваться</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f2f4f7;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background-color: #ffffff;
  border: 1px solid #e1e5eb;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(16, 24, 40, 0.12);
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.login-card__title {
  font-size: 26px;
  font-weight: 700;
  margin: 0;
}

.login-card__subtitle {
  color: #545d6b;
  margin: 4px 0 0;
}

.login-card__error {
  background: #fde9ea;
  border-color: #f3c1c4;
  color: #8e141b;
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 12px 16px;
  border-radius: 6px;
  border: 1px solid;
  font-size: 13px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.login-form label {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 13px;
  font-weight: 600;
  color: #141821;
}

.form-input {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  border: 1px solid #c9d0da;
  border-radius: 6px;
  background: #ffffff;
  color: #141821;
  font: inherit;
}

.form-input--error {
  border-color: #c41f28;
  background: #fffafa;
}

.login-btn {
  width: 100%;
  min-height: 46px;
  font-size: 16px;
  background: #1d4ed8;
  color: #fff !important;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 16px;
  border: 1px solid transparent;
  border-radius: 6px;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  text-decoration: none !important;
  transition:
    background-color 0.15s,
    border-color 0.15s;
}

.login-card__footer {
  text-align: center;
  font-size: 13px;
  color: #545d6b;
}

.link {
  color: #1d4ed8;
  font-weight: 600;
}
</style>
