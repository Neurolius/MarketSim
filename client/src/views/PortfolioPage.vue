<script setup>
import { computed, onBeforeMount, ref } from "vue";
import HeaderNavbar from "@/components/HeaderNavbar.vue";
import AppIcon from "@/components/AppIcon.vue";
import StatCard from "@/components/StatCard.vue";
import ExportButtons from "@/components/ExportButtons.vue";
import InstrumentLogo from "@/components/InstrumentLogo.vue";
import PortfolioFormModal from "@/components/modals/PortfolioFormModal.vue";
import ConfirmDeleteModal from "@/components/modals/ConfirmDeleteModal.vue";
import ImageModal from "@/components/modals/ImageModal.vue";
import SellModal from "@/components/modals/SellModal.vue";
import TradeEditModal from "@/components/modals/TradeEditModal.vue";

import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import {
  formatPrice,
  formatQuantity,
  formatSigned,
  formatCompact,
  formatCompactSigned,
  toDateInputValue,
} from "@/utils/format";
import { toFormData, errorText } from "@/utils/requestFormatter";
import { byId, sortByNewest, inRange, matchesText } from "@/utils/lists";
import { calcPosition } from "@/utils/positions";
import { orderTypeLabels, executionTypeLabels, statusLabels } from "@/utils/labels";

const isEditOpen = ref(false);
const isDeleteOpen = ref(false);
const imageModal = ref(null);
const sellPosition = ref(null);
const editTrade = ref(null);

const route = useRoute();
const router = useRouter();

const portfolio = ref(null);
const positionList = ref([]);
const tradeList = ref([]);
const typesList = ref([]);

async function loadPortfolio() {
  const id = route.params.id;
  const params = { portfolio: id };
  const [portfolioRes, positions, trades, types] = await Promise.all([
    axios.get(`/api/portfolio/${id}/`),
    axios.get("/api/position/", { params }),
    axios.get("/api/trade/", { params }),
    axios.get("/api/instrumenttype/"),
  ]);
  portfolio.value = portfolioRes.data;
  positionList.value = positions.data;
  tradeList.value = trades.data;
  typesList.value = types.data;
}

onBeforeMount(async () => {
  await loadPortfolio();
});

const positionRows = computed(() => {
  const typesById = byId(typesList.value);
  return positionList.value
    .map((pos) => {
      const c = calcPosition(pos);
      const typeId = pos.instrument_info.instrument_type;
      return {
        ...pos,
        typeId,
        typeName: typesById[typeId]?.name ?? "—",
        rawValue: c.value,
        rawCost: c.cost,
        rawProfit: c.profit,
        quantityText: formatQuantity(c.quantity),
        averageText: formatPrice(c.average),
        currentText: formatPrice(c.current),
        valueText: formatPrice(c.value),
        profitText: `${formatSigned(c.profit)} ₽`,
        percentText: `${formatSigned(c.percent)}%`,
        isUp: c.profit >= 0,
      };
    })
    .sort((a, b) => b.rawProfit - a.rawProfit);
});

const totals = computed(() => {
  const rows = positionRows.value;
  const positionsValue = rows.reduce((sum, r) => sum + r.rawValue, 0);
  const cost = rows.reduce((sum, r) => sum + r.rawCost, 0);
  const profit = positionsValue - cost;
  const balance = Number(portfolio.value?.balance ?? 0);
  return {
    balance,
    positionsValue,
    value: balance + positionsValue,
    profit,
    percent: cost ? (profit / cost) * 100 : 0,
    pendingCount: tradeList.value.filter((t) => t.status === "pending").length,
  };
});

const emptyPositionFilters = () => ({
  ticker: "",
  type: "",
  qtyFrom: "",
  qtyTo: "",
  valueFrom: "",
  valueTo: "",
  result: "",
});
const positionFilters = ref(emptyPositionFilters());

