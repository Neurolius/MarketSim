<script setup>
defineProps({
  modelValue: {
    type: String,
    default: "",
  },
  id: {
    type: String,
    default: "code-input",
  },
  invalid: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["update:modelValue"]);
</script>

<template>
  <input
    :id="id"
    class="form-input code-input"
    :class="{ 'is-invalid': invalid }"
    type="text"
    inputmode="numeric"
    autocomplete="one-time-code"
    maxlength="6"
    :value="modelValue"
    @input="$emit('update:modelValue', $event.target.value)"
  />
</template>

<style scoped>
.code-input {
  max-width: 240px;
  font-variant-numeric: tabular-nums;
}

.code-input.is-invalid {
  border-color: var(--color-down);
}
</style>
