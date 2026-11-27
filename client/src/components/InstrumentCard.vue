<script setup>
import InstrumentLogo from "@/components/InstrumentLogo.vue";
import { formatPrice, formatSigned } from "@/utils/format";

defineProps({
  instrument: { type: Object, required: true },
  rank: { type: Number, default: null },
});
</script>

<template>
  <router-link
    :to="{ name: 'instrument', params: { id: instrument.id } }"
    class="instrument-card"
  >
    <span v-if="rank" class="instrument-card-rank">{{ rank }}</span>
    <InstrumentLogo
      :ticker="instrument.ticker"
      :logo="instrument.logo"
      :zoomable="false"
    />
    <span class="cell-instrument-text">
      <span class="cell-instrument-ticker">{{ instrument.ticker }}</span>
      <span class="cell-instrument-name">{{ instrument.name }}</span>
    </span>
    <span class="instrument-card-price">
      <span class="instrument-card-value">
        {{ formatPrice(instrument.current_price) }} ₽
      </span>
      <span
        class="price-change"
        :class="instrument.change_percent >= 0 ? 'is-up' : 'is-down'"
      >
        {{ formatSigned(instrument.change_percent) }}%
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

.instrument-card-price {
  margin-left: auto;
  text-align: right;
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.instrument-card-value {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
</style>
