<script setup>
defineProps({
  id: {
    type: String,
    default: 'code-input',
  },
  length: {
    type: Number,
    default: 6,
  },
  invalid: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <div class="code-input" :class="{ 'is-invalid': invalid }">
    <input
      v-for="n in length"
      :key="n"
      :id="n === 1 ? id : undefined"
      class="code-cell"
      type="text"
      inputmode="numeric"
      maxlength="1"
      autocomplete="one-time-code"
      :aria-label="`Цифра ${n}`"
    />
  </div>
</template>

<style scoped>
.code-input {
  display: flex;
  gap: var(--space-2);
}

.code-cell {
  width: 44px;
  height: 52px;
  text-align: center;
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  font-size: var(--font-size-xl);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.code-cell:focus {
  outline: 3px solid var(--color-accent-soft);
  border-color: var(--color-accent);
}

.code-input.is-invalid .code-cell {
  border-color: var(--color-down);
}

@media (max-width: 760px) {
  .code-cell {
    width: 40px;
    height: 48px;
  }
}
</style>
