<script setup>
import { computed, onBeforeMount, ref, watch } from "vue";
import HeaderNavbar from "@/components/HeaderNavbar.vue";
import AppIcon from "@/components/AppIcon.vue";
import StatCard from "@/components/StatCard.vue";
import ExportButtons from "@/components/ExportButtons.vue";
import PortfolioCard from "@/components/PortfolioCard.vue";
import EmptyState from "@/components/EmptyState.vue";
import PortfolioFormModal from "@/components/modals/PortfolioFormModal.vue";
import ConfirmDeleteModal from "@/components/modals/ConfirmDeleteModal.vue";
import ImageModal from "@/components/modals/ImageModal.vue";
import useProfileStore from "@/stores/profileStore";

import axios from "axios";
import {
  formatPrice,
  formatSigned,
  formatCompact,
  formatCompactSigned,
} from "@/utils/format";
import { toFormData, errorText } from "@/utils/apiHelper";
import { listResults } from "@/utils/lists";
import PaginationControls from "@/components/PaginationControls.vue";

const profileStore = useProfileStore();

const formPortfolio = ref(null);
const deletePortfolio = ref(null);
const coverPortfolio = ref(null);

const portfolioList = ref([]);
const usersList = ref([]);
const page = ref(1);
const pageSize = 20;
const totalCount = ref(0);
const portfolioStats = ref(null);

function filterParams() {
  const params = {};
  if (profileStore.isSuperuser && filters.value.userId) {
    params.user = filters.value.userId;
  }
  if (filters.value.name) params.search = filters.value.name;
  if (filters.value.balanceFrom !== "") {
    params.balance_from = filters.value.balanceFrom;
  }
  if (filters.value.balanceTo !== "") {
    params.balance_to = filters.value.balanceTo;
  }
  if (filters.value.valueFrom !== "") {
    params.value_from = filters.value.valueFrom;
  }
  if (filters.value.valueTo !== "") {
    params.value_to = filters.value.valueTo;
  }
  return params;
}

const exportParams = computed(filterParams);

async function loadPortfolios() {
  const params = {
    ...filterParams(),
    page: page.value,
    page_size: pageSize,
  };
  const requests = [
    axios.get("/api/portfolio/", { params }),
    axios.get("/api/portfolio/stats/", { params: { user: params.user } }),
  ];
  if (profileStore.isSuperuser) {
    requests.push(axios.get("/api/profile/users/"));
  }

  const [portfolios, stats, users] = await Promise.all(requests);
  portfolioList.value = listResults(portfolios.data);
  totalCount.value = portfolios.data.count ?? portfolioList.value.length;
  portfolioStats.value = stats.data;
  if (users) usersList.value = users.data;
}

onBeforeMount(loadPortfolios);
watch(page, loadPortfolios);

const portfolioRows = computed(() =>
  portfolioList.value.map((p) => {
    const positionsValue = Number(p.positions_value ?? 0);
    const cost = Number(p.positions_cost ?? 0);
    const profit = positionsValue - cost;
    const percent = cost ? (profit / cost) * 100 : 0;
    return {
      ...p,
      positionsCount: Number(p.positions_count ?? 0),
      valueText: `${formatPrice(p.total_value)} ₽`,
      profitText: `${formatSigned(profit)} ₽`,
      change: cost ? `${formatSigned(percent)}%` : "",
      isUp: profit >= 0,
    };
  }),
);

const totals = computed(() => {
  const stats = portfolioStats.value ?? {};
  return {
    value: Number(stats.totalValue ?? 0),
    balance: Number(stats.balance ?? 0),
    profit: Number(stats.profit ?? 0),
    avg: Number(stats.avg ?? 0),
    freeShare: Number(stats.freeShare ?? 0),
    profitPercent: Number(stats.profitPercent ?? 0),
  };
});

const emptyFilters = () => ({
  name: "",
  balanceFrom: "",
  balanceTo: "",
  valueFrom: "",
  valueTo: "",
  userId: "",
});
const filters = ref(emptyFilters());

watch(
  filters,
  () => {
    if (page.value !== 1) page.value = 1;
    else loadPortfolios();
  },
  { deep: true },
);

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
    if (!id && page.value !== 1) page.value = 1;
    else await loadPortfolios();
  } catch (e) {
    formError.value = errorText(e);
  } finally {
    isSaving.value = false;
  }
}

async function confirmDelete() {
  try {
    await axios.delete(`/api/portfolio/${deletePortfolio.value.id}/`);
    deletePortfolio.value = null;
    if (page.value > 1 && portfolioList.value.length === 1) page.value -= 1;
    else await loadPortfolios();
  } catch (e) {
    alert(errorText(e));
  }
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
        <ExportButtons
          :small="false"
          url="/api/portfolio/export/"
          :params="exportParams"
        />
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
        :value="totalCount"
        :hint="`по фильтру: ${portfolioRows.length}`"
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

    <form class="filter-bar" @submit.prevent>
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
            v-model.number="filters.valueTo"
          />
        </div>
      </div>
      <div v-if="profileStore.isSuperuser" class="form-field">
        <label class="form-label" for="pf-owner">
          Владелец <span class="admin-only-tag">админ</span>
        </label>
        <select id="pf-owner" v-model="filters.userId" class="form-select">
          <option value="">Все пользователи</option>
          <option v-for="user in usersList" :key="user.id" :value="user.id">
            {{ user.username }} (ID: {{ user.id }})
          </option>
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
        v-for="portfolio in portfolioRows"
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
    <PaginationControls
      v-model:page="page"
      :count="totalCount"
      :page-size="pageSize"
    />
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
    :images="[{ image: coverPortfolio.cover_image ?? '' }]"
    :caption="`Обложка портфеля «${coverPortfolio.name}»`"
    @close="coverPortfolio = null"
  />
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
