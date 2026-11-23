<script setup>
import { computed } from "vue";
import { Line } from "vue-chartjs";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
} from "chart.js";
import { formatPrice } from "@/utils/format";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
);

const props = defineProps({
  labels: { type: Array, default: () => [] },
  prices: { type: Array, default: () => [] },
  isUp: { type: Boolean, default: true },
  large: { type: Boolean, default: false },
});

const lineColor = computed(() => (props.isUp ? "#067a45" : "#c41f28"));
const fillColor = computed(() =>
  props.isUp ? "rgba(6, 122, 69, 0.08)" : "rgba(196, 31, 40, 0.08)",
);

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      data: props.prices,
      borderColor: lineColor.value,
      backgroundColor: fillColor.value,
      fill: true,
      borderWidth: 2,
      pointRadius: 0,
      pointHoverRadius: 4,
      tension: 0.2,
    },
  ],
}));

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: "index", intersect: false },
  plugins: {
    tooltip: {
      callbacks: {
        label: (ctx) => `${formatPrice(ctx.parsed.y)} ₽`,
      },
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { maxTicksLimit: 6 },
    },
    y: {
      position: "right",
      ticks: { callback: (value) => formatPrice(value) },
    },
  },
};
</script>

<template>
  <div class="chart-box" :class="{ 'chart-box-lg': large }">
    <div v-if="prices.length < 2" class="chart-placeholder">
      Нет данных за выбранный период
    </div>
    <Line v-else :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.chart-box {
  position: relative;
  height: 240px;
}

.chart-box-lg {
  height: 340px;
}

.chart-placeholder {
  height: 100%;
  display: grid;
  place-items: center;
  border: 1px dashed var(--color-border-strong);
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}
</style>
