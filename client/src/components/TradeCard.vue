<script setup>
import InstrumentLogo from '@/components/InstrumentLogo.vue'

defineProps({
  trade: {
    type: Object,
    required: true,
  },
  portfolio: {
    type: Object,
    default: null,
  },
})

const orderTypeLabels = { buy: 'Покупка', sell: 'Продажа' }
const executionTypeLabels = { market: 'Рыночная', limit: 'Лимитная' }
const statusLabels = { pending: 'Ожидает', executed: 'Исполнена', cancelled: 'Отменена' }
</script>

<template>
  <article class="trade-card">
    <div class="trade-card-head">
      <span class="badge" :class="`badge-${trade.order_type}`">
        {{ orderTypeLabels[trade.order_type] }}
      </span>
      <span class="badge" :class="`badge-${trade.status}`">{{ statusLabels[trade.status] }}</span>
      <time class="trade-card-date" :datetime="trade.created_at">
        {{ new Date(trade.created_at).toLocaleString() }}
      </time>
    </div>
    <div class="trade-card-main">
      <InstrumentLogo
        :ticker="trade.instrument_info.ticker"
        :logo="trade.instrument_info.logo"
        :zoomable="false"
      />
      <div class="trade-card-instrument">
        <span class="trade-card-ticker">{{ trade.instrument_info.ticker }}</span>
        <span class="trade-card-name">{{ trade.instrument_info.name }}</span>
      </div>
      <div class="trade-card-amount">
        <span class="trade-card-qty">
          {{ trade.quantity }} ×
          <template v-if="trade.execution_type === 'limit'">лимит {{ trade.price }} ₽</template>
          <template v-else>{{ trade.execution_price ?? trade.price }} ₽</template>
        </span>
        <!-- сумма сделки: количество × цена -->
        <span class="trade-card-total">—</span>
      </div>
    </div>
    <div class="trade-card-foot">
      {{ portfolio?.name }} · {{ executionTypeLabels[trade.execution_type] }}
    </div>
  </article>
</template>

<style scoped>
.trade-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.trade-card:hover {
  border-color: var(--color-border-strong);
}

.trade-card-head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.trade-card-date {
  margin-left: auto;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-variant-numeric: tabular-nums;
}

.trade-card-main {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.trade-card-instrument {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
  min-width: 0;
}

.trade-card-ticker {
  font-weight: 700;
}

.trade-card-name {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.trade-card-amount {
  margin-left: auto;
  text-align: right;
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}

.trade-card-qty {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.trade-card-total {
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.trade-card-foot {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}
</style>
