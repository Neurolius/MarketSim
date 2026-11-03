<script setup>
import HeaderNavbar from '@/components/HeaderNavbar.vue'
import TradeCard from '@/components/TradeCard.vue'
import InstrumentCard from '@/components/InstrumentCard.vue'
import PortfolioShortCard from '@/components/PortfolioShortCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import AppIcon from '@/components/AppIcon.vue'
import axios from 'axios'
import { computed, onBeforeMount, ref } from 'vue'

const portfoliosList = ref([])
const tradeList = ref([])
const positionList = ref([])

const portfoliosBalance = computed(() =>
  portfoliosList.value.reduce((total, p) => total + Number(p.balance), 0),
)

const portfoliosById = computed(() =>
  Object.fromEntries(portfoliosList.value.map((p) => [p.id, p])),
)

const lastTrades = computed(() =>
  [...tradeList.value].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 10),
)

function countPosCost(portfolio){
  return positionList.value.filter((p) => p.portfolio == portfolio.id).reduce((total, p) => total + Number(p.instrument_info.current_price) * Number(p.quantity), 0)
}

onBeforeMount(async () => {
  const [portfolios, trades, positions] = await Promise.all([
    axios.get('/api/portfolio/'),
    axios.get('/api/trade/'),
    axios.get('/api/position'),
  ])
  portfoliosList.value = portfolios.data
  tradeList.value = trades.data
  positionList.value = positions.data
})

// моковые данные для верстки — заменить на данные из API
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
      <!-- Портфели -->
      <section class="card">
        <div class="card-header">
          <h2 class="card-title">Портфели</h2>
          <router-link :to="{ name: 'portfolios' }" class="text-sm">Все портфели</router-link>
        </div>
        <div v-if="portfoliosList.length" class="portfolio-list">
          <PortfolioShortCard
            v-for="portfolio in portfoliosList"
            :key="portfolio.id"
            :portfolio="portfolio"
            :value="Number(countPosCost(portfolio)) + Number(portfolio.balance)"
            :positionsCount="positionList.filter((p) => p.portfolio == portfolio.id).length"
          />
          
        </div>
        <EmptyState
          v-else
          icon="briefcase"
          title="Портфелей пока нет"
          text="Создайте первый портфель, задайте стартовый баланс и начните торговать."
        >
          <router-link :to="{ name: 'portfolios' }" class="btn btn-secondary">
            Создать портфель
          </router-link>
        </EmptyState>
        <div class="card-footer">
          <span class="text-muted">Свободные средства</span>
          <span class="num text-strong">{{ portfoliosBalance }} ₽</span>
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

.portfolio-list,
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
}
</style>
