<script setup>
import HeaderNavbar from "@/components/HeaderNavbar.vue";
import TradeCard from "@/components/TradeCard.vue";
import axios from "axios";
import { computed, onBeforeMount, ref } from "vue";

const portfoliosList = ref([]);
const lastTradeList = ref([]);

const portfoliosBalance = computed(() =>
  portfoliosList.value.reduce((total, p) => total + Number(p.balance), 0),
);

onBeforeMount(async () => {
  const [portfolios, trades] = await Promise.all([
    axios.get("/api/portfolio/"),
    axios.get("/api/trade/"),
  ]);
  portfoliosList.value = portfolios.data;
  lastTradeList.value = trades.data;
});

const firstPortfolioTrades = computed(() => {
  const first = portfoliosList.value[0];
  if (!first) return [];
  return lastTradeList.value.filter((trade) => trade.portfolio === first.id);
});
</script>
<!-- потом обращаться не к самому первому портфелю а как бы ко всем потому что же сделки же могут быть в разных портфелях -->
<template>
  <div><HeaderNavbar /></div>
  <div class="main">
    <div class="card">
      <div class="card-header">Общая стоимость портфелей</div>
      <div>//График стоимости портфелей</div>
      {{ portfoliosBalance }}
    </div>
    <div class="card">
      <div class="card-header">Последние сделки</div>
      <div class="card-container">
        <TradeCard
          v-for="trade in firstPortfolioTrades"
          :key="trade.id"
          :trade="trade"
          :portfolio="portfoliosList[0]"
        />
      </div>
    </div>
    <div class="card">
      <div class="card-header">Лучшие инструменты</div>
      <div>Карточки лучших инструментов</div>
    </div>
  </div>
</template>

<style scoped>
.main {
  display: flex;
  gap: 20px;
}

.card {
  flex: 1;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 10px;
}

.card-header {
  text-align: center;
  font-size: 30px;
}

.card-container {
  max-height: 500px;
  overflow-y: auto;
}
</style>
