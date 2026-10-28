<script setup>
import AppIcon from '@/components/AppIcon.vue'

defineProps({
  portfolio: {
    type: Object,
    required: true,
  },
  // стоимость портфеля: баланс + позиции
  value: {
    type: String,
    default: '—',
  },
  // изменение стоимости, например '+3,1%'
  change: {
    type: String,
    default: '',
  },
  isUp: {
    type: Boolean,
    default: true,
  },
  positionsCount: {
    type: [Number, String],
    default: '—',
  },
  profit: {
    type: String,
    default: '—',
  },
  // владелец — показывается только суперпользователю
  owner: {
    type: String,
    default: null,
  },
})

defineEmits(['open-cover', 'edit', 'delete'])
</script>

<template>
  <article class="card portfolio-card">
    <button
      class="portfolio-cover"
      type="button"
      :aria-label="`Открыть обложку «${portfolio.name}»`"
      @click="$emit('open-cover')"
    >
      <img v-if="portfolio.cover_image" :src="portfolio.cover_image" alt="" />
      <span v-else class="portfolio-cover-label">обложка</span>
    </button>

    <div class="portfolio-card-body">
      <h2 class="portfolio-card-title">
        <router-link :to="{ name: 'portfolio', params: { id: portfolio.id } }">
          {{ portfolio.name }}
        </router-link>
        <span
          v-if="change"
          class="price-change price-change-pill"
          :class="isUp ? 'is-up' : 'is-down'"
        >
          {{ change }}
        </span>
      </h2>
      <div>
        <div class="meta-label">Стоимость</div>
        <div class="portfolio-card-value">{{ value }}</div>
      </div>
      <div class="portfolio-card-meta">
        <div>
          <div class="meta-label">Баланс</div>
          <div class="num">{{ portfolio.balance }} ₽</div>
        </div>
        <div>
          <div class="meta-label">Позиций</div>
          <div class="num">{{ positionsCount }}</div>
        </div>
        <div>
          <div class="meta-label">П/У</div>
          <div class="num" :class="isUp ? 'text-up' : 'text-down'">{{ profit }}</div>
        </div>
        <div v-if="owner">
          <div class="meta-label">Владелец <span class="admin-only-tag">админ</span></div>
          <div>{{ owner }}</div>
        </div>
      </div>
    </div>

    <div class="portfolio-card-actions">
      <router-link
        :to="{ name: 'portfolio', params: { id: portfolio.id } }"
        class="btn btn-secondary btn-sm"
      >
        Открыть
      </router-link>
      <button class="btn btn-ghost btn-sm" type="button" @click="$emit('edit')">
        <AppIcon name="edit" />
        Изменить
      </button>
      <button class="btn btn-danger btn-sm push-right" type="button" @click="$emit('delete')">
        <AppIcon name="trash" />
        Удалить
      </button>
    </div>
  </article>
</template>

<style scoped>
.portfolio-card {
  overflow: hidden;
}

.portfolio-cover {
  position: relative;
  display: block;
  width: 100%;
  height: 128px;
  padding: 0;
  border: 0;
  border-bottom: 1px solid var(--color-border);
  background: repeating-linear-gradient(135deg, #e8ecf2 0 10px, #dfe4ec 10px 20px);
  cursor: zoom-in;
}

.portfolio-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.portfolio-cover-label {
  position: absolute;
  left: var(--space-3);
  bottom: var(--space-2);
  padding: 1px 6px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.85);
  font-size: 11px;
  color: var(--color-text-muted);
}

.portfolio-card-body {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.portfolio-card-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-2);
}

.portfolio-card-value {
  font-size: var(--font-size-xl);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.portfolio-card-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-2);
  font-size: var(--font-size-sm);
}

.portfolio-card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: auto;
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--color-border);
}

.push-right {
  margin-left: auto;
}
</style>
