<script setup>
import { computed } from 'vue'

const props = defineProps({
  // точки линии в координатах width×height, например '0,160 40,150 …'
  points: {
    type: String,
    default: '',
  },
  width: {
    type: Number,
    default: 600,
  },
  height: {
    type: Number,
    default: 216,
  },
  yLabels: {
    type: Array,
    default: () => [],
  },
  xLabels: {
    type: Array,
    default: () => [],
  },
  isUp: {
    type: Boolean,
    default: true,
  },
  large: {
    type: Boolean,
    default: false,
  },
})

const top = 20
const baseline = computed(() => props.height - 22)

const gridLines = computed(() => {
  const count = Math.max(props.yLabels.length, 2)
  const step = (baseline.value - top) / (count - 1)
  return Array.from({ length: count }, (_, i) => top + i * step)
})

const areaPath = computed(() => {
  if (!props.points) return ''
  const line = props.points.trim().split(/\s+/).join(' L')
  return `M${line} L${props.width},${baseline.value} L0,${baseline.value} Z`
})
</script>

<template>
  <div class="chart-box" :class="{ 'chart-box-lg': large }">
    <div v-if="!points" class="chart-placeholder">Нет данных за выбранный период</div>
    <template v-else>
      <svg
        class="chart-svg"
        :viewBox="`0 0 ${width} ${height}`"
        preserveAspectRatio="none"
        aria-hidden="true"
      >
        <g class="chart-grid">
          <line v-for="y in gridLines" :key="y" x1="0" :y1="y" :x2="width" :y2="y" />
        </g>
        <path class="chart-area" :class="{ 'is-down': !isUp }" :d="areaPath" />
        <polyline class="chart-line" :class="{ 'is-down': !isUp }" :points="points" />
      </svg>
      <div v-if="yLabels.length" class="chart-y-labels">
        <span v-for="label in yLabels" :key="label">{{ label }}</span>
      </div>
      <div v-if="xLabels.length" class="chart-x-labels">
        <span v-for="label in xLabels" :key="label">{{ label }}</span>
      </div>
    </template>
  </div>
</template>

<style scoped>
.chart-box {
  position: relative;
  height: 240px;
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.chart-box-lg {
  height: 340px;
}

.chart-svg {
  width: 100%;
  height: 100%;
  display: block;
  overflow: visible;
}

.chart-line {
  fill: none;
  stroke: var(--color-up);
  stroke-width: 2;
  vector-effect: non-scaling-stroke;
}

.chart-line.is-down {
  stroke: var(--color-down);
}

.chart-area {
  fill: var(--color-up);
  opacity: 0.08;
}

.chart-area.is-down {
  fill: var(--color-down);
}

.chart-grid line {
  stroke: var(--color-border);
  stroke-width: 1;
  vector-effect: non-scaling-stroke;
}

.chart-y-labels {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-left: var(--space-2);
  background: linear-gradient(90deg, transparent, var(--color-surface) 30%);
  font-size: 11px;
  color: var(--color-text-muted);
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.chart-x-labels {
  position: absolute;
  left: 0;
  right: 64px;
  bottom: 0;
  height: 20px;
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--color-text-muted);
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
