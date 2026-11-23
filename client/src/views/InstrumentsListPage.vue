<script setup>
import { ref, onBeforeMount, computed } from "vue";
import HeaderNavbar from "@/components/HeaderNavbar.vue";
import AppIcon from "@/components/AppIcon.vue";
import StatCard from "@/components/StatCard.vue";
import ExportButtons from "@/components/ExportButtons.vue";
import InstrumentLogo from "@/components/InstrumentLogo.vue";
import InstrumentFormModal from "@/components/modals/InstrumentFormModal.vue";
import useProfileStore from "@/stores/profileStore";
import axios from "axios";
import { mapInstrument } from "@/utils/InstrumentsMapper";
import ConfirmDeleteModal from "@/components/modals/ConfirmDeleteModal.vue";
import { formatCompact } from "@/utils/format";
import { toFormData, errorText } from "@/utils/requestFormatter";
import { byId, inRange, matchesText } from "@/utils/lists";

const profileStore = useProfileStore();

const instrumentsList = ref([]);
const typesList = ref([]);
const isInstrumentModalOpen = ref(false);

async function loadInstruments() {
  const [instruments, types] = await Promise.all([
    axios.get("/api/instrument/"),
    axios.get("/api/instrumenttype/"),
  ]);
  const typesById = byId(types.data);
  instrumentsList.value = instruments.data.map((i) =>
    mapInstrument(i, typesById),
  );
  typesList.value = types.data;
}

onBeforeMount(loadInstruments);

const emptyFilters = () => ({
  search: "",
  type: "",
  priceFrom: "",
  priceTo: "",
  change: "",
  updatedDate: "",
});
const filters = ref(emptyFilters());

const filteredInstrumentsList = computed(() => {
  const f = filters.value;
  return instrumentsList.value.filter(
    (i) =>
      (matchesText(i.ticker, f.search) || matchesText(i.name, f.search)) &&
      (!f.type || i.typeId === f.type) &&
      inRange(i.rawPrice, f.priceFrom, f.priceTo) &&
      (!f.change || (f.change === "up" ? i.rawChange > 0 : i.rawChange < 0)) &&
      (!f.updatedDate || i.updatedDate === f.updatedDate),
  );
});

function resetFilters() {
  filters.value = emptyFilters();
}

const priceStats = computed(() => {
  const list = instrumentsList.value;
  if (!list.length) return null;
  const prices = list.map((i) => i.rawPrice).sort((a, b) => a - b);
  const mid = Math.floor(prices.length / 2);
  return {
    avg: prices.reduce((sum, p) => sum + p, 0) / prices.length,
    median:
      prices.length % 2 ? prices[mid] : (prices[mid - 1] + prices[mid]) / 2,
    cheapest: list.reduce((a, b) => (b.rawPrice < a.rawPrice ? b : a)),
    priciest: list.reduce((a, b) => (b.rawPrice > a.rawPrice ? b : a)),
  };
});

const upCount = computed(
  () => instrumentsList.value.filter((i) => i.rawChange > 0).length,
);
const downCount = computed(
  () => instrumentsList.value.filter((i) => i.rawChange < 0).length,
);

const countByType = computed(() =>
  typesList.value.map((t) => ({
    name: t.name,
    count: instrumentsList.value.filter((i) => i.typeId === t.id).length,
  })),
);
const editingInstrument = ref(null);
const deletingInstrument = ref(null);
const formError = ref("");
const isSaving = ref(false);

function openCreate() {
  editingInstrument.value = null;
  formError.value = "";
  isInstrumentModalOpen.value = true;
}

function openEdit(instrument) {
  editingInstrument.value = instrument;
  formError.value = "";
  isInstrumentModalOpen.value = true;
}

async function saveInstrument(data) {
  formError.value = "";
  isSaving.value = true;
  try {
    const body = toFormData(data);
    if (editingInstrument.value) {
      await axios.patch(`/api/instrument/${editingInstrument.value.id}/`, body);
    } else {
      await axios.post("/api/instrument/", body);
    }
    isInstrumentModalOpen.value = false;
    await loadInstruments();
  } catch (e) {
    formError.value = errorText(e);
  } finally {
    isSaving.value = false;
  }
}

async function deleteInstrument() {
  await axios.delete(`/api/instrument/${deletingInstrument.value.id}/`);
  deletingInstrument.value = null;
  await loadInstruments();
}
</script>

