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

const profileStore = useProfileStore();

const isInstrumentModalOpen = ref(false);

const instrumentsList = ref([]);
const typesList = ref([]);
const filtersType = ref("");

onBeforeMount(async () => {
  const [instruments, types] = await Promise.all([
    axios.get("/api/instrument/"),
    axios.get("/api/instrumenttype/"),
  ]);
  const typesById = Object.fromEntries(types.data.map((t) => [t.id, t]));
  instrumentsList.value = instruments.data.map((i) =>
    mapInstrument(i, typesById),
  );
  typesList.value = types.data;
});

const instrumentsCount = computed(() => instrumentsList.value.length);
const filteredInstrumentsList = computed(() =>
  instrumentsList.value.filter(
    (i) => !filtersType.value || i.typeId === filtersType.value,
  ),
);
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
        <button
          class="btn btn-primary"
          type="button"
          @click="isInstrumentModalOpen = true"
        >
          <AppIcon name="plus" />
          Добавить инструмент
        </button>
      </div>
    </div>

    <section class="stats-grid" aria-label="Статистика">
      <StatCard
        label="Инструментов"
        :value="instrumentsCount"
        :hint="`по текущему фильтру: ${filteredInstrumentsList.length}`"
      />
      <StatCard
        label="Средняя цена"
        value="412 830 ₽"
        hint="медиана 186,40 ₽"
      />
      <StatCard
        label="Мин / макс цена"
        value="0,87 / 8,9 млн ₽"
        hint="DOGE / BTC"
      />
      <StatCard label="Растут / падают" hint="за последние 24 часа">
        <span class="text-up">31</span> / <span class="text-down">17</span>
      </StatCard>
      <StatCard
        label="По типам"
        value="26 · 14 · 8"
        hint="акции · крипто · валюты"
      />
    </section>

    <section class="card">
      <div class="table-toolbar">
        <h2 class="table-toolbar-title">
          Каталог <span class="table-count">12 из 48</span>
        </h2>
        <div class="export-actions">
          <button class="btn btn-ghost btn-sm" type="button">
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
                  class="filter-input"
                  type="search"
                  placeholder="Тикер или название"
                />
              </th>
              <th>
                <label class="visually-hidden" for="f-type">Тип</label>
                <select id="f-type" class="filter-select" v-model="filtersType">
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
                  />
                  <input
                    class="filter-input"
                    type="number"
                    placeholder="до"
                    aria-label="Цена до"
                  />
                </div>
              </th>
              <th>
                <select class="filter-select" aria-label="Изменение">
                  <option value="">Любое</option>
                  <option value="up">Рост</option>
                  <option value="down">Падение</option>
                </select>
              </th>
              <th></th>
              <th>
                <input
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
                    :type="instrument.type"
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
                <router-link
                  :to="{ name: 'instrument', params: { id: instrument.id } }"
                  class="btn btn-buy btn-sm"
                >
                  Купить
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-footer">
        <span>Показано 1–10 из 12</span>
        <nav class="pagination" aria-label="Страницы">
          <button class="pagination-btn" type="button" aria-label="Предыдущая">
            ‹
          </button>
          <button class="pagination-btn is-active" type="button">1</button>
          <button class="pagination-btn" type="button">2</button>
          <button class="pagination-btn" type="button" aria-label="Следующая">
            ›
          </button>
        </nav>
      </div>
    </section>
  </main>

  <InstrumentFormModal
    v-if="isInstrumentModalOpen"
    :instrument-types="instrumentTypes"
    @close="isInstrumentModalOpen = false"
  />
</template>
