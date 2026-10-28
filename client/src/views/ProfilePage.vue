<script setup>
import HeaderNavbar from '@/components/HeaderNavbar.vue'
import StatCard from '@/components/StatCard.vue'
import ExportButtons from '@/components/ExportButtons.vue'
import TwoFactorCard from '@/components/TwoFactorCard.vue'
import useProfileStore from '@/stores/profileStore'

const profileStore = useProfileStore()
const username = profileStore.userName

const orderTypeLabels = { buy: 'Покупка', sell: 'Продажа' }
const executionTypeLabels = { market: 'Рыночная', limit: 'Лимитная' }
const statusLabels = { pending: 'Ожидает', executed: 'Исполнена', cancelled: 'Отменена' }

// моковые данные для верстки — заменить на данные из API
const trades = [
  { id: 1, created: '21.10, 14:32', executed: '21.10, 14:32', user: 'nikita', portfolio: 1, portfolioName: 'Основной', ticker: 'SBER', order_type: 'buy', execution_type: 'market', quantity: '10', price: '312,45 ₽', total: '3 124,50 ₽', status: 'executed' },
  { id: 2, created: '21.10, 12:05', executed: null, user: 'nikita', portfolio: 2, portfolioName: 'Крипта', ticker: 'BTC', order_type: 'sell', execution_type: 'limit', quantity: '0,05', price: '9 100 000 ₽', total: '455 000,00 ₽', status: 'pending' },
  { id: 3, created: '20.10, 18:47', executed: '20.10, 18:47', user: 'student01', portfolio: 4, portfolioName: 'Учебный', ticker: 'USD/RUB', order_type: 'buy', execution_type: 'market', quantity: '500', price: '81,20 ₽', total: '40 600,00 ₽', status: 'executed' },
  { id: 4, created: '20.10, 11:10', executed: null, user: 'nikita', portfolio: 1, portfolioName: 'Основной', ticker: 'LKOH', order_type: 'buy', execution_type: 'limit', quantity: '2', price: '6 800,00 ₽', total: '13 600,00 ₽', status: 'cancelled' },
  { id: 5, created: '19.10, 16:22', executed: '19.10, 16:22', user: 'nikita', portfolio: 1, portfolioName: 'Основной', ticker: 'GAZP', order_type: 'sell', execution_type: 'market', quantity: '100', price: '128,90 ₽', total: '12 890,00 ₽', status: 'executed' },
  { id: 6, created: '18.10, 10:03', executed: '18.10, 15:40', user: 'nikita', portfolio: 2, portfolioName: 'Крипта', ticker: 'ETH', order_type: 'buy', execution_type: 'limit', quantity: '0,2', price: '295 000,00 ₽', total: '59 000,00 ₽', status: 'executed' },
]
</script>

