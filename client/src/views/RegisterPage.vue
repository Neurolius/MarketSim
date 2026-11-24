<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import useProfileStore from "@/stores/profileStore";
import AppIcon from "@/components/AppIcon.vue";

const router = useRouter();
const profileStore = useProfileStore();

const username = ref("");
const email = ref("");
const password = ref("");
const passwordRepeat = ref("");
const errorMessage = ref("");

async function handleRegister() {
  errorMessage.value = "";
  if (password.value !== passwordRepeat.value) {
    errorMessage.value = "Пароли не совпадают.";
    return;
  }

  try {
    await profileStore.register(username.value, password.value, email.value);
    router.push({ name: "dashboard" });
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      "Произошла ошибка при регистрации. Попробуйте снова.";
  }
}
</script>

<template>
  <div class="auth-layout">
    <div class="auth-brand"><span class="auth-logo">MS</span>MarketSim</div>

    <form class="auth-card" @submit.prevent.stop="handleRegister">
      <div>
        <h1 class="auth-title">Регистрация</h1>
        <p class="auth-subtitle">
          После регистрации создайте первый портфель с виртуальным балансом
        </p>
      </div>

      <div v-if="errorMessage" class="alert alert-error">
        <AppIcon name="alert" />
        <span>{{ errorMessage }}</span>
      </div>

      <div class="form">
        <div class="form-field">
          <label class="form-label" for="reg-username">Имя пользователя</label>
          <input
            id="reg-username"
            v-model="username"
            class="form-input"
            :class="{ 'is-invalid': errorMessage }"
            type="text"
            autocomplete="username"
            required
          />
        </div>
        <div class="form-field">
          <label class="form-label" for="reg-email">Email</label>
          <input
            id="reg-email"
            v-model="email"
            class="form-input"
            type="email"
            autocomplete="email"
            placeholder="name@example.com"
          />
          <span class="form-hint"> Адрес электронной почты аккаунта </span>
        </div>
        <div class="form-field">
          <label class="form-label" for="reg-password">Пароль</label>
          <input
            id="reg-password"
            v-model="password"
            class="form-input"
            type="password"
            autocomplete="new-password"
            required
          />
          <span class="form-hint">Не менее 8 символов</span>
        </div>
        <div class="form-field">
          <label class="form-label" for="reg-password-repeat"
            >Повторите пароль</label
          >
          <input
            id="reg-password-repeat"
            v-model="passwordRepeat"
            class="form-input"
            type="password"
            autocomplete="new-password"
            required
          />
        </div>
        <button class="btn btn-primary btn-lg btn-block" type="submit">
          Создать аккаунт
        </button>
      </div>

      <p class="auth-footer">
        Уже есть аккаунт?
        <router-link :to="{ name: 'login' }">Войти</router-link>
      </p>
    </form>
  </div>
</template>
