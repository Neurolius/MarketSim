<script setup>
import { ref, onBeforeMount } from "vue";
import { useRoute } from "vue-router";
import HeaderNavbar from "@/components/HeaderNavbar.vue";
import InstrumentLogo from "@/components/InstrumentLogo.vue";
import PriceChart from "@/components/PriceChart.vue";
import BuyForm from "@/components/BuyForm.vue";
import ExportButtons from "@/components/ExportButtons.vue";
import ImageModal from "@/components/modals/ImageModal.vue";
import SellModal from "@/components/modals/SellModal.vue";
import axios from "axios";

const isLogoModalOpen = ref(false);
const sellPosition = ref(null);
const portfolioList = ref([]);
const instrumentTrade = ref(null);
const route = useRoute();

onBeforeMount(async () => {
  const [instrument, type, portfolios, priceHistory, positions] =
    await Promise.all([
      axios.get(`/api/instrument/${route.params.id}/`),
      axios.get("/api/instrumenttype/"),
      axios.get("/api/portfolio/"),
      axios.get("/api/pricehistory"),
      axios.get("/api/position"),
    ]);
  portfolioList.value = portfolios.data;
  instrumentTrade.value = {
    id: instrument.data.id,
    ticker: instrument.data.ticker,
    name: instrument.data.name,
    type: type.data.filter((i) => i.id == instrument.data.instrument_type).id,
    typeName: type.data.filter((i) => i.id == instrument.data.instrument_type)
      .name,
    current_price: instrument.data.current_price,
    logo: instrument.data.logo,
  };
});

// моковые данные для верстки — заменить на данные из API
// const instrument = {
//   id: 7,
//   ticker: "SBER",
//   name: "Сбербанк",
//   type: "stock",
//   typeName: "Акция",
//   current_price: "312,45",
//   logo: null,
// };

const positions = [
  {
    id: 1,
    portfolio: 1,
    portfolioName: "Основной",
    instrument_info: instrumentTrade,
    quantity: "150",
    average_price: "276,30",
    profit: "+5 422,50 ₽ (+13,08%)",
    isUp: true,
  },
  {
    id: 2,
    portfolio: 3,
    portfolioName: "Валютный",
    instrument_info: instrumentTrade,
    quantity: "10",
    average_price: "318,00",
    profit: "−55,50 ₽ (−1,75%)",
    isUp: false,
  },
];
const priceHistory = [
  {
    id: 1,
    timestamp: "21.10.2026, 14:35",
    price: "312,45",
    change: "+0,42%",
    isUp: true,
  },
  {
    id: 2,
    timestamp: "21.10.2026, 10:00",
    price: "311,14",
    change: "+1,64%",
    isUp: true,
  },
  {
    id: 3,
    timestamp: "20.10.2026, 18:45",
    price: "306,11",
    change: "−0,38%",
    isUp: false,
  },
  {
    id: 4,
    timestamp: "20.10.2026, 10:00",
    price: "307,28",
    change: "+0,91%",
    isUp: true,
  },
];
const chartPoints =
  "0,250 36,240 72,256 108,232 144,238 180,212 216,220 252,196 288,206 324,184 360,198 396,176 432,160 468,170 504,148 540,156 576,130 612,142 648,118 684,124 720,100 756,112 792,86 828,92 864,70 900,62";
</script>

<template>
  <HeaderNavbar />
  <main class="page">
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
          <span class="text-muted text-sm">Обновлено 21.10.2026, 14:35</span>
        </div>
      </div>
      <div class="instrument-hero-price">
        <span class="instrument-hero-value"
          >{{ instrumentTrade.current_price }} ₽</span
        >
        <span class="price-change is-up">+6,34 ₽ (+2,07%) за день</span>
      </div>
    </section>

    <div class="split-main">
      <section class="card">
        <div class="card-header">
          <h2 class="card-title">График цены</h2>
          <div class="segmented" role="group" aria-label="Таймфрейм">
            <button class="segmented-btn" type="button">1Д</button>
            <button class="segmented-btn" type="button">1Н</button>
            <button class="segmented-btn is-active" type="button">1М</button>
            <button class="segmented-btn" type="button">3М</button>
            <button class="segmented-btn" type="button">1Г</button>
            <button class="segmented-btn" type="button">Всё</button>
          </div>
        </div>
        <div class="card-body">
          <PriceChart
            :points="chartPoints"
            :width="900"
            :height="340"
            :y-labels="['320', '310', '300', '290', '280']"
            :x-labels="['21 сен', '28 сен', '5 окт', '12 окт', '21 окт']"
            large
          />
        </div>
        <div class="chart-meta">
          <div>
            <div class="meta-label">Открытие периода</div>
            <div class="num text-strong">284,10 ₽</div>
          </div>
          <div>
            <div class="meta-label">Минимум</div>
            <div class="num text-strong">281,75 ₽</div>
          </div>
          <div>
            <div class="meta-label">Максимум</div>
            <div class="num text-strong">313,20 ₽</div>
          </div>
          <div>
            <div class="meta-label">Изменение за период</div>
            <div class="price-change is-up">+9,98%</div>
          </div>
        </div>
      </section>

      <BuyForm :instrument="instrumentTrade" :portfolios="portfolioList" />
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
              <tr v-for="position in positions" :key="position.id">
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
                <td class="col-num num">{{ position.quantity }}</td>
                <td class="col-num num">{{ position.average_price }} ₽</td>
                <td class="col-num">
                  <span
                    class="price-change"
                    :class="position.isUp ? 'is-up' : 'is-down'"
                  >
                    {{ position.profit }}
                  </span>
                </td>
                <td class="col-actions">
                  <button
                    class="btn btn-sell btn-sm"
                    type="button"
                    @click="sellPosition = position"
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
            История цен <span class="table-count">30 записей</span>
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
                      class="filter-input"
                      type="date"
                      aria-label="С даты"
                    />
                    <input
                      class="filter-input"
                      type="date"
                      aria-label="По дату"
                    />
                  </div>
                </th>
                <th>
                  <div class="filter-range">
                    <input
                      class="filter-input"
                      type="number"
                      placeholder="от"
                      aria-label="Цена от"
                    />
                    <input
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
              <tr v-for="record in priceHistory" :key="record.id">
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
          <span>Среднее: 298,62 ₽ · мин 281,75 ₽ · макс 313,20 ₽</span>
          <a href="#">Показать все</a>
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
    @close="sellPosition = null"
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