const filteredPositions = computed(() => {
  const f = positionFilters.value;
  return positionRows.value.filter(
    (p) =>
      matchesText(p.instrument_info.ticker, f.ticker) &&
      (!f.type || p.typeId === f.type) &&
      inRange(Number(p.quantity), f.qtyFrom, f.qtyTo) &&
      inRange(p.rawValue, f.valueFrom, f.valueTo) &&
      (!f.result || (f.result === "profit" ? p.rawProfit > 0 : p.rawProfit < 0)),
  );
});

const emptyTradeFilters = () => ({
  date: "",
  ticker: "",
  orderType: "",
  executionType: "",
  status: "",
});
const tradeFilters = ref(emptyTradeFilters());

const filteredTrades = computed(() => {
  const f = tradeFilters.value;
  return sortByNewest(tradeList.value).filter(
    (t) =>
      (!f.date || toDateInputValue(t.created_at) === f.date) &&
      matchesText(t.instrument_info.ticker, f.ticker) &&
      (!f.orderType || t.order_type === f.orderType) &&
      (!f.executionType || t.execution_type === f.executionType) &&
      (!f.status || t.status === f.status),
  );
});

const formError = ref("");
const isSaving = ref(false);

function openEdit() {
  formError.value = "";
  isEditOpen.value = true;
}

async function savePortfolio(data) {
  formError.value = "";
  isSaving.value = true;
  try {
    await axios.patch(`/api/portfolio/${portfolio.value.id}/`, toFormData(data));
    isEditOpen.value = false;
    await loadPortfolio();
  } catch (e) {
    formError.value = errorText(e);
  } finally {
    isSaving.value = false;
  }
}

async function deletePortfolio() {
  await axios.delete(`/api/portfolio/${portfolio.value.id}/`);
  router.push({ name: "portfolios" });
}

const sellError = ref("");

function openSell(position) {
  sellError.value = "";
  sellPosition.value = position;
}

async function onSell(data) {
  sellError.value = "";
  isSaving.value = true;
  try {
    await axios.post(
      "/api/trade/",
      toFormData({
        ...data,
        portfolio: portfolio.value.id,
        instrument: sellPosition.value.instrument,
        order_type: "sell",
      }),
    );
    sellPosition.value = null;
    await loadPortfolio();
  } catch (e) {
    sellError.value = errorText(e);
  } finally {
    isSaving.value = false;
  }
}

const tradeError = ref("");
const cancellingTrade = ref(null);

function openTradeEdit(trade) {
  tradeError.value = "";
  editTrade.value = trade;
}

async function saveTrade(data) {
  tradeError.value = "";
  isSaving.value = true;
  try {
    await axios.patch(`/api/trade/${editTrade.value.id}/`, toFormData(data));
    editTrade.value = null;
    await loadPortfolio();
  } catch (e) {
    tradeError.value = errorText(e);
  } finally {
    isSaving.value = false;
  }
}

function askCancelTrade(trade) {
  editTrade.value = null;
  cancellingTrade.value = trade;
}

async function cancelTrade() {
  try {
    await axios.post(`/api/trade/${cancellingTrade.value.id}/cancel/`);
    await loadPortfolio();
  } catch (e) {
    alert(errorText(e));
  } finally {
    cancellingTrade.value = null;
  }
}
</script>

