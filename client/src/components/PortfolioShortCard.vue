<script setup>
// компактная карточка портфеля для дашборда — по образцу TradeCard
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
})
</script>

<template>
  <router-link
    :to="{ name: 'portfolio', params: { id: portfolio.id } }"
    class="portfolio-short-card"
  >
    <div class="portfolio-short-card-head">
      <span class="badge badge-exec">Позиций: {{ positionsCount }}</span>
      <span
        v-if="change"
        class="price-change price-change-pill"
        :class="isUp ? 'is-up' : 'is-down'"
      >
        {{ change }}
      </span>
      <span class="portfolio-short-card-open">Открыть →</span>
    </div>
    <div class="portfolio-short-card-main">
      <span class="portfolio-short-card-cover">
        <img v-if="portfolio.cover_image" :src="portfolio.cover_image" alt="" />
        <template v-else>{{ portfolio.name?.slice(0, 2).toUpperCase() }}</template>
      </span>
      <div class="portfolio-short-card-info">
        <span class="portfolio-short-card-name">{{ portfolio.name }}</span>
        <span class="portfolio-short-card-balance">Свободно: {{ portfolio.balance }} ₽</span>
      </div>
      <div class="portfolio-short-card-amount">
        <span class="portfolio-short-card-label">Стоимость</span>
        <span class="portfolio-short-card-value">{{ value }}</span>
      </div>
    </div>
    <div class="portfolio-short-card-foot">
      П/У: <span :class="isUp ? 'text-up' : 'text-down'">{{ profit }}</span>
    </div>
  </router-link>
</template>

<style scoped>
.portfolio-short-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: inherit !important;
  text-decoration: none !important;
}

.portfolio-short-card:hover {
  border-color: var(--color-border-strong);
}

.portfolio-short-card-head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.portfolio-short-card-open {
  margin-left: auto;
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--color-accent);
}

.portfolio-short-card-main {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.portfolio-short-card-cover {
  width: 32px;
  height: 32px;
  flex: none;
  overflow: hidden;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: repeating-linear-gradient(135deg, #e8ecf2 0 6px, #dfe4ec 6px 12px);
  display: grid;
  place-items: center;
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-muted);
}

.portfolio-short-card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.portfolio-short-card-info {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
  min-width: 0;
}

.portfolio-short-card-name {
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.portfolio-short-card-balance {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.portfolio-short-card-amount {
  margin-left: auto;
  text-align: right;
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}

.portfolio-short-card-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.portfolio-short-card-value {
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.portfolio-short-card-foot {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.portfolio-short-card-foot span {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
</style>
