<script setup>
import BaseModal from '@/components/BaseModal.vue'
import InstrumentLogo from '@/components/InstrumentLogo.vue'

// position — позиция из API (instrument_info, quantity, average_price)
defineProps({
  position: {
    type: Object,
    required: true,
  },
  portfolioName: {
    type: String,
    default: '',
  },
  isLimit: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['close', 'submit', 'change-execution'])
</script>

<template>
  <BaseModal
    :title="`Продать ${position.instrument_info.ticker}`"
    form
    @close="$emit('close')"
    @submit="$emit('submit')"
  >
    <div class="cell-instrument">
      <InstrumentLogo
        :ticker="position.instrument_info.ticker"
        :logo="position.instrument_info.logo"
        :zoomable="false"
      />
      <span class="cell-instrument-text">
        <span class="cell-instrument-ticker">
          {{ position.instrument_info.ticker }} · {{ position.instrument_info.current_price }} ₽
        </span>
        <span class="cell-instrument-name">
          В портфеле «{{ portfolioName }}»: {{ position.quantity }} шт, ср. цена
          {{ position.average_price }} ₽
        </span>
      </span>
    </div>

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

    <div class="form-row">
      <div class="form-field">
        <label class="form-label" for="sell-qty">Количество</label>
        <input
          id="sell-qty"
          class="form-input"
          type="number"
          min="0"
          :max="position.quantity"
        />
        <span class="form-hint">Максимум {{ position.quantity }}</span>
      </div>
      <div class="form-field">
        <label class="form-label" for="sell-limit">Лимитная цена, ₽</label>
        <input
          id="sell-limit"
          class="form-input"
          type="number"
          min="0"
          :disabled="!isLimit"
          :placeholder="isLimit ? '' : '—'"
        />
      </div>
    </div>

    <div class="order-summary">
      <div class="order-summary-row">
        <span class="text-muted">Выручка</span>
        <span class="num">—</span>
      </div>
      <div class="order-summary-row">
        <span class="text-muted">Ожидаемый результат</span>
        <span class="price-change is-up">—</span>
      </div>
    </div>

    <template #footer>
      <button class="btn btn-secondary" type="button" @click="$emit('close')">Отмена</button>
      <button class="btn btn-sell" type="submit">
        {{ isLimit ? 'Выставить заявку' : 'Продать' }}
      </button>
    </template>
  </BaseModal>
</template>
