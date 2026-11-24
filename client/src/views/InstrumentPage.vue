<script setup>
import { ref, onBeforeMount, computed, watch } from "vue";
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
import { toFormData, errorText } from "@/utils/requestFormatter";
import { byId, listResults } from "@/utils/lists";
import { calcPosition } from "@/utils/positions";
import PaginationControls from "@/components/PaginationControls.vue";

const isLogoModalOpen = ref(false);
const sellPosition = ref(null);
const portfolioList = ref([]);
const instrumentTrade = ref(null);
const route = useRoute();
const router = useRouter();
const positionList = ref([]);
const priceHistoryList = ref([]);
const chartHistoryList = ref([]);
const historyStats = ref(null);
const positionCount = ref(0);
const historyCount = ref(0);
const pageSize = 20;
const positionPage = ref(1);
const historyPage = ref(1);

const historyFilters = ref({
  dateFrom: "",
  dateTo: "",
  priceFrom: "",
  priceTo: "",
});

async function loadInstrument() {
  const id = route.params.id;
  const [instrument, types, portfolios, chartHistory, stats] = await Promise.all([
    axios.get(`/api/instrument/${id}/`, { params: { period: "day" } }),
    axios.get("/api/instrumenttype/", { params: { page_size: 100 } }),
    axios.get("/api/portfolio/", { params: { page_size: 100 } }),
    axios.get("/api/pricehistory/", {
      params: { instrument: id, page: 1, page_size: 100 },
    }),
    axios.get("/api/pricehistory/stats/", { params: { instrument: id } }),
  ]);
  const instrumentTypes = listResults(types.data);
  instrumentTrade.value = mapInstrument(instrument.data, byId(instrumentTypes));
  portfolioList.value = listResults(portfolios.data);
  chartHistoryList.value = listResults(chartHistory.data);
  historyStats.value = stats.data.count ? stats.data : null;
  await Promise.all([loadPositions(), loadHistory()]);
}

onBeforeMount(loadInstrument);

async function loadPositions() {
  const { data } = await axios.get("/api/position/", {
    params: {
      instrument: route.params.id,
      page: positionPage.value,
      page_size: pageSize,
    },
  });
  positionList.value = listResults(data);
  positionCount.value = data.count ?? positionList.value.length;
}

function historyFilterParams() {
  const params = { instrument: route.params.id };
  if (historyFilters.value.dateFrom) {
    params.date_from = historyFilters.value.dateFrom;
  }
  if (historyFilters.value.dateTo) {
    params.date_to = historyFilters.value.dateTo;
  }
  if (historyFilters.value.priceFrom !== "") {
    params.price_from = historyFilters.value.priceFrom;
  }
  if (historyFilters.value.priceTo !== "") {
    params.price_to = historyFilters.value.priceTo;
  }
  return params;
}

const historyExportParams = computed(historyFilterParams);

async function loadHistory() {
  const params = {
    ...historyFilterParams(),
    page: historyPage.value,
    page_size: pageSize,
  };

  const { data } = await axios.get("/api/pricehistory/", { params });
  priceHistoryList.value = listResults(data);
  historyCount.value = data.count ?? priceHistoryList.value.length;
}

const visiblePositions = computed(() => positionRows.value);
const visibleHistory = computed(() => historyRows.value);

const positionRows = computed(() => {
  const portfoliosById = byId(portfolioList.value);
  return positionList.value.map((p) => {
    const c = calcPosition(p);
    return {
      ...p,
      portfolioName: portfoliosById[p.portfolio]?.name ?? "—",
      quantityText: formatQuantity(c.quantity),
      averageText: formatPrice(c.average),
      profitText: `${formatSigned(c.profit)} ₽ (${formatSigned(c.percent)}%)`,
      isUp: c.profit >= 0,
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

const chartRecords = computed(() => [...chartHistoryList.value].reverse());

const chartLabels = computed(() =>
  chartRecords.value.map((r) => formatDate(r.timestamp)),
);
const chartPrices = computed(() =>
  chartRecords.value.map((r) => Number(r.price)),
);

const chartStats = computed(() => {
  const stats = historyStats.value;
  if (!stats || stats.count < 2) return null;
  const first = Number(stats.first);
  const last = Number(stats.last);
  return {
    first,
    min: Number(stats.min),
    max: Number(stats.max),
    change: first ? (last / first - 1) * 100 : 0,
  };
});

const buyForm = ref(null);
const buyError = ref("");
const sellError = ref("");
const isSubmitting = ref(false);

async function reloadPortfolios() {
  const { data } = await axios.get("/api/portfolio/", {
    params: { page_size: 100 },
  });
  portfolioList.value = listResults(data);
  await loadPositions();
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
watch(
  historyFilters,
  () => {
    if (historyPage.value !== 1) historyPage.value = 1;
    else loadHistory();
  },
  { deep: true },
);

watch(historyPage, loadHistory);
watch(positionPage, loadPositions);
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
        </div>
        <div class="card-body">
          <PriceChart
            :labels="chartLabels"
            :prices="chartPrices"
            :is-up="(chartStats?.change ?? 0) >= 0"
            large
          />
        </div>
        <div v-if="chartStats" class="chart-meta">
          <div>
            <div class="meta-label">Начальная цена</div>
            <div class="num text-strong">
              {{ formatPrice(chartStats.first) }} ₽
            </div>
          </div>
          <div>
            <div class="meta-label">Минимум</div>
            <div class="num text-strong">
              {{ formatPrice(chartStats.min) }} ₽
            </div>
          </div>
          <div>
            <div class="meta-label">Максимум</div>
            <div class="num text-strong">
              {{ formatPrice(chartStats.max) }} ₽
            </div>
          </div>
          <div>
            <div class="meta-label">Изменения за все время</div>
            <div
              class="price-change"
              :class="chartStats.change >= 0 ? 'is-up' : 'is-down'"
            >
              {{ formatSigned(chartStats.change) }}%
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
              <tr v-if="!positionCount">
                <td colspan="5" class="text-muted">
                  В ваших портфелях нет этого инструмента
                </td>
              </tr>
              <tr v-for="position in visiblePositions" :key="position.id">
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
        <PaginationControls
          v-if="positionCount"
          v-model:page="positionPage"
          :count="positionCount"
          :page-size="pageSize"
        />
      </section>

      <section class="card">
        <div class="table-toolbar">
          <h2 class="table-toolbar-title">
            История цен
            <span class="table-count">{{ historyCount }}</span>
          </h2>
          <div class="export-actions">
            <ExportButtons
              url="/api/pricehistory/export/"
              :params="historyExportParams"
            />
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
              <tr v-for="record in visibleHistory" :key="record.id">
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
        <PaginationControls
          v-if="historyCount"
          v-model:page="historyPage"
          :count="historyCount"
          :page-size="pageSize"
        />
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
