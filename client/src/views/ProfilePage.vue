<script setup>
import HeaderNavbar from "@/components/HeaderNavbar.vue";
import StatCard from "@/components/StatCard.vue";
import ExportButtons from "@/components/ExportButtons.vue";
import TradeImageGallery from "@/components/TradeImageGallery.vue";
import TwoFactorCard from "@/components/TwoFactorCard.vue";
import useProfileStore from "@/stores/profileStore";
import { computed, onBeforeMount, ref, watch } from "vue";
import axios from "axios";
import { listResults } from "@/utils/lists";
import {
  formatPrice,
  formatQuantity,
  formatDate,
  formatCompact,
} from "@/utils/format";
import {
  orderTypeLabels,
  executionTypeLabels,
  statusLabels,
} from "@/utils/labels";
import PaginationControls from "@/components/PaginationControls.vue";

const profileStore = useProfileStore();

const me = ref(null);
const tradeList = ref([]);
const portfolioList = ref([]);
const stats = ref({
  total: 0,
  executed: 0,
  executedShare: 0,
  pending: 0,
  cancelled: 0,
  cancelledShare: 0,
  buys: 0,
  sells: 0,
});
const tradePage = ref(1);
const tradeCount = ref(0);
const pageSize = 20;

async function loadTrades() {
  const params = {
    ...tradeFilterParams(),
    page: tradePage.value,
    page_size: pageSize,
  };

  const { data } = await axios.get("/api/trade/", { params });
  tradeList.value = listResults(data);
  tradeCount.value = data.count ?? tradeList.value.length;
}

onBeforeMount(async () => {
  const [meRes, portfoliosRes, statsRes] = await Promise.all([
    axios.get("/api/profile/me/"),
    axios.get("/api/portfolio/", { params: { page_size: 100 } }),
    axios.get("/api/trade/stats/"),
  ]);
  me.value = meRes.data;
  portfolioList.value = listResults(portfoliosRes.data);
  stats.value = statsRes.data;
  await loadTrades();
});

const tradeRows = computed(() => {
  return tradeList.value.map((t) => {
    const unitPrice = t.execution_price ?? t.price;
    const rawTotal =
      unitPrice != null ? Number(t.quantity) * Number(unitPrice) : null;
    return {
      ...t,
      portfolioName: t.portfolio_name ?? "—",
      createdText: formatDate(t.created_at),
      executedText: formatDate(t.executed_at),
      quantityText: formatQuantity(t.quantity),
      priceText: unitPrice != null ? `${formatPrice(unitPrice)} ₽` : "—",
      totalText: rawTotal != null ? `${formatPrice(rawTotal)} ₽` : "—",
    };
  });
});

const turnover = computed(
  () => Number(stats.value.buys) + Number(stats.value.sells),
);

const emptyFilters = () => ({
  created: "",
  executed: "",
  portfolio: "",
  ticker: "",
  orderType: "",
  executionType: "",
  totalFrom: "",
  totalTo: "",
  status: "",
});
const filters = ref(emptyFilters());

function tradeFilterParams() {
  const params = {};
  const f = filters.value;
  if (f.created) params.created = f.created;
  if (f.executed) params.executed = f.executed;
  if (f.portfolio) params.portfolio = f.portfolio;
  if (f.ticker) params.ticker = f.ticker;
  if (f.orderType) params.order_type = f.orderType;
  if (f.executionType) params.execution_type = f.executionType;
  if (f.totalFrom !== "") params.total_from = f.totalFrom;
  if (f.totalTo !== "") params.total_to = f.totalTo;
  if (f.status) params.status = f.status;
  return params;
}

const exportParams = computed(tradeFilterParams);

function resetFilters() {
  filters.value = emptyFilters();
}

watch(
  filters,
  () => {
    if (tradePage.value !== 1) tradePage.value = 1;
    else loadTrades();
  },
  { deep: true },
);

watch(tradePage, loadTrades);
</script>

