<script setup>
import { ref } from 'vue'
import HeaderNavbar from '@/components/HeaderNavbar.vue'
import AppIcon from '@/components/AppIcon.vue'
import StatCard from '@/components/StatCard.vue'
import ExportButtons from '@/components/ExportButtons.vue'
import InstrumentLogo from '@/components/InstrumentLogo.vue'
import PortfolioFormModal from '@/components/modals/PortfolioFormModal.vue'
import ConfirmDeleteModal from '@/components/modals/ConfirmDeleteModal.vue'
import ImageModal from '@/components/modals/ImageModal.vue'
import SellModal from '@/components/modals/SellModal.vue'
import TradeEditModal from '@/components/modals/TradeEditModal.vue'

const isEditOpen = ref(false)
const isDeleteOpen = ref(false)
const imageModal = ref(null)
const sellPosition = ref(null)
const editTrade = ref(null)

const orderTypeLabels = { buy: 'Покупка', sell: 'Продажа' }
const executionTypeLabels = { market: 'Рыночная', limit: 'Лимитная' }
const statusLabels = { pending: 'Ожидает', executed: 'Исполнена', cancelled: 'Отменена' }

// моковые данные для верстки — заменить на данные из API
const portfolio = { id: 1, name: 'Основной', balance: '182 400,00', cover_image: null }
const positions = [
  { id: 1, instrument_info: { id: 7, ticker: 'SBER', name: 'Сбербанк', current_price: '312,45' }, type: 'stock', typeName: 'Акция', quantity: '150', average_price: '276,30', value: '46 867,50', profit: '+5 422,50 ₽', profitPercent: '+13,08%', isUp: true },
  { id: 2, instrument_info: { id: 10, ticker: 'YDEX', name: 'Яндекс', current_price: '4 186,50' }, type: 'stock', typeName: 'Акция', quantity: '40', average_price: '3 902,00', value: '167 460,00', profit: '+11 380,00 ₽', profitPercent: '+7,29%', isUp: true },
  { id: 3, instrument_info: { id: 2, ticker: 'ETH', name: 'Ethereum', current_price: '312 450,00' }, type: 'crypto', typeName: 'Криптовалюта', quantity: '0,5', average_price: '298 100,00', value: '156 225,00', profit: '+7 175,00 ₽', profitPercent: '+4,81%', isUp: true },
  { id: 4, instrument_info: { id: 6, ticker: 'GMKN', name: 'Норникель', current_price: '142,36' }, type: 'stock', typeName: 'Акция', quantity: '300', average_price: '141,80', value: '42 708,00', profit: '+168,00 ₽', profitPercent: '+0,39%', isUp: true },
  { id: 5, instrument_info: { id: 5, ticker: 'LKOH', name: 'Лукойл', current_price: '6 912,00' }, type: 'stock', typeName: 'Акция', quantity: '15', average_price: '7 010,00', value: '103 680,00', profit: '−1 470,00 ₽', profitPercent: '−1,40%', isUp: false },
  { id: 6, instrument_info: { id: 4, ticker: 'GAZP', name: 'Газпром', current_price: '128,90' }, type: 'stock', typeName: 'Акция', quantity: '333', average_price: '130,10', value: '42 923,70', profit: '−399,60 ₽', profitPercent: '−0,92%', isUp: false },
]
const trades = [
  { id: 1, created_at: '2026-10-21T14:32:00', instrument: 7, instrument_info: { ticker: 'SBER' }, order_type: 'buy', execution_type: 'market', quantity: '10', price: null, execution_price: '312,45', status: 'executed', image: '' },
  { id: 2, created_at: '2026-10-21T11:05:00', instrument: 10, instrument_info: { ticker: 'YDEX' }, order_type: 'sell', execution_type: 'limit', quantity: '5', price: '4 300,00', execution_price: null, status: 'pending', image: null },
  { id: 3, created_at: '2026-10-20T11:10:00', instrument: 5, instrument_info: { ticker: 'LKOH' }, order_type: 'buy', execution_type: 'limit', quantity: '2', price: '6 800,00', execution_price: null, status: 'cancelled', image: null },
  { id: 4, created_at: '2026-10-19T16:22:00', instrument: 4, instrument_info: { ticker: 'GAZP' }, order_type: 'sell', execution_type: 'market', quantity: '100', price: null, execution_price: '128,90', status: 'executed', image: '' },
]
</script>

