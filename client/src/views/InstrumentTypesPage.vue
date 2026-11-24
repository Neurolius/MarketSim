<script setup>
import { computed, onBeforeMount, ref, watch } from "vue";
import axios from "axios";
import { toFormData, errorText } from "@/utils/requestFormatter";
import { listResults } from "@/utils/lists";
import HeaderNavbar from "@/components/HeaderNavbar.vue";
import AppIcon from "@/components/AppIcon.vue";
import StatCard from "@/components/StatCard.vue";
import ExportButtons from "@/components/ExportButtons.vue";
import InstrumentTypeFormModal from "@/components/modals/InstrumentTypeFormModal.vue";
import ConfirmDeleteModal from "@/components/modals/ConfirmDeleteModal.vue";
import PaginationControls from "@/components/PaginationControls.vue";

const formType = ref(null);
const deleteType = ref(null);
const errorMessage = ref("");
const typesList = ref([]);
const page = ref(1);
const pageSize = 20;
const totalCount = ref(0);
const globalStats = ref({ type_count: 0, instrument_count: 0 });

const emptyFilters = () => ({ id: "", name: "", countFrom: "", countTo: "" });
const filters = ref(emptyFilters());

function filterParams() {
  const params = {};
  if (filters.value.id !== "") params.id = filters.value.id;
  if (filters.value.name) params.name = filters.value.name;
  if (filters.value.countFrom !== "") {
    params.count_from = filters.value.countFrom;
  }
  if (filters.value.countTo !== "") {
    params.count_to = filters.value.countTo;
  }
  return params;
}

const exportParams = computed(filterParams);

async function loadTypes() {
  const params = {
    ...filterParams(),
    page: page.value,
    page_size: pageSize,
  };
  const [r, stats] = await Promise.all([
    axios.get("/api/instrumenttype/", { params }),
    axios.get("/api/instrumenttype/stats/"),
  ]);
  typesList.value = listResults(r.data);
  totalCount.value = r.data.count ?? typesList.value.length;
  globalStats.value = stats.data;
}

onBeforeMount(loadTypes);
watch(page, loadTypes);

const stats = computed(() => {
  const list = typesList.value;
  const total = globalStats.value.instrument_count ?? 0;
  const largest = list.length
    ? list.reduce((a, b) => (b.instruments_count > a.instruments_count ? b : a))
    : null;
  return {
    total,
    avg: globalStats.value.type_count
      ? Math.round(total / globalStats.value.type_count)
      : 0,
    largest,
  };
});

const filteredTypes = computed(() => typesList.value);

watch(
  filters,
  () => {
    if (page.value !== 1) page.value = 1;
    else loadTypes();
  },
  { deep: true },
);

const formError = ref("");
const isSaving = ref(false);

function openForm(type) {
  formError.value = "";
  formType.value = type;
}

async function saveType(data) {
  formError.value = "";
  isSaving.value = true;
  try {
    const id = formType.value.id;
    if (id) await axios.patch(`/api/instrumenttype/${id}/`, toFormData(data));
    else await axios.post("/api/instrumenttype/", toFormData(data));
    formType.value = null;
    if (!id && page.value !== 1) page.value = 1;
    else await loadTypes();
  } catch (e) {
    formError.value = errorText(e);
  } finally {
    isSaving.value = false;
  }
}

async function confirmDelete() {
  errorMessage.value = "";
  try {
    await axios.delete(`/api/instrumenttype/${deleteType.value.id}/`);
    if (page.value > 1 && typesList.value.length === 1) page.value -= 1;
    else await loadTypes();
  } catch (e) {
    errorMessage.value = errorText(e);
  } finally {
    deleteType.value = null;
  }
}
</script>

