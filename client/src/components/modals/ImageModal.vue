<script setup>
import { computed, ref } from "vue";
import AppIcon from "@/components/AppIcon.vue";

const props = defineProps({
  src: {
    type: String,
    default: "",
  },
  caption: {
    type: String,
    default: "",
  },
  images: {
    type: Array,
    default: () => [],
  },
  initialIndex: {
    type: Number,
    default: 0,
  },
});

const currentIndex = ref(props.initialIndex);
const currentSrc = computed(() =>
  props.images.length ? props.images[currentIndex.value].image : props.src,
);

function showPrevious() {
  currentIndex.value =
    (currentIndex.value - 1 + props.images.length) % props.images.length;
}

function showNext() {
  currentIndex.value = (currentIndex.value + 1) % props.images.length;
}

defineEmits(["close"]);
</script>

<template>
  <Teleport to="body">
    <div class="image-modal-backdrop" @click.self="$emit('close')">
      <button class="image-modal-close" type="button" @click="$emit('close')">
        <AppIcon name="close" />
      </button>
      <button
        v-if="images.length > 1"
        class="image-modal-nav image-modal-previous"
        type="button"
        @click.stop="showPrevious"
      >
        ‹
      </button>
      <div class="image-modal">
        <img
          v-if="currentSrc"
          class="image-modal-img"
          :src="currentSrc"
          :alt="caption"
        />
        <div v-else class="image-modal-img">изображение в полном размере</div>
        <div class="image-modal-caption">
          <span v-if="caption">{{ caption }}</span>
          <span v-if="images.length > 1"
            >{{ currentIndex + 1 }} / {{ images.length }}</span
          >
          <a v-if="currentSrc" :href="currentSrc" target="_blank" rel="noopener"
            >Открыть оригинал</a
          >
        </div>
      </div>
      <button
        v-if="images.length > 1"
        class="image-modal-nav image-modal-next"
        type="button"
        @click.stop="showNext"
      >
        ›
      </button>
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
  background: repeating-linear-gradient(
    135deg,
    #3a4559 0 14px,
    #333d50 14px 28px
  );
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

.image-modal-nav {
  position: absolute;
  top: 50%;
  z-index: 1;
  width: 48px;
  height: 48px;
  padding: 0 0 5px;
  transform: translateY(-50%);
  border: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
  font-size: 40px;
  line-height: 1;
  cursor: pointer;
}

.image-modal-nav:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-modal-previous {
  left: var(--space-4);
}

.image-modal-next {
  right: var(--space-4);
}

@media (max-width: 600px) {
  .image-modal-nav {
    width: 40px;
    height: 40px;
    font-size: 34px;
  }

  .image-modal-previous {
    left: var(--space-2);
  }

  .image-modal-next {
    right: var(--space-2);
  }
}
</style>
