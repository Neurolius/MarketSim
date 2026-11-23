<script setup>
import { computed } from "vue";

const props = defineProps({
  page: { type: Number, required: true },
  count: { type: Number, required: true },
  pageSize: { type: Number, default: 20 },
});

const emit = defineEmits(["update:page"]);

const totalPages = computed(() =>
  Math.max(1, Math.ceil(props.count / props.pageSize)),
);
</script>

<template>
  <nav
    v-if="totalPages > 1"
    class="pagination-nav"
    aria-label="Страницы списка"
  >
    <button
      class="btn btn-secondary btn-sm"
      type="button"
      :disabled="page <= 1"
      @click="emit('update:page', page - 1)"
    >
      Назад
    </button>

    <span>Страница {{ page }} из {{ totalPages }} (всего: {{ count }})</span>

    <button
      class="btn btn-secondary btn-sm"
      type="button"
      :disabled="page >= totalPages"
      @click="emit('update:page', page + 1)"
    >
      Вперёд
    </button>
  </nav>
</template>

<style scoped>
.pagination-nav {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) 0;
}
</style>
