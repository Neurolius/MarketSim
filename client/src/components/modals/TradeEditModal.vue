<script setup>
import BaseModal from '@/components/BaseModal.vue'
import ImageUpload from '@/components/ImageUpload.vue'

// trade — заявка из API в статусе «pending»
defineProps({
  trade: {
    type: Object,
    required: true,
  },
})

defineEmits(['close', 'submit', 'cancel-trade'])

const orderTypeLabels = { buy: 'Покупка', sell: 'Продажа' }
const executionTypeLabels = { market: 'Рыночная', limit: 'Лимитная' }
</script>

<template>
  <BaseModal title="Изменить заявку" form @close="$emit('close')" @submit="$emit('submit')">
    <div class="inline-row trade-badges">
      <span class="badge" :class="`badge-${trade.order_type}`">
        {{ orderTypeLabels[trade.order_type] }}
      </span>
      <span class="badge badge-exec">{{ executionTypeLabels[trade.execution_type] }}</span>
      <span class="badge badge-pending">Ожидает</span>
      <span class="text-muted text-sm">
        {{ trade.instrument_info?.ticker }} · создана
        {{ new Date(trade.created_at).toLocaleString() }}
      </span>
    </div>

    <div class="form-row">
      <div class="form-field">
        <label class="form-label" for="trade-qty">Количество</label>
        <input id="trade-qty" class="form-input" type="number" min="0" :value="trade.quantity" />
      </div>
      <div class="form-field">
        <label class="form-label" for="trade-limit">Лимитная цена, ₽</label>
        <input id="trade-limit" class="form-input" type="number" min="0" :value="trade.price" />
      </div>
    </div>

    <div class="form-field">
      <span class="form-label">
        Изображение <span class="form-label-hint">(необязательно)</span>
      </span>
      <ImageUpload
        id="trade-image"
        :preview-url="trade.image ?? null"
        icon="image"
        action-text="Прикрепить скриншот"
        text="графика"
        hint=""
      />
    </div>

    <template #footer>
      <button class="btn btn-danger push-left" type="button" @click="$emit('cancel-trade')">
        Отменить заявку
      </button>
      <button class="btn btn-secondary" type="button" @click="$emit('close')">Закрыть</button>
      <button class="btn btn-primary" type="submit">Сохранить</button>
    </template>
  </BaseModal>
</template>

<style scoped>
.trade-badges {
  gap: var(--space-2);
}

.push-left {
  margin-right: auto;
}
</style>
