<script setup>
import AppIcon from '@/components/AppIcon.vue'

defineProps({
  id: {
    type: String,
    required: true,
  },
  // ссылка на текущее изображение: null — без превью, '' — пустая заглушка превью
  previewUrl: {
    type: String,
    default: null,
  },
  // круглое превью — для логотипов
  round: {
    type: Boolean,
    default: false,
  },
  icon: {
    type: String,
    default: 'upload',
  },
  actionText: {
    type: String,
    default: 'Выберите файл',
  },
  text: {
    type: String,
    default: 'или перетащите сюда',
  },
  hint: {
    type: String,
    default: 'PNG, JPG до 5 МБ',
  },
})

defineEmits(['change', 'open-preview'])
</script>

<template>
  <div class="image-upload">
    <button
      v-if="previewUrl !== null"
      class="image-upload-preview"
      :class="{ 'is-round': round }"
      type="button"
      aria-label="Открыть изображение"
      @click="$emit('open-preview')"
    >
      <img v-if="previewUrl" :src="previewUrl" alt="" />
      <span v-else>превью</span>
    </button>
    <label class="image-upload-dropzone" :for="id">
      <AppIcon v-if="icon" :name="icon" large />
      <span>
        <strong>{{ actionText }}</strong>
        {{ text }}
      </span>
      <span v-if="hint" class="text-xs">{{ hint }}</span>
    </label>
    <input
      :id="id"
      class="visually-hidden"
      type="file"
      accept="image/*"
      @change="$emit('change', $event)"
    />
  </div>
</template>

<style scoped>
.image-upload {
  display: flex;
  gap: var(--space-4);
  align-items: stretch;
}

.image-upload-preview {
  width: 160px;
  height: 104px;
  flex: none;
  padding: 0;
  overflow: hidden;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: repeating-linear-gradient(135deg, #e3e8f0 0 10px, #d9dfe9 10px 20px);
  display: grid;
  place-items: center;
  font-size: 11px;
  color: var(--color-text-muted);
  cursor: zoom-in;
}

.image-upload-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-upload-preview.is-round {
  width: 72px;
  height: 72px;
  border-radius: 50%;
}

.image-upload-dropzone {
  flex: 1;
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

@media (max-width: 760px) {
  .image-upload {
    flex-direction: column;
  }
}
</style>
