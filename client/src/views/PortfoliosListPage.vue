<script setup>
import { computed, onBeforeMount, ref } from "vue";
import HeaderNavbar from "@/components/HeaderNavbar.vue";
import AppIcon from "@/components/AppIcon.vue";
import StatCard from "@/components/StatCard.vue";
import ExportButtons from "@/components/ExportButtons.vue";
import PortfolioCard from "@/components/PortfolioCard.vue";
import EmptyState from "@/components/EmptyState.vue";
import PortfolioFormModal from "@/components/modals/PortfolioFormModal.vue";
import ConfirmDeleteModal from "@/components/modals/ConfirmDeleteModal.vue";
import TwoFactorModal from "@/components/modals/TwoFactorModal.vue";
import ImageModal from "@/components/modals/ImageModal.vue";
import useProfileStore from "@/stores/profileStore";

import axios from "axios";
import {
  formatPrice,
  formatSigned,
  formatCompact,
  formatCompactSigned,
} from "@/utils/format";
import { toFormData, errorText } from "@/utils/requestFormatter";
import { inRange, matchesText } from "@/utils/lists";
import { calcPosition } from "@/utils/positions";

const profileStore = useProfileStore();

const formPortfolio = ref(null);
const deletePortfolio = ref(null);
const coverPortfolio = ref(null);
const isTwoFactorOpen = ref(false);

const portfolioList = ref([]);
const positionList = ref([]);

async function loadPortfolios() {
  const [portfolios, positions] = await Promise.all([
    axios.get("/api/portfolio/"),
    axios.get("/api/position/"),
  ]);
  portfolioList.value = portfolios.data;
  positionList.value = positions.data;
}

onBeforeMount(loadPortfolios);

const portfolioRows = computed(() => {
  const stats = {};
  for (const pos of positionList.value) {
    if (!stats[pos.portfolio])
      stats[pos.portfolio] = { positionsValue: 0, cost: 0, count: 0 };
    const s = stats[pos.portfolio];
    const c = calcPosition(pos);
    s.positionsValue += c.value;
    s.cost += c.cost;
    s.count += 1;
  }

  return portfolioList.value.map((p) => {
    const s = stats[p.id] ?? { positionsValue: 0, cost: 0, count: 0 };
    const balance = Number(p.balance);
    const value = balance + s.positionsValue;
    const profit = s.positionsValue - s.cost;
    const percent = s.cost ? (profit / s.cost) * 100 : 0;
    return {
      ...p,
      rawBalance: balance,
      rawValue: value,
      rawProfit: profit,
      rawCost: s.cost,
      positionsCount: s.count,
      valueText: `${formatPrice(value)} ₽`,
      profitText: `${formatSigned(profit)} ₽`,
      change: s.cost ? `${formatSigned(percent)}%` : "",
      isUp: profit >= 0,
    };
  });
});

const totals = computed(() => {
  const rows = portfolioRows.value;
  const sum = (key) => rows.reduce((total, p) => total + p[key], 0);
  const value = sum("rawValue");
  const balance = sum("rawBalance");
  const profit = sum("rawProfit");
  const cost = sum("rawCost");
  return {
    value,
    balance,
    profit,
    avg: rows.length ? value / rows.length : 0,
    freeShare: value ? (balance / value) * 100 : 0,
    profitPercent: cost ? (profit / cost) * 100 : 0,
  };
});

const emptyFilters = () => ({
  name: "",
  balanceFrom: "",
  balanceTo: "",
  valueFrom: "",
  valueTo: "",
});
const filters = ref(emptyFilters());

const filteredPortfolios = computed(() => {
  const f = filters.value;
  return portfolioRows.value.filter(
    (p) =>
      matchesText(p.name, f.name) &&
      inRange(p.rawBalance, f.balanceFrom, f.balanceTo) &&
      inRange(p.rawValue, f.valueFrom, f.valueTo),
  );
});

function resetFilters() {
  filters.value = emptyFilters();
}

const formError = ref("");
const isSaving = ref(false);

function openForm(portfolio) {
  formError.value = "";
  formPortfolio.value = portfolio;
}

async function savePortfolio(data) {
  formError.value = "";
  isSaving.value = true;
  try {
    const body = toFormData(data);
    const id = formPortfolio.value.id;
    if (id) await axios.patch(`/api/portfolio/${id}/`, body);
    else await axios.post("/api/portfolio/", body);
    formPortfolio.value = null;
    await loadPortfolios();
  } catch (e) {
    formError.value = errorText(e);
  } finally {
    isSaving.value = false;
  }
}

async function confirmDelete() {
  await axios.delete(`/api/portfolio/${deletePortfolio.value.id}/`);
  deletePortfolio.value = null;
  await loadPortfolios();
}
</script>

