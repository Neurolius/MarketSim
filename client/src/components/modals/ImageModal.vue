<script setup>
import AppIcon from '@/components/AppIcon.vue'

defineProps({
  src: {
    type: String,
    default: '',
  },
  caption: {
    type: String,
    default: '',
  },
})

defineEmits(['close'])
</script>

<template>
  <Teleport to="body">
    <div class="image-modal-backdrop" @click.self="$emit('close')">
      <button class="image-modal-close" type="button" aria-label="Закрыть" @click="$emit('close')">
        <AppIcon name="close" />
      </button>
      <div class="image-modal" role="dialog" aria-modal="true" aria-label="Просмотр изображения">
        <img v-if="src" class="image-modal-img" :src="src" :alt="caption" />
        <div v-else class="image-modal-img">изображение в полном размере</div>
        <div class="image-modal-caption">
          <span v-if="caption">{{ caption }}</span>
          <a v-if="src" :href="src" target="_blank" rel="noopener">Открыть оригинал</a>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.image-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: grid;
  place-items: center;
  padding: var(--space-4);
  background: rgba(10, 15, 28, 0.55);
}

.image-modal {
  width: 100%;
  max-width: 860px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.image-modal-img {
  width: 100%;
  max-height: calc(100vh - 120px);
  aspect-ratio: 16 / 9;
  object-fit: contain;
  border-radius: var(--radius-md);
  background: repeating-linear-gradient(135deg, #3a4559 0 14px, #333d50 14px 28px);
  display: grid;
  place-items: center;
  color: #c7cfdd;
  font-size: var(--font-size-sm);
}

.image-modal-caption {
  display: flex;
  gap: var(--space-4);
  align-items: center;
  color: #fff;
  font-size: var(--font-size-sm);
}

.image-modal-caption a {
  color: #c7d7ff;
}

.image-modal-close {
  position: absolute;
  top: var(--space-4);
  right: var(--space-4);
  width: 40px;
  height: 40px;
  border: 0;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  cursor: pointer;
}

.image-modal-close:hover {
  background: rgba(255, 255, 255, 0.24);
}
</style>