<template>
  <HeaderNavbar />
  <main class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Инструменты</h1>
        <p class="page-subtitle">
          Акции, криптовалюты и валютные пары по текущей цене
        </p>
      </div>
      <div v-if="profileStore.isSuperuser" class="page-actions">
        <button class="btn btn-primary" type="button" @click="openCreate">
          <AppIcon name="plus" />
          Добавить инструмент
        </button>
      </div>
    </div>

    <section class="stats-grid" aria-label="Статистика">
      <StatCard
        label="Инструментов"
        :value="instrumentsList.length"
        :hint="`по текущему фильтру: ${filteredInstrumentsList.length}`"
      />
      <StatCard
        label="Средняя цена"
        :value="priceStats ? `${formatCompact(priceStats.avg)} ₽` : '-'"
        :hint="
          priceStats ? `медиана ${formatCompact(priceStats.median)} ₽` : ''
        "
      />
      <StatCard
        label="Мин / макс цена"
        :value="
          priceStats
            ? `${formatCompact(priceStats.cheapest.rawPrice)} / ${formatCompact(priceStats.priciest.rawPrice)} ₽`
            : '—'
        "
        :hint="
          priceStats
            ? `${priceStats.cheapest.ticker} / ${priceStats.priciest.ticker}`
            : ''
        "
      />
      <StatCard label="Растут / падают" hint="за последние 24 часа">
        <span class="text-up">{{ upCount }}</span> /
        <span class="text-down">{{ downCount }}</span>
      </StatCard>
      <StatCard
        label="По типам"
        :value="countByType.map((t) => t.count).join(' · ')"
        :hint="countByType.map((t) => t.name.toLowerCase()).join(' · ')"
      />
    </section>

    <section class="card">
      <div class="table-toolbar">
        <h2 class="table-toolbar-title">
          Каталог
          <span class="table-count"
            >{{ filteredInstrumentsList.length }} из
            {{ instrumentsList.length }}</span
          >
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
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th><span class="th-sort is-sorted">Инструмент ▲</span></th>
              <th>Тип</th>
              <th class="col-num"><span class="th-sort">Цена</span></th>
              <th class="col-num"><span class="th-sort">Изм. 24ч</span></th>
              <th class="col-num">Изм. ₽</th>
              <th>Обновлено</th>
              <th class="col-actions">Действия</th>
            </tr>
            <tr class="filter-row">
              <th>
                <label class="visually-hidden" for="f-ticker"
                  >Тикер или название</label
                >
                <input
                  id="f-ticker"
                  v-model="filters.search"
                  class="filter-input"
                  type="search"
                  placeholder="Тикер или название"
                />
              </th>
              <th>
                <label class="visually-hidden" for="f-type">Тип</label>
                <select
                  id="f-type"
                  class="filter-select"
                  v-model="filters.type"
                >
                  <option value="">Все типы</option>
                  <option
                    v-for="type in typesList"
                    :key="type.id"
                    :value="type.id"
                  >
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
                    aria-label="Цена от"
                    v-model.number="filters.priceFrom"
                  />
                  <input
                    class="filter-input"
                    type="number"
                    placeholder="до"
                    aria-label="Цена до"
                    v-model.number="filters.priceTo"
                  />
                </div>
              </th>
              <th>
                <select
                  class="filter-select"
                  aria-label="Изменение"
                  v-model="filters.change"
                >
                  <option value="">Любое</option>
                  <option value="up">Рост</option>
                  <option value="down">Падение</option>
                </select>
              </th>
              <th></th>
              <th>
                <input
                  v-model="filters.updatedDate"
                  class="filter-input"
                  type="date"
                  aria-label="Дата обновления"
                />
              </th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="instrument in filteredInstrumentsList"
              :key="instrument.id"
            >
              <td>
                <div class="cell-instrument">
                  <InstrumentLogo
                    :ticker="instrument.ticker"
                    :logo="instrument.logo"
                    :zoomable="false"
                  />
                  <span class="cell-instrument-text">
                    <router-link
                      :to="{
                        name: 'instrument',
                        params: { id: instrument.id },
                      }"
                      class="cell-instrument-ticker"
                    >
                      {{ instrument.ticker }}
                    </router-link>
                    <span class="cell-instrument-name">{{
                      instrument.name
                    }}</span>
                  </span>
                </div>
              </td>
              <td>
                <span class="badge badge-type">{{ instrument.typeName }}</span>
              </td>
              <td class="col-num num">{{ instrument.price }} ₽</td>
              <td class="col-num">
                <span
                  class="price-change price-change-pill"
                  :class="instrument.isUp ? 'is-up' : 'is-down'"
                >
                  {{ instrument.change }}
                </span>
              </td>
              <td
                class="col-num num"
                :class="instrument.isUp ? 'text-up' : 'text-down'"
              >
                {{ instrument.diff }}
              </td>
              <td class="text-muted text-sm num">{{ instrument.updated }}</td>
              <td class="col-actions">
                <div class="inline-row">
                  <router-link
                    :to="{ name: 'instrument', params: { id: instrument.id } }"
                    class="btn btn-buy btn-sm"
                  >
                    Купить
                  </router-link>
                  <template v-if="profileStore.isSuperuser">
                    <button
                      class="btn btn-ghost btn-sm"
                      type="button"
                      aria-label="Изменить"
                      @click="openEdit(instrument)"
                    >
                      <AppIcon name="edit" />
                    </button>
                    <button
                      class="btn btn-ghost btn-sm"
                      type="button"
                      aria-label="Удалить"
                      @click="deletingInstrument = instrument"
                    >
                      <AppIcon name="trash" />
                    </button>
                  </template>
                </div>
              </td>
            </tr>
            <tr v-if="!filteredInstrumentsList.length">
              <td colspan="7" class="text-muted">
                Ничего не найдено — попробуйте изменить фильтры
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-footer">
        <span
          >Показано {{ filteredInstrumentsList.length }} из
          {{ instrumentsList.length }}</span
        >
      </div>
    </section>
  </main>

  <InstrumentFormModal
    v-if="isInstrumentModalOpen"
    :instrument="editingInstrument"
    :instrument-types="typesList"
    :error="formError"
    :loading="isSaving"
    @close="isInstrumentModalOpen = false"
    @submit="saveInstrument"
  />
  <ConfirmDeleteModal
    v-if="deletingInstrument"
    :title="`Удалить ${deletingInstrument.ticker}?`"
    text="Вместе с инструментом удалятся его история цен, сделки и позиции во всех портфелях."
    @close="deletingInstrument = null"
    @confirm="deleteInstrument"
  />
</template>