<template>
  <HeaderNavbar />
  <main class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Портфели</h1>
        <p class="page-subtitle">
          Виртуальные счета с собственным балансом и позициями
        </p>
      </div>
      <div class="page-actions">
        <ExportButtons :small="false" />
        <button
          class="btn btn-primary"
          type="button"
          @click="formPortfolio = {}"
        >
          <AppIcon name="plus" />
          Создать портфель
        </button>
      </div>
    </div>

    <section class="stats-grid" aria-label="Статистика">
      <StatCard
        label="Портфелей"
        :value="portfolioList.length"
        :hint="`по фильтру: ${filteredPortfolios.length}`"
      />
      <StatCard
        label="Общая стоимость"
        :value="`${formatCompact(totals.value)} ₽`"
        :hint="`средняя ${formatCompact(totals.avg)} ₽`"
      />
      <StatCard
        label="Свободные средства"
        :value="`${formatCompact(totals.balance)} ₽`"
        :hint="`${formatPrice(totals.freeShare)}% от стоимости`"
      />
      <StatCard
        label="Прибыль / убыток"
        :value="`${formatCompactSigned(totals.profit)} ₽`"
        :hint="`${formatSigned(totals.profitPercent)}% к вложенному в позиции`"
        :tone="totals.profit >= 0 ? 'up' : 'down'"
      />
    </section>

    <form class="filter-bar" aria-label="Фильтры портфелей" @submit.prevent>
      <div class="form-field">
        <label class="form-label" for="pf-name">Название</label>
        <input
          id="pf-name"
          class="form-input"
          type="search"
          placeholder="Поиск по названию"
          v-model="filters.name"
        />
      </div>
      <div class="form-field">
        <label class="form-label" for="pf-balance">Баланс, ₽</label>
        <div class="filter-range">
          <input
            id="pf-balance"
            class="form-input"
            type="number"
            placeholder="от"
            v-model.number="filters.balanceFrom"
          />
          <input
            class="form-input"
            type="number"
            placeholder="до"
            aria-label="Баланс до"
            v-model.number="filters.balanceTo"
          />
        </div>
      </div>
      <div class="form-field">
        <label class="form-label" for="pf-value">Стоимость, ₽</label>
        <div class="filter-range">
          <input
            id="pf-value"
            class="form-input"
            type="number"
            placeholder="от"
            v-model.number="filters.valueFrom"
          />
          <input
            class="form-input"
            type="number"
            placeholder="до"
            aria-label="Стоимость до"
            v-model.number="filters.valueTo"
          />
        </div>
      </div>
      <div v-if="profileStore.isSuperuser" class="form-field">
        <label class="form-label" for="pf-owner">
          Владелец <span class="admin-only-tag">админ</span>
        </label>
        <select id="pf-owner" class="form-select">
          <option value="">Все пользователи</option>
        </select>
      </div>
      <button class="btn btn-ghost" type="button" @click="resetFilters">
        Сбросить
      </button>
    </form>

    <section
      v-if="portfolioList.length"
      class="portfolio-grid"
      aria-label="Список портфелей"
    >
      <PortfolioCard
        v-for="portfolio in filteredPortfolios"
        :key="portfolio.id"
        :portfolio="portfolio"
        :value="portfolio.valueText"
        :change="portfolio.change"
        :is-up="portfolio.isUp"
        :positions-count="portfolio.positionsCount"
        :profit="portfolio.profitText"
        @open-cover="portfolio.cover_image && (coverPortfolio = portfolio)"
        @edit="openForm(portfolio)"
        @delete="deletePortfolio = portfolio"
      />

      <button class="portfolio-card-new" type="button" @click="openForm({})">
        <AppIcon name="plus" large />
        Новый портфель
        <span class="text-sm portfolio-card-new-hint"
          >Стартовый баланс задаётся при создании</span
        >
      </button>
    </section>

    <section v-else class="card">
      <EmptyState
        icon="briefcase"
        title="Портфелей пока нет"
        text="Создайте первый портфель, задайте стартовый баланс и начните торговать."
      >
        <button
          class="btn btn-primary"
          type="button"
          @click="formPortfolio = {}"
        >
          Создать портфель
        </button>
      </EmptyState>
    </section>
  </main>

  <PortfolioFormModal
    v-if="formPortfolio"
    :portfolio="formPortfolio.id ? formPortfolio : null"
    :error="formError"
    :loading="isSaving"
    @close="formPortfolio = null"
    @submit="savePortfolio"
  />
  <ConfirmDeleteModal
    v-if="deletePortfolio"
    :title="`Удалить портфель «${deletePortfolio.name}»?`"
    text="Будут удалены все позиции и сделки портфеля. Действие нельзя отменить."
    @close="deletePortfolio = null"
    @confirm="confirmDelete"
  />
  <ImageModal
    v-if="coverPortfolio"
    :src="coverPortfolio.cover_image ?? ''"
    :caption="`Обложка портфеля «${coverPortfolio.name}»`"
    @close="coverPortfolio = null"
  />
  <TwoFactorModal v-if="isTwoFactorOpen" @close="isTwoFactorOpen = false" />
</template>

<style scoped>
.portfolio-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-4);
}

.portfolio-card-new {
  min-height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  border: 2px dashed var(--color-border-strong);
  border-radius: var(--radius-lg);
  background: transparent;
  font-weight: 600;
  color: var(--color-text-muted);
  cursor: pointer;
}

.portfolio-card-new:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.portfolio-card-new-hint {
  font-weight: 400;
}
</style>
