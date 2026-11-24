<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  modelValue: {
    type: String,
    default: "",
  },
  id: {
    type: String,
    default: "code-input",
  },
  length: {
    type: Number,
    default: 6,
  },
  invalid: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:modelValue"]);
const cells = ref([]);
const inputs = ref([]);

watch(
  () => props.modelValue,
  (value) => {
    cells.value = Array.from(
      { length: props.length },
      (_, index) => value[index] ?? "",
    );
  },
  { immediate: true },
);

function updateCell(index, event) {
  const digits = event.target.value.replace(/\D/g, "");
  const nextCells = [...cells.value];

  if (digits.length > 1) {
    for (
      let offset = 0;
      offset < digits.length && index + offset < props.length;
      offset++
    ) {
      nextCells[index + offset] = digits[offset];
    }
  } else {
    nextCells[index] = digits;
  }

  cells.value = nextCells;
  emit("update:modelValue", nextCells.join(""));
  if (digits) {
    inputs.value[Math.min(index + digits.length, props.length - 1)]?.focus();
  }
}

function onKeydown(event, index) {
  if (event.key === "Backspace" && !cells.value[index] && index > 0) {
    inputs.value[index - 1]?.focus();
  }
}
</script>

<template>
  <div class="code-input" :class="{ 'is-invalid': invalid }">
    <input
      v-for="n in length"
      :key="n"
      :ref="(element) => (inputs[n - 1] = element)"
      :id="n === 1 ? id : undefined"
      class="code-cell"
      type="text"
      maxlength="1"
      :value="cells[n - 1]"
      @input="updateCell(n - 1, $event)"
      @keydown="onKeydown($event, n - 1)"
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
