<script setup>
import AppIcon from '@/components/AppIcon.vue'

// instrument — инструмент из API, portfolios — портфели пользователя
defineProps({
  instrument: {
    type: Object,
    required: true,
  },
  portfolios: {
    type: Array,
    default: () => [],
  },
  isLimit: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: '',
  },
})

defineEmits(['submit', 'change-execution'])
</script>

<template>
  <section class="card">
    <div class="card-header">
      <h2 class="card-title">Купить {{ instrument.ticker }}</h2>
    </div>
    <form class="card-body form" @submit.prevent="$emit('submit')">
      <div class="form-field">
        <label class="form-label" for="buy-portfolio">Портфель</label>
        <select id="buy-portfolio" class="form-select">
          <option v-for="portfolio in portfolios" :key="portfolio.id" :value="portfolio.id">
            {{ portfolio.name }} — баланс {{ portfolio.balance }} ₽
          </option>
        </select>
      </div>

      <div class="form-field">
        <span class="form-label">Тип исполнения</span>
        <div class="segmented segmented-block" role="group" aria-label="Тип исполнения">
          <button
            class="segmented-btn"
            :class="{ 'is-active': !isLimit }"
            type="button"
            @click="$emit('change-execution', 'market')"
          >
            Рыночная
          </button>
          <button
            class="segmented-btn"
            :class="{ 'is-active': isLimit }"
            type="button"
            @click="$emit('change-execution', 'limit')"
          >
            Лимитная
          </button>
        </div>
      </div>

      <div class="form-row">
        <div class="form-field">
          <label class="form-label" for="buy-qty">Количество</label>
          <div class="input-group">
            <input id="buy-qty" class="form-input" type="number" min="0" step="any" />
            <span class="input-addon">шт</span>
          </div>
        </div>
        <div class="form-field">
          <label class="form-label" for="buy-limit">Лимитная цена</label>
          <div class="input-group">
            <input
              id="buy-limit"
              class="form-input"
              type="number"
              min="0"
              step="any"
              placeholder="—"
              :disabled="!isLimit"
            />
            <span class="input-addon">₽</span>
          </div>
          <span class="form-hint">Только для лимитной заявки</span>
        </div>
      </div>

      <div class="form-field">
        <label class="form-label" for="buy-image">
          Скриншот / заметка к сделке <span class="form-label-hint">(необязательно)</span>
        </label>
        <input id="buy-image" class="form-input" type="file" accept="image/*" />
      </div>

      <div class="order-summary">
        <div class="order-summary-row">
          <span class="text-muted">Цена</span>
          <span class="num">{{ instrument.current_price }} ₽</span>
        </div>
        <div class="order-summary-row">
          <span class="text-muted">Количество</span>
          <span class="num">— шт</span>
        </div>
        <div class="order-summary-row">
          <span class="text-muted">Доступно</span>
          <span class="num">— ₽</span>
        </div>
        <div class="order-summary-row order-summary-total">
          <span>Итого</span>
          <span class="num">— ₽</span>
        </div>
      </div>

      <div v-if="error" class="alert alert-error" role="alert">
        <AppIcon name="alert" />
        <span>{{ error }}</span>
      </div>

      <button class="btn btn-buy btn-lg btn-block" type="submit">Купить</button>
    </form>
  </section>
</template>
