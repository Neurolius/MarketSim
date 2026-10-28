<script setup>
import AppIcon from '@/components/AppIcon.vue'

defineProps({
  title: {
    type: String,
    default: '',
  },
  // 'sm' | 'md' | 'lg'
  size: {
    type: String,
    default: 'md',
  },
  // form — модалка оборачивается в <form>, кнопка type="submit" в футере отправляет её
  form: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['close', 'submit'])
</script>

<template>
  <Teleport to="body">
    <div class="modal-backdrop" @click.self="$emit('close')">
      <component
        :is="form ? 'form' : 'div'"
        class="modal"
        :class="`modal-${size}`"
        role="dialog"
        aria-modal="true"
        :aria-label="title"
        @submit.prevent="$emit('submit')"
      >
        <div v-if="title" class="modal-header">
          <h2 class="modal-title">{{ title }}</h2>
          <button class="modal-close" type="button" aria-label="Закрыть" @click="$emit('close')">
            <AppIcon name="close" />
          </button>
        </div>
        <div class="modal-body">
          <slot />
        </div>
        <div v-if="$slots.footer" class="modal-footer">
          <slot name="footer" />
        </div>
      </component>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: grid;
  place-items: center;
  padding: var(--space-4);
  background: rgba(10, 15, 28, 0.55);
}

.modal {
  width: 100%;
  max-width: 520px;
  max-height: calc(100vh - 32px);
  overflow: auto;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-modal);
}

.modal-sm {
  max-width: 420px;
}

.modal-lg {
  max-width: 640px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
}

.modal-close {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
}

.modal-close:hover {
  background: var(--color-neutral-soft);
  color: var(--color-text);
}

.modal-body {
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--color-border);
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  background: var(--color-surface-alt);
}
</style>
