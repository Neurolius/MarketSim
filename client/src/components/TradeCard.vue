<script setup>
const props = defineProps({
  trade: {
    type: Object,
    required: true,
  },
  portfolio: {
    type: Object,
    required: true,
  },
});
</script>

<template>
  <div class="card">
    <div class="header">Карточка сделки</div>
    <div>Портфель: {{ portfolio.name }}</div>
    <div>Инструмент: {{ trade.instrument_info.name }}</div>
    <div>Тикер: {{ trade.instrument_info.ticker }}</div>
    <div>Тип сделки: {{ trade.order_type }}</div>
    <div>Тип исполнения: {{ trade.execution_type }}</div>
    <div>Количество: {{ trade.quantity }}</div>
    <div>Цена выполнения: {{ trade.execution_price }}</div>
  </div>
</template>

<style scoped>
.card {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 16px;
  margin: 8px;
  cursor: pointer;
}

.header {
  text-align: center;
  font-size: 25px;
}

.card:hover {
  background-color: #f5f5f5;
}
</style>
