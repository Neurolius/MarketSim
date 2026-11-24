<script setup>
import { ref } from "vue";
import ImageModal from "@/components/modals/ImageModal.vue";

defineProps({
  images: {
    type: Array,
    default: () => [],
  },
  caption: {
    type: String,
    default: "Изображение сделки",
  },
});

const selectedIndex = ref(null);
</script>

<template>
  <div v-if="images.length" class="trade-image-gallery">
    <button
      v-for="(image, index) in images"
      :key="image.id"
      class="trade-image-thumb"
      type="button"
      :aria-label="`Открыть ${caption.toLowerCase()}`"
      @click="selectedIndex = index"
    >
      <img :src="image.image" alt="" />
    </button>
    <ImageModal
      v-if="selectedIndex !== null"
      :images="images"
      :initial-index="selectedIndex"
      :caption="caption"
      @close="selectedIndex = null"
    />
  </div>
</template>

<style scoped>
.trade-image-gallery {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
}

.trade-image-thumb {
  width: 40px;
  height: 40px;
  padding: 0;
  overflow: hidden;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface-alt);
  cursor: zoom-in;
}

.trade-image-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
