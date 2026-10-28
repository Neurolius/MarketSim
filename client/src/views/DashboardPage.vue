<script setup>
import HeaderNavbar from '@/components/HeaderNavbar.vue'
import TradeCard from '@/components/TradeCard.vue'
import InstrumentCard from '@/components/InstrumentCard.vue'
import PriceChart from '@/components/PriceChart.vue'
import EmptyState from '@/components/EmptyState.vue'
import AppIcon from '@/components/AppIcon.vue'
import axios from 'axios'
import { computed, onBeforeMount, ref } from 'vue'

const portfoliosList = ref([])
const tradeList = ref([])

const portfoliosBalance = computed(() =>
  portfoliosList.value.reduce((total, p) => total + Number(p.balance), 0),
)

const portfoliosById = computed(() =>
  Object.fromEntries(portfoliosList.value.map((p) => [p.id, p])),
)

const lastTrades = computed(() =>
  [...tradeList.value].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 10),
)

onBeforeMount(async () => {
  const [portfolios, trades] = await Promise.all([
    axios.get('/api/portfolio/'),
    axios.get('/api/trade/'),
  ])
  portfoliosList.value = portfolios.data
  tradeList.value = trades.data
})

// моковые данные для верстки — заменить на данные из API
const portfolioColors = ['#1d4ed8', '#b7791f', '#067a45', '#7c3aed', '#0e7490']
const chartPoints =
  '0,160 40,150 80,156 120,132 160,140 200,118 240,124 280,102 320,110 360,88 400,95 440,76 480,82 520,60 560,66 600,44'
const bestInstruments = [
  { id: 1, ticker: 'ETH', name: 'Ethereum', type: 'crypto', current_price: '312 450', change: '+6,42%', isUp: true, spark: '0,22 10,20 20,23 30,16 40,17 50,10 60,12 72,4' },
  { id: 2, ticker: 'YDEX', name: 'Яндекс', type: 'stock', current_price: '4 186,50', change: '+4,18%', isUp: true, spark: '0,20 10,21 20,17 30,18 40,12 50,13 60,8 72,6' },
  { id: 3, ticker: 'SBER', name: 'Сбербанк', type: 'stock', current_price: '312,45', change: '+2,07%', isUp: true, spark: '0,18 10,19 20,15 30,16 40,14 50,11 60,12 72,8' },
  { id: 4, ticker: 'BTC', name: 'Bitcoin', type: 'crypto', current_price: '8 945 200', change: '+1,35%', isUp: true, spark: '0,16 10,18 20,14 30,15 40,13 50,14 60,10 72,11' },
  { id: 5, ticker: 'EUR/RUB', name: 'Евро', type: 'currency', current_price: '94,12', change: '+0,48%', isUp: true, spark: '0,15 10,16 20,14 30,15 40,13 50,13 60,12 72,11' },
  { id: 6, ticker: 'GAZP', name: 'Газпром', type: 'stock', current_price: '128,90', change: '−0,92%', isUp: false, spark: '0,8 10,9 20,12 30,11 40,15 50,14 60,18 72,20' },
]
</script>