<template>
  <HeaderNavbar />
  <main v-if="portfolio" class="page">
    <nav class="breadcrumbs" aria-label="Навигационная цепочка">
      <router-link :to="{ name: 'portfolios' }">Портфели</router-link>
      <span class="breadcrumbs-sep">/</span>
      <span>{{ portfolio.name }}</span>
    </nav>

    <section class="portfolio-hero">
      <button
        class="portfolio-hero-cover"
        type="button"
        aria-label="Открыть обложку портфеля"
        @click="
          portfolio.cover_image &&
          (imageModal = {
            src: portfolio.cover_image,
            caption: `Обложка портфеля «${portfolio.name}»`,
          })
        "
      >
        <img v-if="portfolio.cover_image" :src="portfolio.cover_image" alt="" />
      </button>
      <div class="portfolio-hero-body">
        <div>
          <h1 class="page-title">{{ portfolio.name }}</h1>
          <p class="page-subtitle">Владелец {{ portfolio.user_name }}</p>
        </div>
        <div class="page-actions">
          <button class="btn btn-secondary" type="button" @click="openEdit">
            <AppIcon name="edit" />
            Изменить
          </button>
          <button class="btn btn-danger" type="button" @click="isDeleteOpen = true">
            <AppIcon name="trash" />
            Удалить
          </button>
        </div>
      </div>
    </section>

    <section class="stats-grid" aria-label="Статистика портфеля">
      <StatCard
        label="Стоимость"
        :value="`${formatCompact(totals.value)} ₽`"
        hint="баланс + позиции"
      />
      <StatCard
        label="Баланс"
        :value="`${formatCompact(totals.balance)} ₽`"
        hint="доступно для покупок"
      />
      <StatCard
        label="В позициях"
        :value="`${formatCompact(totals.positionsValue)} ₽`"
        :hint="`инструментов: ${positionRows.length}`"
      />
      <StatCard
        label="П/У по позициям"
        :value="`${formatCompactSigned(totals.profit)} ₽`"
        :hint="`${formatSigned(totals.percent)}% от вложенного`"
        :tone="totals.profit >= 0 ? 'up' : 'down'"
      />
      <StatCard
        label="Сделок"
        :value="tradeList.length"
        :hint="`ожидают исполнения: ${totals.pendingCount}`"
      />
    </section>

    <section class="card">
      <div class="table-toolbar">
        <h2 class="table-toolbar-title">
          Позиции
          <span class="table-count">{{ filteredPositions.length }}</span>
        </h2>
        <div class="export-actions">
          <ExportButtons />
        </div>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Инструмент</th>
              <th>Тип</th>
              <th class="col-num">Кол-во</th>
              <th class="col-num">Ср. цена</th>
              <th class="col-num">Текущая цена</th>
              <th class="col-num">Стоимость</th>
              <th class="col-num">
                <span class="th-sort is-sorted">П/У ▼</span>
              </th>
              <th class="col-actions"></th>
            </tr>
            <tr class="filter-row">
              <th>
                <input
                  v-model="positionFilters.ticker"
                  class="filter-input"
                  type="search"
                  placeholder="Тикер"
                  aria-label="Тикер"
                />
              </th>
              <th>
                <select v-model="positionFilters.type" class="filter-select" aria-label="Тип">
                  <option value="">Все</option>
                  <option v-for="type in typesList" :key="type.id" :value="type.id">
                    {{ type.name }}
                  </option>
                </select>
              </th>
              <th>
                <div class="filter-range">
                  <input
                    class="filter-input"
                    type="number"
                    placeholder="от"
                    aria-label="Количество от"
                    v-model.number="positionFilters.qtyFrom"
                  />
                  <input
                    class="filter-input"
                    type="number"
                    placeholder="до"
                    aria-label="Количество до"
                    v-model.number="positionFilters.qtyTo"
                  />
                </div>
              </th>
              <th></th>
              <th></th>
              <th>
                <div class="filter-range">
                  <input
                    class="filter-input"
                    type="number"
                    placeholder="от"
                    aria-label="Стоимость от"
                    v-model.number="positionFilters.valueFrom"
                  />
                  <input
                    class="filter-input"
                    type="number"
                    placeholder="до"
                    aria-label="Стоимость до"
                    v-model.number="positionFilters.valueTo"
                  />
                </div>
              </th>
              <th>
                <select
                  class="filter-select"
                  aria-label="Результат"
                  v-model="positionFilters.result"
                >
                  <option value="">Все</option>
                  <option value="profit">Прибыль</option>
                  <option value="loss">Убыток</option>
                </select>
              </th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="position in filteredPositions" :key="position.id">
              <td>
                <div class="cell-instrument">
                  <InstrumentLogo
                    :ticker="position.instrument_info.ticker"
                    :logo="position.instrument_info.logo"
                    :zoomable="false"
                  />
                  <span class="cell-instrument-text">
                    <router-link
                      :to="{
                        name: 'instrument',
                        params: { id: position.instrument_info.id },
                      }"
                      class="cell-instrument-ticker"
                    >
                      {{ position.instrument_info.ticker }}
                    </router-link>
                    <span class="cell-instrument-name">{{ position.instrument_info.name }}</span>
                  </span>
                </div>
              </td>
              <td>
                <span class="badge badge-type">{{ position.typeName }}</span>
              </td>
              <td class="col-num num">{{ position.quantityText }}</td>
              <td class="col-num num">{{ position.averageText }} ₽</td>
              <td class="col-num num">{{ position.currentText }} ₽</td>
              <td class="col-num num">{{ position.valueText }} ₽</td>
              <td class="col-num">
                <div class="price-change" :class="position.isUp ? 'is-up' : 'is-down'">
                  {{ position.profitText }}
                </div>
                <div class="price-change text-xs" :class="position.isUp ? 'is-up' : 'is-down'">
                  {{ position.percentText }}
                </div>
              </td>
              <td class="col-actions">
                <button class="btn btn-sell btn-sm" type="button" @click="openSell(position)">
                  Продать
                </button>
              </td>
            </tr>
            <tr v-if="!filteredPositions.length">
              <td colspan="8" class="text-muted">Позиций нет</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-footer">
        <span
          >Итого в позициях:
          <strong class="num">{{ formatPrice(totals.positionsValue) }} ₽</strong></span
        >
        <span
          >Общий П/У:
          <span class="price-change" :class="totals.profit >= 0 ? 'is-up' : 'is-down'"
            >{{ formatSigned(totals.profit) }} ₽</span
          >
        </span>
      </div>
    </section>

    <section class="card">
      <div class="table-toolbar">
        <h2 class="table-toolbar-title">
          Сделки портфеля
          <span class="table-count">{{ filteredTrades.length }}</span>
        </h2>
        <div class="export-actions">
          <ExportButtons />
        </div>
      </div>
      <div class="table-wrap">
        <table class="data-table data-table-compact">
          <thead>
            <tr>
              <th>Создана</th>
              <th>Инструмент</th>
              <th>Операция</th>
              <th>Исполнение</th>
              <th class="col-num">Кол-во</th>
              <th class="col-num">Лимит</th>
              <th class="col-num">Цена исп.</th>
              <th>Статус</th>
              <th>Фото</th>
              <th class="col-actions"></th>
            </tr>
            <tr class="filter-row">
              <th>
                <input
                  class="filter-input"
                  type="date"
                  aria-label="Дата создания"
                  v-model="tradeFilters.date"
                />
              </th>
              <th>
                <input
                  class="filter-input"
                  type="search"
                  placeholder="Тикер"
                  aria-label="Тикер"
                  v-model="tradeFilters.ticker"
                />
              </th>
              <th>
                <select
                  class="filter-select"
                  aria-label="Операция"
                  v-model="tradeFilters.orderType"
                >
                  <option value="">Все</option>
                  <option value="buy">Покупка</option>
                  <option value="sell">Продажа</option>
                </select>
              </th>
              <th>
                <select
                  v-model="tradeFilters.executionType"
                  class="filter-select"
                  aria-label="Исполнение"
                >
                  <option value="">Все</option>
                  <option value="market">Рыночная</option>
                  <option value="limit">Лимитная</option>
                </select>
              </th>
              <th></th>
              <th></th>
              <th></th>
              <th>
                <select class="filter-select" aria-label="Статус" v-model="tradeFilters.status">
                  <option value="">Все</option>
                  <option value="pending">Ожидает</option>
                  <option value="executed">Исполнена</option>
                  <option value="cancelled">Отменена</option>
                </select>
              </th>
              <th></th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="trade in filteredTrades" :key="trade.id">
              <td class="num">
                {{ new Date(trade.created_at).toLocaleString() }}
              </td>
              <td>
                <router-link :to="{ name: 'instrument', params: { id: trade.instrument } }">
                  <strong>{{ trade.instrument_info.ticker }}</strong>
                </router-link>
              </td>
              <td>
                <span class="badge" :class="`badge-${trade.order_type}`">
                  {{ orderTypeLabels[trade.order_type] }}
                </span>
              </td>
              <td>
                <span class="badge badge-exec">{{
                  executionTypeLabels[trade.execution_type]
                }}</span>
              </td>
              <td class="col-num num">{{ formatQuantity(trade.quantity) }}</td>
              <td class="col-num num" :class="{ 'text-muted': !trade.price }">
                {{ trade.price ? `${formatPrice(trade.price)} ₽` : "—" }}
              </td>
              <td class="col-num num" :class="{ 'text-muted': !trade.execution_price }">
                {{ trade.execution_price ? `${formatPrice(trade.execution_price)} ₽` : "—" }}
              </td>
              <td>
                <span class="badge" :class="`badge-${trade.status}`">
                  {{ statusLabels[trade.status] }}
                </span>
              </td>
              <td>
                <button
                  v-if="trade.image"
                  class="row-thumb"
                  type="button"
                  aria-label="Открыть изображение сделки"
                  :style="{
                    backgroundImage: `url(${trade.image})`,
                    backgroundSize: 'cover',
                  }"
                  @click="
                    imageModal = {
                      src: trade.image,
                      caption: `Сделка ${trade.instrument_info.ticker}`,
                    }
                  "
                ></button>
                <span v-else class="text-muted">—</span>
              </td>
              <td class="col-actions">
                <template v-if="trade.status === 'pending'">
                  <button class="btn btn-ghost btn-sm" type="button" @click="openTradeEdit(trade)">
                    Изменить
                  </button>
                  <button
                    class="btn btn-danger btn-sm"
                    type="button"
                    @click="cancellingTrade = trade"
                  >
                    Отменить
                  </button>
                </template>
              </td>
            </tr>
            <tr v-if="!filteredTrades.length">
              <td colspan="10" class="text-muted">Сделок нет</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-footer">
        <span>Показано {{ filteredTrades.length }} из {{ tradeList.length }}</span>
      </div>
    </section>
  </main>

  <PortfolioFormModal
    v-if="isEditOpen"
    :portfolio="portfolio"
    :error="formError"
    :loading="isSaving"
    @close="isEditOpen = false"
    @submit="savePortfolio"
  />
  <ConfirmDeleteModal
    v-if="cancellingTrade"
    :title="`Отменить заявку по ${cancellingTrade.instrument_info.ticker}?`"
    text="Заявка получит статус «Отменена» и больше не исполнится. Вернуть её нельзя."
    confirm-text="Отменить заявку"
    @close="cancellingTrade = null"
    @confirm="cancelTrade"
  />
  <ImageModal
    v-if="imageModal"
    :src="imageModal.src"
    :caption="imageModal.caption"
    @close="imageModal = null"
  />
  <SellModal
    v-if="sellPosition"
    :position="sellPosition"
    :portfolio-name="portfolio.name"
    :error="sellError"
    :loading="isSaving"
    @close="sellPosition = null"
    @submit="onSell"
  />
  <TradeEditModal
    v-if="editTrade"
    :trade="editTrade"
    :error="tradeError"
    :loading="isSaving"
    @close="editTrade = null"
    @submit="saveTrade"
    @cancel-trade="askCancelTrade(editTrade)"
  />
</template>

<style scoped>
.portfolio-hero {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
}

.portfolio-hero-cover {
  display: block;
  width: 100%;
  height: 160px;
  padding: 0;
  border: 0;
  background: repeating-linear-gradient(135deg, #e3e8f0 0 12px, #d9dfe9 12px 24px);
  cursor: zoom-in;
}

.portfolio-hero-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.portfolio-hero-body {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-5);
}
</style>
