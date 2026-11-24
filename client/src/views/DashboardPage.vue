<script setup>
import HeaderNavbar from "@/components/HeaderNavbar.vue";
import TradeCard from "@/components/TradeCard.vue";
import InstrumentCard from "@/components/InstrumentCard.vue";
import PortfolioShortCard from "@/components/PortfolioShortCard.vue";
import EmptyState from "@/components/EmptyState.vue";
import AppIcon from "@/components/AppIcon.vue";
import axios from "axios";
import { computed, onBeforeMount, ref, watch } from "vue";
import { mapInstrument } from "@/utils/InstrumentsMapper.js";
import { formatPrice } from "@/utils/format.js";
import { listResults } from "@/utils/lists";
import PaginationControls from "@/components/PaginationControls.vue";

const portfoliosList = ref([]);
const tradeList = ref([]);
const portfolioPage = ref(1);
const pageSize = 20;
const portfolioCount = ref(0);
const portfolioStats = ref(null);
const portfoliosBalance = computed(() =>
  Number(portfolioStats.value?.balance ?? 0),
);

const leadersPeriod = ref("day");
const leaders = ref([]);

async function fetchLeaders() {
  const { data } = await axios.get("/api/instrument/leaders/", {
    params: { period: leadersPeriod.value },
  });
  leaders.value = data.map((item) => mapInstrument(item, {}));
}

async function loadPortfolios() {
  const { data } = await axios.get("/api/portfolio/", {
    params: { page: portfolioPage.value, page_size: pageSize },
  });
  portfoliosList.value = listResults(data);
  portfolioCount.value = data.count ?? portfoliosList.value.length;
}

async function loadDashboard() {
  const [trades, stats] = await Promise.all([
    axios.get("/api/trade/", { params: { page: 1, page_size: 10 } }),
    axios.get("/api/portfolio/stats/"),
  ]);
  tradeList.value = listResults(trades.data);
  portfolioStats.value = stats.data;
}

onBeforeMount(async () => {
  await Promise.all([loadDashboard(), loadPortfolios(), fetchLeaders()]);
});

watch(portfolioPage, loadPortfolios);
watch(leadersPeriod, fetchLeaders);
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
      <section class="card">
        <div class="card-header">
          <h2 class="card-title">Портфели</h2>
          <router-link :to="{ name: 'portfolios' }" class="text-sm"
            >Все портфели</router-link
          >
        </div>
        <div v-if="portfoliosList.length" class="portfolio-list">
          <PortfolioShortCard
            v-for="portfolio in portfoliosList"
            :key="portfolio.id"
            :portfolio="portfolio"
            :value="
              formatPrice(
                Number(portfolio.balance) +
                  Number(portfolio.positions_value ?? 0),
              )
            "
            :positionsCount="portfolio.positions_count ?? 0"
          />
        </div>
        <PaginationControls
          v-if="portfolioCount"
          v-model:page="portfolioPage"
          :count="portfolioCount"
          :page-size="pageSize"
        />
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
          <span class="num text-strong"
            >{{ formatPrice(portfoliosBalance) }} ₽</span
          >
        </div>
      </section>
      <section class="card">
        <div class="card-header">
          <h2 class="card-title">Последние сделки</h2>
          <router-link :to="{ name: 'profile' }" class="text-sm"
            >Вся история</router-link
          >
        </div>
        <div v-if="tradeList.length" class="trade-list">
          <TradeCard
            v-for="trade in tradeList"
            :key="trade.id"
            :trade="trade"
            :portfolio="{ name: trade.portfolio_name }"
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
      <section class="card">
        <div class="card-header">
          <h2 class="card-title">Лидеры роста</h2>
          <div class="segmented">
            <button
              class="segmented-btn"
              :class="{ 'is-active': leadersPeriod === 'day' }"
              type="button"
              @click="leadersPeriod = 'day'"
            >
              День
            </button>
            <button
              class="segmented-btn"
              :class="{ 'is-active': leadersPeriod === 'week' }"
              type="button"
              @click="leadersPeriod = 'week'"
            >
              Неделя
            </button>
          </div>
        </div>
        <div class="instrument-list">
          <InstrumentCard
            v-for="(instrument, index) in leaders"
            :key="instrument.id"
            :instrument="instrument"
            :rank="index + 1"
            :change="instrument.change"
            :is-up="instrument.isUp"
          />
        </div>
        <div class="card-footer">
          <span class="text-muted"
            >По изменению цены за
            {{ leadersPeriod === "day" ? "день" : "неделю" }}</span
          >
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
