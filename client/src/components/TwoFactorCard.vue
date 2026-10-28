<script setup>
import AppIcon from '@/components/AppIcon.vue'
import CodeInput from '@/components/CodeInput.vue'

defineProps({
  // код подтверждён и действует
  isConfirmed: {
    type: Boolean,
    default: false,
  },
  // до какого времени действует подтверждение, например '15:05'
  activeUntil: {
    type: String,
    default: '',
  },
  error: {
    type: String,
    default: '',
  },
})

defineEmits(['submit', 'resend'])
</script>

<template>
  <section class="card">
    <div class="card-header">
      <h2 class="card-title">Двухфакторная аутентификация</h2>
    </div>
    <form class="card-body form" @submit.prevent="$emit('submit')">
      <div class="twofa-status">
        <span class="twofa-status-icon" :class="isConfirmed ? 'is-on' : 'is-off'">
          <AppIcon :name="isConfirmed ? 'shield-check' : 'shield-alert'" large />
        </span>
        <div>
          <div class="text-strong">{{ isConfirmed ? 'Код подтверждён' : 'Код не подтверждён' }}</div>
          <div class="text-muted text-sm">
            {{
              isConfirmed
                ? 'Можно изменять и удалять данные'
                : 'Без кода нельзя изменять и удалять данные'
            }}
          </div>
        </div>
      </div>

      <template v-if="!isConfirmed">
        <div class="form-field">
          <label class="form-label" for="twofa-code">Код из письма</label>
          <CodeInput id="twofa-code" :invalid="!!error" />
          <span v-if="error" class="form-error-text">{{ error }}</span>
          <span v-else class="form-hint">Код действует ограниченное время</span>
        </div>
        <div class="inline-row">
          <button class="btn btn-primary" type="submit">Подтвердить</button>
          <button class="btn btn-ghost" type="button" @click="$emit('resend')">
            Отправить код ещё раз
          </button>
        </div>
      </template>
    </form>
    <div v-if="isConfirmed" class="card-footer">
      <span class="text-muted">Подтверждённое состояние:</span>
      <span class="badge badge-executed">Активна до {{ activeUntil }}</span>
    </div>
  </section>
</template>
