<script setup>
import { computed, onBeforeMount, ref } from "vue";
import axios from "axios";
import AppIcon from "@/components/AppIcon.vue";
import CodeInput from "@/components/CodeInput.vue";
import { errorText } from "@/utils/apiHelper";

const secret = ref("");
const code = ref("");
const isConfigured = ref(false);
const isConfirmed = ref(false);
const activeUntil = ref("");
const error = ref("");
const isLoading = ref(false);

const activeUntilText = computed(() =>
  activeUntil.value
    ? new Date(activeUntil.value).toLocaleTimeString("ru-RU")
    : "",
);

async function loadStatus() {
  error.value = "";
  try {
    const [setupResponse, statusResponse] = await Promise.all([
      axios.get("/api/profile/otp-setup/"),
      axios.get("/api/profile/otp-status/"),
    ]);
    isConfigured.value = setupResponse.data.configured;
    secret.value = setupResponse.data.secret ?? "";
    isConfirmed.value = statusResponse.data.confirmed;
    activeUntil.value = statusResponse.data.active_until ?? "";
  } catch (requestError) {
    error.value = errorText(requestError);
  }
}

async function verifyCode() {
  error.value = "";
  isLoading.value = true;
  try {
    const { data } = await axios.post("/api/profile/otp-login/", {
      key: code.value,
    });
    isConfirmed.value = data.success;
    isConfigured.value = true;
    activeUntil.value = data.active_until;
    secret.value = "";
    code.value = "";
  } catch (requestError) {
    error.value = errorText(requestError);
  } finally {
    isLoading.value = false;
  }
}

onBeforeMount(loadStatus);
</script>

<template>
  <section class="card">
    <div class="card-header">
      <h2 class="card-title">Двухфакторная аутентификация</h2>
    </div>
    <div class="card-body form">
      <div class="twofa-status">
        <span
          class="twofa-status-icon"
          :class="isConfirmed ? 'is-on' : 'is-off'"
        >
          <AppIcon
            :name="isConfirmed ? 'shield-check' : 'shield-alert'"
            large
          />
        </span>
        <div>
          <div class="text-strong">
            {{ isConfirmed ? "Код подтверждён" : "Код не подтверждён" }}
          </div>
          <div class="text-muted text-sm">
            {{
              isConfirmed
                ? `Изменение данных разрешено до ${activeUntilText}`
                : "Подтвердите код, чтобы разрешить изменение данных на 10 минут"
            }}
          </div>
        </div>
      </div>

      <div v-if="secret" class="form-field">
        <span class="form-label">Ключ для приложения-аутентификатора</span>
        <code class="twofa-secret">{{ secret }}</code>
        <span class="form-hint">
          Добавьте ключ в приложение-аутентификатор, затем введите текущий
          шестизначный код.
        </span>
      </div>
      <p v-else-if="isConfigured" class="form-hint">
        Приложение-аутентификатор уже подключено. Введите код из него.
      </p>

      <form class="form" @submit.prevent="verifyCode">
        <div class="form-field">
          <label class="form-label" for="twofa-code">Код из приложения</label>
          <CodeInput id="twofa-code" v-model="code" :invalid="!!error" />
          <span v-if="error" class="form-error-text">
            {{ error }}
          </span>
        </div>
        <div class="inline-row">
          <button
            class="btn btn-primary"
            type="submit"
            :disabled="isLoading || code.length !== 6"
          >
            {{ isLoading ? "Проверка..." : "Подтвердить код" }}
          </button>
        </div>
      </form>
    </div>
  </section>
</template>

<style scoped>
.twofa-secret {
  padding: var(--space-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface-alt);
  font-size: var(--font-size-sm);
  overflow-wrap: anywhere;
}
</style>