<template>
  <HeaderNavbar />
  <main class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Профиль</h1>
        <p class="page-subtitle">
          Данные аккаунта, двухфакторная защита и полная история сделок
        </p>
      </div>
    </div>

    <div class="split-side">
      <div class="stack">
        <section class="card profile-card">
          <span class="avatar avatar-lg">{{ username?.slice(0, 2).toUpperCase() }}</span>
          <h2 class="profile-name">{{ username }}</h2>
          <span v-if="profileStore.isSuperuser" class="badge badge-admin">Суперпользователь</span>
          <div class="info-list">
            <div class="info-list-row">
              <span class="text-muted">Email</span>
              <span>—</span>
            </div>
            <div class="info-list-row">
              <span class="text-muted">Регистрация</span>
              <span class="num">—</span>
            </div>
            <div class="info-list-row">
              <span class="text-muted">Последний вход</span>
              <span class="num">—</span>
            </div>
            <div class="info-list-row">
              <span class="text-muted">Портфелей</span>
              <span class="num">—</span>
            </div>
          </div>
        </section>

        <TwoFactorCard />
      </div>

      <div class="stack">
        <section class="stats-grid" aria-label="Статистика сделок">
          <StatCard label="Всего сделок" value="57" hint="за всё время" />
          <StatCard label="Исполнено" value="49" hint="86%" tone="up" />
          <StatCard label="Ожидают" value="3" hint="лимитные заявки" tone="warn" />
          <StatCard label="Отменено" value="5" hint="9%" tone="muted" />
          <StatCard label="Оборот" value="2,84 млн ₽" hint="покупки 1,62 · продажи 1,22" />
        </section>

        <section class="card">
          <div class="table-toolbar">
            <h2 class="table-toolbar-title">История сделок <span class="table-count">57</span></h2>
            <div class="export-actions">
              <button class="btn btn-ghost btn-sm" type="button">Сбросить фильтры</button>
              <ExportButtons />
            </div>
          </div>
          <div class="table-wrap">
            <table class="data-table data-table-compact">
              <thead>
                <tr>
                  <th>Создана</th>
                  <th>Исполнена</th>
                  <th v-if="profileStore.isSuperuser">
                    Пользователь <span class="admin-only-tag">админ</span>
                  </th>
                  <th>Портфель</th>
                  <th>Инструмент</th>
                  <th>Операция</th>
                  <th>Исполнение</th>
                  <th class="col-num">Кол-во</th>
                  <th class="col-num">Цена</th>
                  <th class="col-num">Сумма</th>
                  <th>Статус</th>
                </tr>
                <tr class="filter-row">
                  <th><input class="filter-input" type="date" aria-label="Создана" /></th>
                  <th><input class="filter-input" type="date" aria-label="Исполнена" /></th>
                  <th v-if="profileStore.isSuperuser">
                    <select class="filter-select" aria-label="Пользователь">
                      <option value="">Все</option>
                    </select>
                  </th>
                  <th>
                    <select class="filter-select" aria-label="Портфель">
                      <option value="">Все</option>
                    </select>
                  </th>
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
                  <th>
                    <div class="filter-range">
                      <input class="filter-input" type="number" placeholder="от" aria-label="Сумма от" />
                      <input class="filter-input" type="number" placeholder="до" aria-label="Сумма до" />
                    </div>
                  </th>
                  <th>
                    <select class="filter-select" aria-label="Статус">
                      <option value="">Все</option>
                      <option value="pending">Ожидает</option>
                      <option value="executed">Исполнена</option>
                      <option value="cancelled">Отменена</option>
                    </select>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="trade in trades" :key="trade.id">
                  <td class="num">{{ trade.created }}</td>
                  <td class="num" :class="{ 'text-muted': !trade.executed }">
                    {{ trade.executed ?? '—' }}
                  </td>
                  <td v-if="profileStore.isSuperuser">{{ trade.user }}</td>
                  <td>
                    <router-link :to="{ name: 'portfolio', params: { id: trade.portfolio } }">
                      {{ trade.portfolioName }}
                    </router-link>
                  </td>
                  <td><strong>{{ trade.ticker }}</strong></td>
                  <td>
                    <span class="badge" :class="`badge-${trade.order_type}`">
                      {{ orderTypeLabels[trade.order_type] }}
                    </span>
                  </td>
                  <td>
                    <span class="badge badge-exec">
                      {{ executionTypeLabels[trade.execution_type] }}
                    </span>
                  </td>
                  <td class="col-num num">{{ trade.quantity }}</td>
                  <td class="col-num num">{{ trade.price }}</td>
                  <td class="col-num num">{{ trade.total }}</td>
                  <td>
                    <span class="badge" :class="`badge-${trade.status}`">
                      {{ statusLabels[trade.status] }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="table-footer">
            <span>Показано 1–6 из 57</span>
            <nav class="pagination" aria-label="Страницы">
              <button class="pagination-btn" type="button" aria-label="Предыдущая">‹</button>
              <button class="pagination-btn is-active" type="button">1</button>
              <button class="pagination-btn" type="button">2</button>
              <button class="pagination-btn" type="button">3</button>
              <button class="pagination-btn" type="button" aria-label="Следующая">›</button>
            </nav>
          </div>
        </section>
      </div>
    </div>
  </main>
</template>

<style scoped>
.profile-card {
  align-items: center;
  text-align: center;
  gap: var(--space-2);
  padding: var(--space-6);
}

.profile-name {
  font-size: var(--font-size-xl);
  font-weight: 600;
}

.info-list {
  display: flex;
  flex-direction: column;
  width: 100%;
  margin-top: var(--space-3);
  text-align: left;
}

.info-list-row {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  border-top: 1px solid var(--color-border);
  font-size: var(--font-size-sm);
}
</style>
