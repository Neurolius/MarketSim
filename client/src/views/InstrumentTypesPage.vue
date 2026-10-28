<script setup>
import { ref } from 'vue'
import HeaderNavbar from '@/components/HeaderNavbar.vue'
import AppIcon from '@/components/AppIcon.vue'
import StatCard from '@/components/StatCard.vue'
import ExportButtons from '@/components/ExportButtons.vue'
import InstrumentTypeFormModal from '@/components/modals/InstrumentTypeFormModal.vue'
import ConfirmDeleteModal from '@/components/modals/ConfirmDeleteModal.vue'

// открытые модалки: форма (null — закрыта, {} — новый тип) и удаление
const formType = ref(null)
const deleteType = ref(null)
const errorMessage = ref('')

// моковые данные для верстки — заменить на данные из API
const instrumentTypes = [
  { id: 1, name: 'Акция', instrumentsCount: 26 },
  { id: 2, name: 'Криптовалюта', instrumentsCount: 14 },
  { id: 3, name: 'Валюта', instrumentsCount: 8 },
]
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
        <button class="btn btn-primary" type="button" @click="formType = {}">
          <AppIcon name="plus" />
          Добавить тип
        </button>
      </div>
    </div>

    <section class="stats-grid" aria-label="Статистика">
      <StatCard label="Типов" value="3" hint="в справочнике" />
      <StatCard label="Инструментов" value="48" hint="в среднем 16 на тип" />
      <StatCard label="Самый крупный" value="Акция" hint="26 инструментов" />
    </section>

    <!-- пример: «Не удалось удалить «Валюта». К этому типу привязано 8 инструментов — сначала измените их тип.» -->
    <div v-if="errorMessage" class="alert alert-error" role="alert">
      <AppIcon name="alert" />
      <span>{{ errorMessage }}</span>
    </div>

    <section class="card">
      <div class="table-toolbar">
        <h2 class="table-toolbar-title">
          Справочник <span class="table-count">{{ instrumentTypes.length }}</span>
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
              <th><input class="filter-input" type="number" placeholder="ID" aria-label="ID" /></th>
              <th>
                <input class="filter-input" type="search" placeholder="Название" aria-label="Название" />
              </th>
              <th>
                <div class="filter-range">
                  <input class="filter-input" type="number" placeholder="от" aria-label="Инструментов от" />
                  <input class="filter-input" type="number" placeholder="до" aria-label="Инструментов до" />
                </div>
              </th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="type in instrumentTypes" :key="type.id">
              <td class="num text-muted">{{ type.id }}</td>
              <td><strong>{{ type.name }}</strong></td>
              <td class="col-num num">{{ type.instrumentsCount }}</td>
              <td class="col-actions">
                <button class="btn btn-ghost btn-sm" type="button" @click="formType = type">
                  <AppIcon name="edit" />
                  Изменить
                </button>
                <button class="btn btn-danger btn-sm" type="button" @click="deleteType = type">
                  <AppIcon name="trash" />
                  Удалить
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>

  <InstrumentTypeFormModal
    v-if="formType"
    :instrument-type="formType.id ? formType : null"
    @close="formType = null"
  />
  <ConfirmDeleteModal
    v-if="deleteType"
    :title="`Удалить тип «${deleteType.name}»?`"
    text="Удалить можно только тип, к которому не привязаны инструменты."
    @close="deleteType = null"
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
