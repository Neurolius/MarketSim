<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number],
    default: '',
  },
  hint: {
    type: String,
    default: '',
  },
  // цвет значения: 'up' | 'down' | 'warn' | 'muted'
  tone: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <div class="stat-card">
    <span class="stat-label">{{ label }}</span>
    <span class="stat-value" :class="tone && `is-${tone}`">
      <slot>{{ value }}</slot>
    </span>
    <span v-if="hint" class="stat-hint">{{ hint }}</span>
  </div>
</template>

<style scoped>
.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.stat-label {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.stat-value {
  font-size: var(--font-size-xl);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.stat-value.is-up {
  color: var(--color-up);
}

.stat-value.is-down {
  color: var(--color-down);
}

.stat-value.is-warn {
  color: var(--color-warn);
}

.stat-value.is-muted {
  color: var(--color-text-muted);
}

.stat-hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}
</style>
