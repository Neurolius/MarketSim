<script setup>
import { ref } from 'vue'
import HeaderNavbar from '@/components/HeaderNavbar.vue'
import AppIcon from '@/components/AppIcon.vue'
import StatCard from '@/components/StatCard.vue'
import ExportButtons from '@/components/ExportButtons.vue'
import PortfolioCard from '@/components/PortfolioCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import PortfolioFormModal from '@/components/modals/PortfolioFormModal.vue'
import ConfirmDeleteModal from '@/components/modals/ConfirmDeleteModal.vue'
import TwoFactorModal from '@/components/modals/TwoFactorModal.vue'
import ImageModal from '@/components/modals/ImageModal.vue'
import useProfileStore from '@/stores/profileStore'

const profileStore = useProfileStore()

// открытые модалки: форма (null — закрыта, {} — новый портфель), удаление, обложка, 2FA
const formPortfolio = ref(null)
const deletePortfolio = ref(null)
const coverPortfolio = ref(null)
const isTwoFactorOpen = ref(false)

// моковые данные для верстки — заменить на данные из API
const portfolios = [
  { id: 1, name: 'Основной', balance: '182 400,00', cover_image: null, owner: 'nikita', value: '742 310,00 ₽', change: '+3,1%', isUp: true, positionsCount: 6, profit: '+22 310,00 ₽' },
  { id: 2, name: 'Крипта', balance: '64 000,00', cover_image: null, owner: 'nikita', value: '318 905,40 ₽', change: '−1,4%', isUp: false, positionsCount: 3, profit: '−4 512,60 ₽' },
  { id: 3, name: 'Валютный', balance: '66 000,00', cover_image: null, owner: 'nikita', value: '187 315,00 ₽', change: '+0,6%', isUp: true, positionsCount: 2, profit: '+1 115,00 ₽' },
]
</script>

<template>
  <HeaderNavbar />
  <main class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Портфели</h1>
        <p class="page-subtitle">Виртуальные счета с собственным балансом и позициями</p>
      </div>
      <div class="page-actions">
        <ExportButtons :small="false" />
        <button class="btn btn-primary" type="button" @click="formPortfolio = {}">
          <AppIcon name="plus" />
          Создать портфель
        </button>
      </div>
    </div>

    <section class="stats-grid" aria-label="Статистика">
      <StatCard label="Портфелей" value="3" hint="у всех пользователей: 41" />
      <StatCard label="Общая стоимость" value="1 248 530 ₽" hint="средняя 416 177 ₽" />
      <StatCard label="Свободные средства" value="312 400 ₽" hint="25% от стоимости" />
      <StatCard label="Прибыль / убыток" value="+48 530 ₽" hint="+4,04% к стартовому балансу" tone="up" />
    </section>

    <form class="filter-bar" aria-label="Фильтры портфелей" @submit.prevent>
      <div class="form-field">
        <label class="form-label" for="pf-name">Название</label>
        <input id="pf-name" class="form-input" type="search" placeholder="Поиск по названию" />
      </div>
      <div class="form-field">
        <label class="form-label" for="pf-balance">Баланс, ₽</label>
        <div class="filter-range">
          <input id="pf-balance" class="form-input" type="number" placeholder="от" />
          <input class="form-input" type="number" placeholder="до" aria-label="Баланс до" />
        </div>
      </div>
      <div class="form-field">
        <label class="form-label" for="pf-value">Стоимость, ₽</label>
        <div class="filter-range">
          <input id="pf-value" class="form-input" type="number" placeholder="от" />
          <input class="form-input" type="number" placeholder="до" aria-label="Стоимость до" />
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
      <button class="btn btn-ghost" type="reset">Сбросить</button>
    </form>

    <section v-if="portfolios.length" class="portfolio-grid" aria-label="Список портфелей">
      <PortfolioCard
        v-for="portfolio in portfolios"
        :key="portfolio.id"
        :portfolio="portfolio"
        :value="portfolio.value"
        :change="portfolio.change"
        :is-up="portfolio.isUp"
        :positions-count="portfolio.positionsCount"
        :profit="portfolio.profit"
        :owner="profileStore.isSuperuser ? portfolio.owner : null"
        @open-cover="coverPortfolio = portfolio"
        @edit="formPortfolio = portfolio"
        @delete="deletePortfolio = portfolio"
      />

      <button class="portfolio-card-new" type="button" @click="formPortfolio = {}">
        <AppIcon name="plus" large />
        Новый портфель
        <span class="text-sm portfolio-card-new-hint">Стартовый баланс задаётся при создании</span>
      </button>
    </section>

    <section v-else class="card">
      <EmptyState
        icon="briefcase"
        title="Портфелей пока нет"
        text="Создайте первый портфель, задайте стартовый баланс и начните торговать."
      >
        <button class="btn btn-primary" type="button" @click="formPortfolio = {}">
          Создать портфель
        </button>
      </EmptyState>
    </section>
  </main>

  <PortfolioFormModal
    v-if="formPortfolio"
    :portfolio="formPortfolio.id ? formPortfolio : null"
    @close="formPortfolio = null"
  />
  <ConfirmDeleteModal
    v-if="deletePortfolio"
    :title="`Удалить портфель «${deletePortfolio.name}»?`"
    text="Будут удалены все позиции и сделки портфеля. Действие нельзя отменить."
    @close="deletePortfolio = null"
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