<template>
  <HeaderNavbar />
  <main class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">
          Типы инструментов
          <span class="badge badge-admin title-badge">Только админ</span>
        </h1>
        <p class="page-subtitle">Справочник для поля «Тип» у инструментов</p>
      </div>
      <div class="page-actions">
        <button class="btn btn-primary" type="button" @click="openForm({})">
          <AppIcon name="plus" />
          Добавить тип
        </button>
      </div>
    </div>

    <section class="stats-grid" aria-label="Статистика">
      <StatCard label="Типов" :value="totalCount" hint="в справочнике" />
      <StatCard
        label="Инструментов"
        :value="stats.total"
        :hint="`в среднем ${stats.avg} на тип`"
      />
      <StatCard
        label="Самый крупный"
        :value="stats.largest?.name ?? '—'"
        :hint="
          stats.largest
            ? `инструментов: ${stats.largest.instruments_count}`
            : ''
        "
      />
    </section>

    <div v-if="errorMessage" class="alert alert-error" role="alert">
      <AppIcon name="alert" />
      <span>{{ errorMessage }}</span>
    </div>

    <section class="card">
      <div class="table-toolbar">
        <h2 class="table-toolbar-title">
          Справочник
          <span class="table-count"
            >{{ filteredTypes.length }} из {{ totalCount }}</span
          >
        </h2>
        <div class="export-actions">
          <ExportButtons
            url="/api/instrumenttype/export/"
            :params="exportParams"
          />
        </div>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th class="col-id">ID</th>
              <th>Название</th>
              <th class="col-num">Инструментов</th>
              <th class="col-actions">Действия</th>
            </tr>
            <tr class="filter-row">
              <th>
                <input
                  class="filter-input"
                  type="number"
                  placeholder="ID"
                  aria-label="ID"
                  v-model.number="filters.id"
                />
              </th>
              <th>
                <input
                  class="filter-input"
                  type="search"
                  placeholder="Название"
                  aria-label="Название"
                  v-model="filters.name"
                />
              </th>
              <th>
                <div class="filter-range">
                  <input
                    class="filter-input"
                    type="number"
                    placeholder="от"
                    aria-label="Инструментов от"
                    v-model.number="filters.countFrom"
                  />
                  <input
                    class="filter-input"
                    type="number"
                    placeholder="до"
                    aria-label="Инструментов до"
                    v-model.number="filters.countTo"
                  />
                </div>
              </th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="type in filteredTypes" :key="type.id">
              <td class="num text-muted">{{ type.id }}</td>
              <td>
                <strong>{{ type.name }}</strong>
              </td>
              <td class="col-num num">{{ type.instruments_count }}</td>
              <td class="col-actions">
                <button
                  class="btn btn-ghost btn-sm"
                  type="button"
                  @click="openForm(type)"
                >
                  <AppIcon name="edit" />
                  Изменить
                </button>
                <button
                  class="btn btn-danger btn-sm"
                  type="button"
                  :disabled="type.instruments_count > 0"
                  :title="
                    type.instruments_count > 0
                      ? 'К типу привязаны инструменты'
                      : ''
                  "
                  @click="deleteType = type"
                >
                  <AppIcon name="trash" />
                  Удалить
                </button>
              </td>
            </tr>
            <tr v-if="!filteredTypes.length">
              <td colspan="4" class="text-muted">Ничего не найдено</td>
            </tr>
          </tbody>
        </table>
      </div>
      <PaginationControls
        v-model:page="page"
        :count="totalCount"
        :page-size="pageSize"
      />
    </section>
  </main>

  <InstrumentTypeFormModal
    v-if="formType"
    :instrument-type="formType.id ? formType : null"
    :error="formError"
    :loading="isSaving"
    @close="formType = null"
    @submit="saveType"
  />
  <ConfirmDeleteModal
    v-if="deleteType"
    :title="`Удалить тип «${deleteType.name}»?`"
    text="Удалить можно только тип, к которому не привязаны инструменты."
    @close="deleteType = null"
    @confirm="confirmDelete"
  />
</template>

<style scoped>
.title-badge {
  vertical-align: middle;
}

.col-id {
  width: 80px;
}
</style>
