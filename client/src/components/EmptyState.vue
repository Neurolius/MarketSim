<script setup>
import AppIcon from '@/components/AppIcon.vue'

defineProps({
  icon: {
    type: String,
    default: 'search',
  },
  title: {
    type: String,
    required: true,
  },
  text: {
    type: String,
    default: '',
  },
  // красная иконка — для страниц ошибок (403, 404)
  danger: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <div class="empty-state">
    <span class="empty-state-icon" :class="{ 'is-danger': danger }">
      <AppIcon :name="icon" large />
    </span>
    <span class="empty-state-title">{{ title }}</span>
    <span v-if="text" class="empty-state-text">{{ text }}</span>
    <div v-if="$slots.default" class="empty-state-actions">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--space-2);
  padding: var(--space-10) var(--space-6);
  color: var(--color-text-muted);
}

.empty-state-icon {
  width: 48px;
  height: 48px;
  margin-bottom: var(--space-2);
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--color-neutral-soft);
  color: var(--color-neutral);
}

.empty-state-icon.is-danger {
  background: var(--color-down-soft);
  color: var(--color-down);
}

.empty-state-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text);
}

.empty-state-text {
  max-width: 360px;
  font-size: var(--font-size-sm);
}

.empty-state-actions {
  margin-top: var(--space-2);
  display: flex;
  gap: var(--space-2);
}
</style>
