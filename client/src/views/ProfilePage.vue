<script setup>
import HeaderNavbar from "@/components/HeaderNavbar.vue";
import StatCard from "@/components/StatCard.vue";
import ExportButtons from "@/components/ExportButtons.vue";
import TwoFactorCard from "@/components/TwoFactorCard.vue";
import useProfileStore from "@/stores/profileStore";
import { computed, onBeforeMount, ref } from "vue";
import axios from "axios";
import {
  formatPrice,
  formatQuantity,
  formatDate,
  formatCompact,
  toDateInputValue,
} from "@/utils/format";

const profileStore = useProfileStore();

const orderTypeLabels = { buy: "Покупка", sell: "Продажа" };
const executionTypeLabels = { market: "Рыночная", limit: "Лимитная" };
const statusLabels = {
  pending: "Ожидает",
  executed: "Исполнена",
  cancelled: "Отменена",
};

const me = ref(null);
const tradeList = ref([]);
const portfolioList = ref([]);

onBeforeMount(async () => {
  const [meRes, trades, portfolios] = await Promise.all([
    axios.get("/api/profile/me/"),
    axios.get("/api/trade/"),
    axios.get("/api/portfolio/"),
  ]);
  me.value = meRes.data;
  tradeList.value = trades.data;
  portfolioList.value = portfolios.data;
});

const tradeRows = computed(() => {
  const portfoliosById = Object.fromEntries(
    portfolioList.value.map((p) => [p.id, p]),
  );
  return [...tradeList.value]
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .map((t) => {
      const unitPrice = t.execution_price ?? t.price;
      const rawTotal =
        unitPrice != null ? Number(t.quantity) * Number(unitPrice) : null;
      return {
        ...t,
        portfolioName: portfoliosById[t.portfolio]?.name ?? "—",
        createdText: formatDate(t.created_at),
        executedText: formatDate(t.executed_at),
        createdDate: toDateInputValue(t.created_at),
        executedDate: toDateInputValue(t.executed_at),
        quantityText: formatQuantity(t.quantity),
        priceText: unitPrice != null ? `${formatPrice(unitPrice)} ₽` : "—",
        rawTotal,
        totalText: rawTotal != null ? `${formatPrice(rawTotal)} ₽` : "—",
      };
    });
});

const stats = computed(() => {
  const list = tradeList.value;
  const byStatus = (status) => list.filter((t) => t.status === status);
  const share = (n) => (list.length ? Math.round((n / list.length) * 100) : 0);

  const executed = byStatus("executed");
  const turnover = (type) =>
    executed
      .filter((t) => t.order_type === type)
      .reduce(
        (sum, t) => sum + Number(t.quantity) * Number(t.execution_price),
        0,
      );
  const buys = turnover("buy");
  const sells = turnover("sell");

  return {
    total: list.length,
    executed: executed.length,
    executedShare: share(executed.length),
    pending: byStatus("pending").length,
    cancelled: byStatus("cancelled").length,
    cancelledShare: share(byStatus("cancelled").length),
    buys,
    sells,
    turnover: buys + sells,
  };
});

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

const filteredTrades = computed(() => {
  const f = filters.value;
  const ticker = f.ticker.trim().toLowerCase();
  return tradeRows.value.filter(
    (t) =>
      (!f.created || t.createdDate === f.created) &&
      (!f.executed || t.executedDate === f.executed) &&
      (!f.portfolio || t.portfolio === f.portfolio) &&
      (!ticker || t.instrument_info.ticker.toLowerCase().includes(ticker)) &&
      (!f.orderType || t.order_type === f.orderType) &&
      (!f.executionType || t.execution_type === f.executionType) &&
      (f.totalFrom === "" || (t.rawTotal ?? 0) >= f.totalFrom) &&
      (f.totalTo === "" || (t.rawTotal ?? 0) <= f.totalTo) &&
      (!f.status || t.status === f.status),
  );
});

function resetFilters() {
  filters.value = emptyFilters();
}
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
        <section class="stats-grid" aria-label="Статистика сделок">
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
            :value="`${formatCompact(stats.turnover)} ₽`"
            :hint="`покупки ${formatCompact(stats.buys)} · продажи ${formatCompact(stats.sells)}`"
          />
        </section>

        <section class="card">
          <div class="table-toolbar">
            <h2 class="table-toolbar-title">
              История сделок
              <span class="table-count">{{ filteredTrades.length }}</span>
            </h2>
            <div class="export-actions">
              <button
                class="btn btn-ghost btn-sm"
                type="button"
                @click="resetFilters"
              >
                Сбросить фильтры
              </button>
              <ExportButtons />
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
                </tr>
                <tr class="filter-row">
                  <th>
                    <input
                      class="filter-input"
                      type="date"
                      aria-label="Создана"
                      v-model="filters.created"
                    />
                  </th>
                  <th>
                    <input
                      class="filter-input"
                      type="date"
                      aria-label="Исполнена"
                      v-model="filters.executed"
                    />
                  </th>
                  <th v-if="profileStore.isSuperuser">
                    <select class="filter-select" aria-label="Пользователь">
                      <option value="">Все</option>
                    </select>
                  </th>
                  <th>
                    <select
                      v-model="filters.portfolio"
                      class="filter-select"
                      aria-label="Портфель"
                    >
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
                      aria-label="Тикер"
                      v-model="filters.ticker"
                    />
                  </th>
                  <th>
                    <select
                      class="filter-select"
                      aria-label="Операция"
                      v-model="filters.orderType"
                    >
                      <option value="">Все</option>
                      <option value="buy">Покупка</option>
                      <option value="sell">Продажа</option>
                    </select>
                  </th>
                  <th>
                    <select
                      class="filter-select"
                      aria-label="Исполнение"
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
                        aria-label="Сумма от"
                        v-model.number="filters.totalFrom"
                      />
                      <input
                        class="filter-input"
                        type="number"
                        placeholder="до"
                        aria-label="Сумма до"
                        v-model.number="filters.totalTo"
                      />
                    </div>
                  </th>
                  <th>
                    <select
                      class="filter-select"
                      aria-label="Статус"
                      v-model="filters.status"
                    >
                      <option value="">Все</option>
                      <option value="pending">Ожидает</option>
                      <option value="executed">Исполнена</option>
                      <option value="cancelled">Отменена</option>
                    </select>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="trade in filteredTrades" :key="trade.id">
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
                </tr>
                <tr v-if="!filteredTrades.length">
                  <td
                    :colspan="profileStore.isSuperuser ? 11 : 10"
                    class="text-muted"
                  >
                    Сделок нет
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="table-footer">
            <span
              >Показано {{ filteredTrades.length }} из
              {{ tradeList.length }}</span
            >
          </div>
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
