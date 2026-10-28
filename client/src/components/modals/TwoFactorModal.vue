<script setup>
import AppIcon from '@/components/AppIcon.vue'
import BaseModal from '@/components/BaseModal.vue'
import CodeInput from '@/components/CodeInput.vue'

defineProps({
  // замаскированный email, на который отправлен код
  email: {
    type: String,
    default: '',
  },
  error: {
    type: String,
    default: '',
  },
})

defineEmits(['close', 'submit', 'resend'])
</script>

<template>
  <BaseModal title="Подтвердите действие" size="sm" form @close="$emit('close')" @submit="$emit('submit')">
    <div class="twofa-status">
      <span class="twofa-status-icon is-off">
        <AppIcon name="shield" large />
      </span>
      <p class="text-sm">
        Для изменения данных нужен код двухфакторной аутентификации. Мы отправили его на
        {{ email }}.
      </p>
    </div>
    <div class="form-field">
      <label class="form-label" for="twofa-modal-code">Код</label>
      <CodeInput id="twofa-modal-code" :invalid="!!error" />
      <span v-if="error" class="form-error-text">{{ error }}</span>
    </div>
    <button class="btn btn-ghost btn-sm align-start" type="button" @click="$emit('resend')">
      Отправить код ещё раз
    </button>

    <template #footer>
      <button class="btn btn-secondary" type="button" @click="$emit('close')">Отмена</button>
      <button class="btn btn-primary" type="submit">Подтвердить</button>
    </template>
  </BaseModal>
</template>

<style scoped>
.align-start {
  align-self: flex-start;
}
</style>
