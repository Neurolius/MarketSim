<script setup>
import { computed, onBeforeMount, ref } from "vue";
import axios from "axios";
import { toFormData, errorText } from "@/utils/requestFormatter";
import { inRange, matchesText } from "@/utils/lists";
import HeaderNavbar from "@/components/HeaderNavbar.vue";
import AppIcon from "@/components/AppIcon.vue";
import StatCard from "@/components/StatCard.vue";
import ExportButtons from "@/components/ExportButtons.vue";
import InstrumentTypeFormModal from "@/components/modals/InstrumentTypeFormModal.vue";
import ConfirmDeleteModal from "@/components/modals/ConfirmDeleteModal.vue";

const formType = ref(null);
const deleteType = ref(null);
const errorMessage = ref("");
const typesList = ref([]);

async function loadTypes() {
  const r = await axios.get("/api/instrumenttype/");
  typesList.value = r.data;
}

onBeforeMount(loadTypes);

const stats = computed(() => {
  const list = typesList.value;
  const total = list.reduce((sum, t) => sum + t.instruments_count, 0);
  const largest = list.length
    ? list.reduce((a, b) => (b.instruments_count > a.instruments_count ? b : a))
    : null;
  return {
    total,
    avg: list.length ? Math.round(total / list.length) : 0,
    largest,
  };
});

const emptyFilters = () => ({ id: "", name: "", countFrom: "", countTo: "" });
const filters = ref(emptyFilters());

const filteredTypes = computed(() => {
  const f = filters.value;
  return typesList.value.filter(
    (t) =>
      (f.id === "" || t.id === f.id) &&
      matchesText(t.name, f.name) &&
      inRange(t.instruments_count, f.countFrom, f.countTo),
  );
});

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
    await loadTypes();
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
    await loadTypes();
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
      <StatCard label="Типов" :value="typesList.length" hint="в справочнике" />
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
          <span class="table-count">{{ filteredTypes.length }}</span>
        </h2>
        <div class="export-actions">
          <ExportButtons />
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