<template>
  <HeaderNavbar />
  <main class="page">
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
        @click="imageModal = { src: portfolio.cover_image ?? '', caption: `Обложка портфеля «${portfolio.name}»` }"
      >
        <img v-if="portfolio.cover_image" :src="portfolio.cover_image" alt="" />
      </button>
      <div class="portfolio-hero-body">
        <div>
          <h1 class="page-title">{{ portfolio.name }}</h1>
          <p class="page-subtitle">Создан 02.09.2026 · владелец nikita</p>
        </div>
        <div class="page-actions">
          <button class="btn btn-secondary" type="button" @click="isEditOpen = true">
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
      <StatCard label="Стоимость" value="742 310,00 ₽" hint="баланс + позиции" />
      <StatCard label="Баланс" :value="`${portfolio.balance} ₽`" hint="доступно для покупок" />
      <StatCard label="В позициях" value="559 910,00 ₽" hint="6 инструментов" />
      <StatCard label="П/У по позициям" value="+22 310,00 ₽" hint="+4,15% от вложенного" tone="up" />
      <StatCard label="Сделок" value="24" hint="2 ожидают исполнения" />
    </section>

    <!-- Позиции -->
    <section class="card">
      <div class="table-toolbar">
        <h2 class="table-toolbar-title">
          Позиции <span class="table-count">{{ positions.length }}</span>
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
              <th class="col-num"><span class="th-sort is-sorted">П/У ▼</span></th>
              <th class="col-actions"></th>
            </tr>
            <tr class="filter-row">
              <th>
                <input class="filter-input" type="search" placeholder="Тикер" aria-label="Тикер" />
              </th>
              <th>
                <select class="filter-select" aria-label="Тип">
                  <option value="">Все</option>
                </select>
              </th>
              <th>
                <div class="filter-range">
                  <input class="filter-input" type="number" placeholder="от" aria-label="Количество от" />
                  <input class="filter-input" type="number" placeholder="до" aria-label="Количество до" />
                </div>
              </th>
              <th></th>
              <th></th>
              <th>
                <div class="filter-range">
                  <input class="filter-input" type="number" placeholder="от" aria-label="Стоимость от" />
                  <input class="filter-input" type="number" placeholder="до" aria-label="Стоимость до" />
                </div>
              </th>
              <th>
                <select class="filter-select" aria-label="Результат">
                  <option value="">Все</option>
                  <option value="profit">Прибыль</option>
                  <option value="loss">Убыток</option>
                </select>
              </th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="position in positions" :key="position.id">
              <td>
                <div class="cell-instrument">
                  <InstrumentLogo
                    :ticker="position.instrument_info.ticker"
                    :logo="position.instrument_info.logo"
                    :type="position.type"
                  />
                  <span class="cell-instrument-text">
                    <router-link
                      :to="{ name: 'instrument', params: { id: position.instrument_info.id } }"
                      class="cell-instrument-ticker"
                    >
                      {{ position.instrument_info.ticker }}
                    </router-link>
                    <span class="cell-instrument-name">{{ position.instrument_info.name }}</span>
                  </span>
                </div>
              </td>
              <td><span class="badge badge-type">{{ position.typeName }}</span></td>
              <td class="col-num num">{{ position.quantity }}</td>
              <td class="col-num num">{{ position.average_price }} ₽</td>
              <td class="col-num num">{{ position.instrument_info.current_price }} ₽</td>
              <td class="col-num num">{{ position.value }} ₽</td>
              <td class="col-num">
                <div class="price-change" :class="position.isUp ? 'is-up' : 'is-down'">
                  {{ position.profit }}
                </div>
                <div class="price-change text-xs" :class="position.isUp ? 'is-up' : 'is-down'">
                  {{ position.profitPercent }}
                </div>
              </td>
              <td class="col-actions">
                <button class="btn btn-sell btn-sm" type="button" @click="sellPosition = position">
                  Продать
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-footer">
        <span>Итого в позициях: <strong class="num">559 864,20 ₽</strong></span>
        <span>Общий П/У: <span class="price-change is-up">+22 275,90 ₽</span></span>
      </div>
    </section>

    <!-- Сделки портфеля -->
    <section class="card">
      <div class="table-toolbar">
        <h2 class="table-toolbar-title">Сделки портфеля <span class="table-count">24</span></h2>
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
              <th><input class="filter-input" type="date" aria-label="Дата создания" /></th>
              <th>
                <input class="filter-input" type="search" placeholder="Тикер" aria-label="Тикер" />
              </th>
              <th>
                <select class="filter-select" aria-label="Операция">
                  <option value="">Все</option>
                  <option value="buy">Покупка</option>
                  <option value="sell">Продажа</option>
                </select>
              </th>
              <th>
                <select class="filter-select" aria-label="Исполнение">
                  <option value="">Все</option>
                  <option value="market">Рыночная</option>
                  <option value="limit">Лимитная</option>
                </select>
              </th>
              <th></th>
              <th></th>
              <th></th>
              <th>
                <select class="filter-select" aria-label="Статус">
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
            <tr v-for="trade in trades" :key="trade.id">
              <td class="num">{{ new Date(trade.created_at).toLocaleString() }}</td>
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
                <span class="badge badge-exec">{{ executionTypeLabels[trade.execution_type] }}</span>
              </td>
              <td class="col-num num">{{ trade.quantity }}</td>
              <td class="col-num num" :class="{ 'text-muted': !trade.price }">
                {{ trade.price ? `${trade.price} ₽` : '—' }}
              </td>
              <td class="col-num num" :class="{ 'text-muted': !trade.execution_price }">
                {{ trade.execution_price ? `${trade.execution_price} ₽` : '—' }}
              </td>
              <td>
                <span class="badge" :class="`badge-${trade.status}`">
                  {{ statusLabels[trade.status] }}
                </span>
              </td>
              <td>
                <button
                  v-if="trade.image !== null"
                  class="row-thumb"
                  type="button"
                  aria-label="Открыть изображение сделки"
                  @click="imageModal = { src: trade.image, caption: `Сделка ${trade.instrument_info.ticker}` }"
                ></button>
                <span v-else class="text-muted">—</span>
              </td>
              <td class="col-actions">
                <template v-if="trade.status === 'pending'">
                  <button class="btn btn-ghost btn-sm" type="button" @click="editTrade = trade">
                    Изменить
                  </button>
                  <button class="btn btn-danger btn-sm" type="button">Отменить</button>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-footer">
        <span>Показано 4 из 24</span>
        <nav class="pagination" aria-label="Страницы">
          <button class="pagination-btn is-active" type="button">1</button>
          <button class="pagination-btn" type="button">2</button>
          <button class="pagination-btn" type="button">3</button>
        </nav>
      </div>
    </section>
  </main>

  <PortfolioFormModal v-if="isEditOpen" :portfolio="portfolio" @close="isEditOpen = false" />
  <ConfirmDeleteModal
    v-if="isDeleteOpen"
    :title="`Удалить портфель «${portfolio.name}»?`"
    :text="`Будут удалены ${positions.length} позиций и все сделки портфеля. Действие нельзя отменить.`"
    @close="isDeleteOpen = false"
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
    @close="sellPosition = null"
  />
  <TradeEditModal v-if="editTrade" :trade="editTrade" @close="editTrade = null" />
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
