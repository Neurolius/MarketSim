<script setup>
import AppIcon from '@/components/AppIcon.vue'
import BaseModal from '@/components/BaseModal.vue'

defineProps({
  title: {
    type: String,
    required: true,
  },
  text: {
    type: String,
    default: 'Действие нельзя отменить.',
  },
  confirmText: {
    type: String,
    default: 'Удалить',
  },
})

defineEmits(['close', 'confirm'])
</script>

<template>
  <BaseModal size="sm" @close="$emit('close')">
    <div class="confirm">
      <span class="confirm-icon">
        <AppIcon name="trash" large />
      </span>
      <h2 class="confirm-title">{{ title }}</h2>
      <p class="text-muted text-sm">{{ text }}</p>
    </div>

    <template #footer>
      <button class="btn btn-secondary" type="button" @click="$emit('close')">Отмена</button>
      <button class="btn btn-sell" type="button" @click="$emit('confirm')">{{ confirmText }}</button>
    </template>
  </BaseModal>
</template>

<style scoped>
.confirm {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-4);
}

.confirm-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--color-down-soft);
  color: var(--color-down);
}

.confirm-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
}
</style>
