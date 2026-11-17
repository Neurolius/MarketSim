<script setup>
import { ref, onBeforeMount, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import HeaderNavbar from "@/components/HeaderNavbar.vue";
import InstrumentLogo from "@/components/InstrumentLogo.vue";
import PriceChart from "@/components/PriceChart.vue";
import BuyForm from "@/components/BuyForm.vue";
import ExportButtons from "@/components/ExportButtons.vue";
import ImageModal from "@/components/modals/ImageModal.vue";
import SellModal from "@/components/modals/SellModal.vue";
import axios from "axios";

import { mapInstrument } from "@/utils/InstrumentsMapper";
import {
  formatPrice,
  formatQuantity,
  formatSigned,
  formatDate,
  toDateInputValue,
} from "@/utils/format";
import { buildChart } from "@/utils/chart";
import { toFormData, errorText } from "@/utils/api";

const isLogoModalOpen = ref(false);
const sellPosition = ref(null);
const portfolioList = ref([]);
const instrumentTrade = ref(null);
const route = useRoute();
const router = useRouter();
const positionList = ref([]);
const priceHistoryList = ref([]);

onBeforeMount(async () => {
  const id = route.params.id;
  const [instrument, type, portfolios, history, positions] = await Promise.all([
    axios.get(`/api/instrument/${id}/`, {
      params: { period: "day" },
    }),
    axios.get("/api/instrumenttype/"),
    axios.get("/api/portfolio/"),
    axios.get("/api/pricehistory/", { params: { instrument: id } }),
    axios.get("/api/position/", { params: { instrument: id } }),
  ]);
  const typesById = Object.fromEntries(type.data.map((t) => [t.id, t]));
  instrumentTrade.value = mapInstrument(instrument.data, typesById);
  portfolioList.value = portfolios.data;
  priceHistoryList.value = history.data;
  positionList.value = positions.data;
});

const positionRows = computed(() => {
  const portfoliosById = Object.fromEntries(
    portfolioList.value.map((p) => [p.id, p]),
  );
  const currentPrice = instrumentTrade.value?.rawPrice ?? 0;
  return positionList.value.map((p) => {
    const quantity = Number(p.quantity);
    const avarage = Number(p.average_price);
    const profit = quantity * (currentPrice - avarage);
    const percent = avarage ? (currentPrice / avarage - 1) * 100 : 0;
    return {
      ...p,
      portfolioName: portfoliosById[p.portfolio]?.name ?? "—",
      quantityText: formatQuantity(quantity),
      averageText: formatPrice(avarage),
      profitText: `${formatSigned(profit)} ₽ (${formatSigned(percent)}%)`,
      isUp: profit >= 0,
    };
  });
});

const historyRows = computed(() =>
  priceHistoryList.value.map((record, i, list) => {
    const price = Number(record.price);
    const older = list[i + 1];
    const percent = older ? (price / Number(older.price) - 1) * 100 : 0;
    return {
      id: record.id,
      date: toDateInputValue(record.timestamp),
      rawPrice: price,
      timestamp: formatDate(record.timestamp),
      price: formatPrice(price),
      change: formatSigned(percent) + "%",
      isUp: percent >= 0,
    };
  }),
);

const historyFilters = ref({
  dateFrom: "",
  dateTo: "",
  priceFrom: "",
  priceTo: "",
});

const filteredHistory = computed(() => {
  const f = historyFilters.value;
  return historyRows.value.filter(
    (r) =>
      (!f.dateFrom || r.date >= f.dateFrom) &&
      (!f.dateTo || r.date <= f.dateTo) &&
      (f.priceFrom === "" || r.rawPrice >= f.priceFrom) &&
      (f.priceTo === "" || r.rawPrice <= f.priceTo),
  );
});

const historyStats = computed(() => {
  const prices = priceHistoryList.value.map((r) => Number(r.price));
  if (!prices.length) return null;
  return {
    avg: prices.reduce((sum, p) => sum + p, 0) / prices.length,
    min: Math.min(...prices),
    max: Math.max(...prices),
  };
});

const chartPeriods = [
  { label: "1Д", days: 1 },
  { label: "1Н", days: 7 },
  { label: "1М", days: 30 },
  { label: "3М", days: 90 },
  { label: "1Г", days: 365 },
  { label: "Всё", days: null },
];
const chartPeriod = ref(chartPeriods[2]);

const chart = computed(() => {
  const days = chartPeriod.value.days;
  const since = days ? Date.now() - days * 24 * 60 * 60 * 1000 : 0;
  const records = priceHistoryList.value
    .filter((r) => new Date(r.timestamp).getTime() >= since)
    .reverse();
  return buildChart(records, 900, 340);
});

const chartChange = computed(() =>
  chart.value ? (chart.value.last / chart.value.first - 1) * 100 : 0,
);

const buyForm = ref(null);
const buyError = ref("");
const sellError = ref("");
const isSubmitting = ref(false);

async function reloadPortfolios() {
  const [portfolios, positions] = await Promise.all([
    axios.get("/api/portfolio/"),
    axios.get("/api/position/", { params: { instrument: route.params.id } }),
  ]);
  positionList.value = positions.data;
  portfolioList.value = portfolios.data;
}

async function createTrade(data) {
  await axios.post(
    "/api/trade/",
    toFormData({ ...data, instrument: instrumentTrade.value.id }),
  );
  await reloadPortfolios();
}

async function onBuy(data) {
  buyError.value = "";
  isSubmitting.value = true;
  try {
    await createTrade({ ...data, order_type: "buy" });
    buyForm.value.reset();
  } catch (e) {
    buyError.value = errorText(e);
  } finally {
    isSubmitting.value = false;
  }
}

function openSell(position) {
  sellError.value = "";
  sellPosition.value = position;
}

async function onSell(data) {
  sellError.value = "";
  isSubmitting.value = true;
  try {
    await createTrade({
      ...data,
      portfolio: sellPosition.value.portfolio,
      order_type: "sell",
    });
    sellPosition.value = null;
  } catch (e) {
    sellError.value = errorText(e);
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <HeaderNavbar />
  <main v-if="instrumentTrade" class="page">
    <nav class="breadcrumbs" aria-label="Навигационная цепочка">
      <router-link :to="{ name: 'instruments' }">Инструменты</router-link>
      <span class="breadcrumbs-sep">/</span>
      <span>{{ instrumentTrade.ticker }}</span>
    </nav>

    <section class="instrument-hero">
      <InstrumentLogo
        :ticker="instrumentTrade.ticker"
        :logo="instrumentTrade.logo"
        :type="instrumentTrade.type"
        large
        @open="isLogoModalOpen = true"
      />
      <div class="instrument-hero-title">
        <h1 class="page-title">
          {{ instrumentTrade.ticker }}
          <span class="instrument-hero-name">· {{ instrumentTrade.name }}</span>
        </h1>
        <div class="inline-row instrument-hero-meta">
          <span class="badge badge-type">{{ instrumentTrade.typeName }}</span>
          <span class="text-muted text-sm"
            >Обновлено {{ instrumentTrade.updated }}</span
          >
        </div>
      </div>
      <div class="instrument-hero-price">
        <span class="instrument-hero-value">{{ instrumentTrade.price }} ₽</span>
        <span
          class="price-change"
          :class="instrumentTrade.isUp ? 'is-up' : 'is-down'"
        >
          {{ instrumentTrade.diff }} ₽ ({{ instrumentTrade.change }}) за день
        </span>
      </div>
    </section>

    <div class="split-main">
      <section class="card">
        <div class="card-header">
          <h2 class="card-title">График цены</h2>
          <div class="segmented" role="group" aria-label="Таймфрейм">
            <button
              v-for="period in chartPeriods"
              :key="period.label"
              class="segmented-btn"
              :class="{ 'is-active': chartPeriod === period }"
              type="button"
              @click="chartPeriod = period"
            >
              {{ period.label }}
            </button>
          </div>
        </div>
        <div class="card-body">
          <PriceChart
            :points="chart?.points ?? ''"
            :width="900"
            :height="340"
            :y-labels="chart?.yLabels ?? []"
            :x-labels="chart?.xLabels ?? []"
            :is-up="chartChange >= 0"
            large
          />
        </div>
        <div v-if="chart" class="chart-meta">
          <div>
            <div class="meta-label">Открытие периода</div>
            <div class="num text-strong">{{ formatPrice(chart?.first) }} ₽</div>
          </div>
          <div>
            <div class="meta-label">Минимум</div>
            <div class="num text-strong">{{ formatPrice(chart?.min) }} ₽</div>
          </div>
          <div>
            <div class="meta-label">Максимум</div>
            <div class="num text-strong">{{ formatPrice(chart?.max) }} ₽</div>
          </div>
          <div>
            <div class="meta-label">Изменение за период</div>
            <div
              class="price-change"
              :class="chartChange >= 0 ? 'is-up' : 'is-down'"
            >
              {{ formatSigned(chartChange) }}%
            </div>
          </div>
        </div>
      </section>

      <BuyForm
        ref="buyForm"
        :instrument="instrumentTrade"
        :portfolios="portfolioList"
        :error="buyError"
        :loading="isSubmitting"
        @submit="onBuy"
      />
    </div>

    <div class="grid-2">
      <section class="card">
        <div class="table-toolbar">
          <h2 class="table-toolbar-title">
            Ваши позиции по {{ instrumentTrade.ticker }}
          </h2>
        </div>
        <div class="table-wrap">
          <table class="data-table data-table-compact">
            <thead>
              <tr>
                <th>Портфель</th>
                <th class="col-num">Кол-во</th>
                <th class="col-num">Ср. цена</th>
                <th class="col-num">П/У</th>
                <th class="col-actions"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!positionRows.length">
                <td colspan="5" class="text-muted">
                  В ваших портфелях нет этого инструмента
                </td>
              </tr>
              <tr v-for="position in positionRows" :key="position.id">
                <td>
                  <router-link
                    :to="{
                      name: 'portfolio',
                      params: { id: position.portfolio },
                    }"
                  >
                    {{ position.portfolioName }}
                  </router-link>
                </td>
                <td class="col-num num">{{ position.quantityText }}</td>
                <td class="col-num num">{{ position.averageText }} ₽</td>
                <td class="col-num">
                  <span
                    class="price-change"
                    :class="position.isUp ? 'is-up' : 'is-down'"
                  >
                    {{ position.profitText }}
                  </span>
                </td>
                <td class="col-actions">
                  <button
                    class="btn btn-sell btn-sm"
                    type="button"
                    @click="openSell(position)"
                  >
                    Продать
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="card">
        <div class="table-toolbar">
          <h2 class="table-toolbar-title">
            История цен
            <span class="table-count">{{ filteredHistory.length }}</span>
          </h2>
          <div class="export-actions">
            <ExportButtons />
          </div>
        </div>
        <div class="table-wrap">
          <table class="data-table data-table-compact">
            <thead>
              <tr>
                <th>Дата и время</th>
                <th class="col-num">Цена</th>
                <th class="col-num">Изменение</th>
              </tr>
              <tr class="filter-row">
                <th>
                  <div class="filter-range">
                    <input
                      v-model="historyFilters.dateFrom"
                      class="filter-input"
                      type="date"
                      aria-label="С даты"
                    />
                    <input
                      v-model="historyFilters.dateTo"
                      class="filter-input"
                      type="date"
                      aria-label="По дату"
                    />
                  </div>
                </th>
                <th>
                  <div class="filter-range">
                    <input
                      v-model.number="historyFilters.priceFrom"
                      class="filter-input"
                      type="number"
                      placeholder="от"
                      aria-label="Цена от"
                    />
                    <input
                      v-model.number="historyFilters.priceTo"
                      class="filter-input"
                      type="number"
                      placeholder="до"
                      aria-label="Цена до"
                    />
                  </div>
                </th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in filteredHistory" :key="record.id">
                <td class="num">{{ record.timestamp }}</td>
                <td class="col-num num">{{ record.price }} ₽</td>
                <td class="col-num">
                  <span
                    class="price-change"
                    :class="record.isUp ? 'is-up' : 'is-down'"
                  >
                    {{ record.change }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="table-footer">
          <span v-if="historyStats"
            >Среднее: {{ formatPrice(historyStats.avg) }} ₽ · мин
            {{ formatPrice(historyStats.min) }} ₽ · макс
            {{ formatPrice(historyStats.max) }} ₽</span
          >
        </div>
      </section>
    </div>
  </main>

  <ImageModal
    v-if="isLogoModalOpen"
    :src="instrumentTrade.logo ?? ''"
    :caption="`Логотип ${instrumentTrade.ticker}`"
    @close="isLogoModalOpen = false"
  />
  <SellModal
    v-if="sellPosition"
    :position="sellPosition"
    :portfolio-name="sellPosition.portfolioName"
    :error="sellError"
    :loading="isSubmitting"
    @close="sellPosition = null"
    @submit="onSell"
  />
</template>

<style scoped>
.instrument-hero {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-4);
}

.instrument-hero-title {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.instrument-hero-name {
  color: var(--color-text-muted);
  font-weight: 500;
}

.instrument-hero-meta {
  gap: var(--space-2);
}

.instrument-hero-price {
  margin-left: auto;
  text-align: right;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.instrument-hero-value {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  line-height: 1.1;
}

.chart-meta {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--color-border);
}

@media (max-width: 760px) {
  .instrument-hero-price {
    margin-left: 0;
    text-align: left;
  }

  .instrument-hero-value {
    font-size: var(--font-size-2xl);
  }

  .chart-meta {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
