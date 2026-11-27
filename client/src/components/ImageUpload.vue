<script setup>
import { ref, watch } from "vue";
import AppIcon from "@/components/AppIcon.vue";

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
  modelValue: {
    type: Object,
    default: null,
  },
  icon: {
    type: String,
    default: "upload",
  },
  actionText: {
    type: String,
    default: "Выберите файл",
  },
  text: {
    type: String,
    default: "или перетащите сюда",
  },
  hint: {
    type: String,
    default: "PNG, JPG до 5 МБ",
  },
});

const emit = defineEmits(["update:modelValue"]);
const input = ref(null);

watch(
  () => props.modelValue,
  (file) => {
    if (!file && input.value) input.value.value = "";
  },
);

function onChange(event) {
  emit("update:modelValue", event.target.files[0] ?? null);
}

function onDrop(event) {
  emit("update:modelValue", event.dataTransfer.files[0] ?? null);
}
</script>

<template>
  <div class="image-upload">
    <label
      class="image-upload-dropzone"
      :for="id"
      @dragover.prevent
      @drop.prevent="onDrop"
    >
      <AppIcon v-if="icon" :name="icon" large />
      <span>
        <strong>{{ actionText }}</strong>
        {{ text }}
      </span>
      <span v-if="hint" class="text-xs">{{ hint }}</span>
      <span v-if="modelValue" class="text-xs">
        Выбрано изображений: 1 ({{ modelValue.name }})
      </span>
    </label>
    <input
      ref="input"
      :id="id"
      class="visually-hidden"
      type="file"
      @change="onChange"
    />
  </div>
</template>

<style scoped>
.image-upload-dropzone {
  min-height: 104px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: var(--space-3);
  border: 2px dashed var(--color-border-strong);
  border-radius: var(--radius-md);
  background: var(--color-surface-alt);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  text-align: center;
  cursor: pointer;
}

.image-upload-dropzone:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.image-upload-dropzone strong {
  color: var(--color-accent);
}
</style>