<template>
  <HeaderNavbar />
  <main class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Профиль</h1>
        <p class="page-subtitle">
          Данные аккаунта, двухфакторная защита и полная история сделок
        </p>
      </div>
    </div>

    <div class="split-side">
      <div class="stack">
        <section class="card profile-card">
          <span class="avatar avatar-lg">{{
            profileStore.userName?.slice(0, 2).toUpperCase()
          }}</span>
          <h2 class="profile-name">{{ profileStore.userName }}</h2>
          <span v-if="profileStore.isSuperuser" class="badge badge-admin"
            >Суперпользователь</span
          >
          <div v-if="me" class="info-list">
            <div class="info-list-row">
              <span class="text-muted">Email</span>
              <span>{{ me.email || "—" }}</span>
            </div>
            <div class="info-list-row">
              <span class="text-muted">Регистрация</span>
              <span class="num">{{
                new Date(me.date_joined).toLocaleDateString("ru-RU")
              }}</span>
            </div>
            <div class="info-list-row">
              <span class="text-muted">Последний вход</span>
              <span class="num">{{ formatDate(me.last_login) }}</span>
            </div>
            <div class="info-list-row">
              <span class="text-muted">Портфелей</span>
              <span class="num">{{ me.portfolios_count }}</span>
            </div>
          </div>
        </section>

        <TwoFactorCard />
      </div>

      <div class="stack">
        <section class="stats-grid">
          <StatCard
            label="Всего сделок"
            :value="stats.total"
            hint="за всё время"
          />
          <StatCard
            label="Исполнено"
            :value="stats.executed"
            :hint="`${stats.executedShare}%`"
            tone="up"
          />
          <StatCard
            label="Ожидают"
            :value="stats.pending"
            hint="лимитные заявки"
            tone="warn"
          />
          <StatCard
            label="Отменено"
            :value="stats.cancelled"
            :hint="`${stats.cancelledShare}%`"
            tone="muted"
          />
          <StatCard
            label="Оборот"
            :value="`${formatCompact(turnover)} ₽`"
            :hint="`покупки ${formatCompact(stats.buys)} · продажи ${formatCompact(stats.sells)}`"
          />
        </section>

        <section class="card">
          <div class="table-toolbar">
            <h2 class="table-toolbar-title">
              История сделок
              <span class="table-count">{{ tradeCount }}</span>
            </h2>
            <div class="export-actions">
              <button
                class="btn btn-ghost btn-sm"
                type="button"
                @click="resetFilters"
              >
                Сбросить фильтры
              </button>
              <ExportButtons url="/api/trade/export/" :params="exportParams" />
            </div>
          </div>
          <div class="table-wrap trades-scroll">
            <table class="data-table data-table-compact">
              <thead>
                <tr>
                  <th>Создана</th>
                  <th>Исполнена</th>
                  <th v-if="profileStore.isSuperuser">
                    Пользователь <span class="admin-only-tag">админ</span>
                  </th>
                  <th>Портфель</th>
                  <th>Инструмент</th>
                  <th>Операция</th>
                  <th>Исполнение</th>
                  <th class="col-num">Кол-во</th>
                  <th class="col-num">Цена</th>
                  <th class="col-num">Сумма</th>
                  <th>Статус</th>
                  <th>Фото</th>
                </tr>
                <tr class="filter-row">
                  <th>
                    <input
                      class="filter-input"
                      type="date"
                      v-model="filters.created"
                    />
                  </th>
                  <th>
                    <input
                      class="filter-input"
                      type="date"
                      v-model="filters.executed"
                    />
                  </th>
                  <th v-if="profileStore.isSuperuser">
                    <select class="filter-select">
                      <option value="">Все</option>
                    </select>
                  </th>
                  <th>
                    <select v-model="filters.portfolio" class="filter-select">
                      <option value="">Все</option>
                      <option
                        v-for="p in portfolioList"
                        :key="p.id"
                        :value="p.id"
                      >
                        {{ p.name }}
                      </option>
                    </select>
                  </th>
                  <th>
                    <input
                      class="filter-input"
                      type="search"
                      placeholder="Тикер"
                      v-model="filters.ticker"
                    />
                  </th>
                  <th>
                    <select class="filter-select" v-model="filters.orderType">
                      <option value="">Все</option>
                      <option value="buy">Покупка</option>
                      <option value="sell">Продажа</option>
                    </select>
                  </th>
                  <th>
                    <select
                      class="filter-select"
                      v-model="filters.executionType"
                    >
                      <option value="">Все</option>
                      <option value="market">Рыночная</option>
                      <option value="limit">Лимитная</option>
                    </select>
                  </th>
                  <th></th>
                  <th></th>
                  <th>
                    <div class="filter-range">
                      <input
                        class="filter-input"
                        type="number"
                        placeholder="от"
                        v-model.number="filters.totalFrom"
                      />
                      <input
                        class="filter-input"
                        type="number"
                        placeholder="до"
                        v-model.number="filters.totalTo"
                      />
                    </div>
                  </th>
                  <th>
                    <select class="filter-select" v-model="filters.status">
                      <option value="">Все</option>
                      <option value="pending">Ожидает</option>
                      <option value="executed">Исполнена</option>
                      <option value="cancelled">Отменена</option>
                    </select>
                  </th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="trade in tradeRows" :key="trade.id">
                  <td class="num">{{ trade.createdText }}</td>
                  <td class="num" :class="{ 'text-muted': !trade.executed_at }">
                    {{ trade.executedText }}
                  </td>
                  <td v-if="profileStore.isSuperuser" class="text-muted">—</td>
                  <td>
                    <router-link
                      :to="{
                        name: 'portfolio',
                        params: { id: trade.portfolio },
                      }"
                    >
                      {{ trade.portfolioName }}
                    </router-link>
                  </td>
                  <td>
                    <router-link
                      :to="{
                        name: 'instrument',
                        params: { id: trade.instrument },
                      }"
                    >
                      <strong>{{ trade.instrument_info.ticker }}</strong>
                    </router-link>
                  </td>
                  <td>
                    <span class="badge" :class="`badge-${trade.order_type}`">
                      {{ orderTypeLabels[trade.order_type] }}
                    </span>
                  </td>
                  <td>
                    <span class="badge badge-exec">
                      {{ executionTypeLabels[trade.execution_type] }}
                    </span>
                  </td>
                  <td class="col-num num">{{ trade.quantityText }}</td>
                  <td class="col-num num">{{ trade.priceText }}</td>
                  <td class="col-num num">{{ trade.totalText }}</td>
                  <td>
                    <span class="badge" :class="`badge-${trade.status}`">
                      {{ statusLabels[trade.status] }}
                    </span>
                  </td>
                  <td>
                    <TradeImageGallery
                      :images="trade.images"
                      :caption="`Сделка ${trade.instrument_info.ticker}`"
                    />
                    <span v-if="!trade.images?.length" class="text-muted"
                      >—</span
                    >
                  </td>
                </tr>
                <tr v-if="!tradeRows.length">
                  <td
                    :colspan="profileStore.isSuperuser ? 12 : 11"
                    class="text-muted"
                  >
                    Сделок нет
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="table-footer">
            <span>Показано {{ tradeRows.length }} из {{ tradeCount }}</span>
          </div>
          <PaginationControls
            v-if="tradeCount"
            v-model:page="tradePage"
            :count="tradeCount"
            :page-size="pageSize"
          />
        </section>
      </div>
    </div>
  </main>
</template>

<style scoped>
.profile-card {
  align-items: center;
  text-align: center;
  gap: var(--space-2);
  padding: var(--space-6);
}

.profile-name {
  font-size: var(--font-size-xl);
  font-weight: 600;
}

.info-list {
  display: flex;
  flex-direction: column;
  width: 100%;
  margin-top: var(--space-3);
  text-align: left;
}

.trades-scroll {
  max-height: 360px;
  overflow-y: auto;
}

.trades-scroll thead {
  position: sticky;
  top: 0;
  z-index: 1;
}

.info-list-row {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  border-top: 1px solid var(--color-border);
  font-size: var(--font-size-sm);
}
</style>