<template>
  <HeaderNavbar />
  <main class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Дашборд</h1>
        <p class="page-subtitle">Сводка по всем портфелям</p>
      </div>
      <div class="page-actions">
        <router-link :to="{ name: 'instruments' }" class="btn btn-secondary">
          Все инструменты
        </router-link>
        <router-link :to="{ name: 'instruments' }" class="btn btn-primary">
          <AppIcon name="plus" />
          Новая сделка
        </router-link>
      </div>
    </div>

    <div class="dashboard-grid">
      <!-- Стоимость портфелей -->
      <section class="card">
        <div class="card-header">
          <h2 class="card-title">Стоимость портфелей</h2>
          <div class="segmented" role="group" aria-label="Период">
            <button class="segmented-btn" type="button">1Д</button>
            <button class="segmented-btn" type="button">1Н</button>
            <button class="segmented-btn is-active" type="button">1М</button>
            <button class="segmented-btn" type="button">1Г</button>
            <button class="segmented-btn" type="button">Всё</button>
          </div>
        </div>
        <div class="card-body stack">
          <div>
            <div class="value-row">
              <span class="value-big">{{ portfoliosBalance }} ₽</span>
              <span class="price-change price-change-pill is-up">+28 112,05 ₽ (+2,30%)</span>
            </div>
            <p class="text-muted text-sm value-hint">
              Свободные средства: {{ portfoliosBalance }} ₽ · в позициях: — ₽
            </p>
          </div>
          <PriceChart
            :points="chartPoints"
            :y-labels="['1,26 млн', '1,24 млн', '1,22 млн', '1,20 млн']"
            :x-labels="['21 сен', '28 сен', '5 окт', '12 окт', '21 окт']"
          />
        </div>
        <div class="portfolio-mini-list">
          <div
            v-for="(portfolio, index) in portfoliosList"
            :key="portfolio.id"
            class="portfolio-mini-row"
          >
            <router-link :to="{ name: 'portfolio', params: { id: portfolio.id } }">
              <span
                class="dot"
                :style="{ background: portfolioColors[index % portfolioColors.length] }"
              ></span>
              {{ portfolio.name }}
            </router-link>
            <span class="num">{{ portfolio.balance }} ₽</span>
          </div>
        </div>
      </section>

      <!-- Последние сделки -->
      <section class="card">
        <div class="card-header">
          <h2 class="card-title">Последние сделки</h2>
          <router-link :to="{ name: 'profile' }" class="text-sm">Вся история</router-link>
        </div>
        <div v-if="lastTrades.length" class="trade-list">
          <TradeCard
            v-for="trade in lastTrades"
            :key="trade.id"
            :trade="trade"
            :portfolio="portfoliosById[trade.portfolio]"
          />
        </div>
        <EmptyState
          v-else
          icon="chart"
          title="Сделок ещё не было"
          text="Купите инструмент из каталога — сделка появится здесь."
        >
          <router-link :to="{ name: 'instruments' }" class="btn btn-secondary">
            Открыть каталог
          </router-link>
        </EmptyState>
      </section>

      <!-- Лидеры роста -->
      <section class="card">
        <div class="card-header">
          <h2 class="card-title">Лидеры роста</h2>
          <div class="segmented" role="group" aria-label="Период">
            <button class="segmented-btn is-active" type="button">День</button>
            <button class="segmented-btn" type="button">Неделя</button>
          </div>
        </div>
        <div class="instrument-list">
          <InstrumentCard
            v-for="(instrument, index) in bestInstruments"
            :key="instrument.id"
            :instrument="instrument"
            :rank="index + 1"
            :change="instrument.change"
            :is-up="instrument.isUp"
            :spark-points="instrument.spark"
          />
        </div>
        <div class="card-footer">
          <span class="text-muted">По изменению цены за день</span>
          <router-link :to="{ name: 'instruments' }">Каталог →</router-link>
        </div>
      </section>
    </div>
  </main>
</template>

<style scoped>
.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(0, 1fr) minmax(0, 1fr);
  gap: var(--space-5);
  align-items: stretch;
}

.value-row {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--space-3);
}

.value-big {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  line-height: 1.1;
}

.value-hint {
  margin-top: var(--space-1);
}

.portfolio-mini-list {
  display: flex;
  flex-direction: column;
  border-top: 1px solid var(--color-border);
}

.portfolio-mini-row {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-5);
  border-bottom: 1px solid var(--color-border);
  font-size: var(--font-size-sm);
}

.portfolio-mini-row:last-child {
  border-bottom: 0;
}

.portfolio-mini-row a {
  color: var(--color-text);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 6px;
}

.trade-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-4);
  max-height: 520px;
  overflow-y: auto;
}

.instrument-list {
  display: flex;
  flex-direction: column;
}

@media (max-width: 1100px) {
  .dashboard-grid {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  }

  .dashboard-grid > :first-child {
    grid-column: 1 / -1;
  }
}

@media (max-width: 760px) {
  .dashboard-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .value-big {
    font-size: var(--font-size-2xl);
  }
}
</style>
