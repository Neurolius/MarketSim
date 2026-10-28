<script setup>
import InstrumentLogo from '@/components/InstrumentLogo.vue'

defineProps({
  instrument: {
    type: Object,
    required: true,
  },
  rank: {
    type: Number,
    default: null,
  },
  // изменение цены за период, например '+6,42%'
  change: {
    type: String,
    default: '',
  },
  isUp: {
    type: Boolean,
    default: true,
  },
  // точки мини-графика в координатах 72×28, например '0,22 10,20 20,23 …'
  sparkPoints: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <router-link :to="{ name: 'instrument', params: { id: instrument.id } }" class="instrument-card">
    <span v-if="rank" class="instrument-card-rank">{{ rank }}</span>
    <InstrumentLogo
      :ticker="instrument.ticker"
      :logo="instrument.logo"
      :type="instrument.type"
      :zoomable="false"
    />
    <span class="cell-instrument-text">
      <span class="cell-instrument-ticker">{{ instrument.ticker }}</span>
      <span class="cell-instrument-name">{{ instrument.name }}</span>
    </span>
    <svg
      v-if="sparkPoints"
      class="instrument-card-spark"
      viewBox="0 0 72 28"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      <polyline class="spark-line" :class="{ 'is-down': !isUp }" :points="sparkPoints" />
    </svg>
    <span class="instrument-card-price">
      <span class="instrument-card-value">{{ instrument.current_price }} ₽</span>
      <span v-if="change" class="price-change" :class="isUp ? 'is-up' : 'is-down'">
        {{ change }}
      </span>
    </span>
  </router-link>
</template>

<style scoped>
.instrument-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-5);
  border-bottom: 1px solid var(--color-border);
  color: inherit !important;
  text-decoration: none !important;
}

.instrument-card:last-child {
  border-bottom: 0;
}

.instrument-card:hover {
  background: #f8fafd;
}

.instrument-card-rank {
  width: 18px;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-weight: 600;
}

.instrument-card-spark {
  width: 72px;
  height: 28px;
  flex: none;
  margin-left: auto;
}

.spark-line {
  fill: none;
  stroke: var(--color-up);
  stroke-width: 2;
  vector-effect: non-scaling-stroke;
}

.spark-line.is-down {
  stroke: var(--color-down);
}

.instrument-card-price {
  margin-left: auto;
  text-align: right;
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.instrument-card-spark + .instrument-card-price {
  margin-left: 0;
  min-width: 96px;
}

.instrument-card-value {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
</style>
