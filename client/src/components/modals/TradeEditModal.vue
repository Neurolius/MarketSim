<script setup>
import { computed, ref } from "vue";
import AppIcon from "@/components/AppIcon.vue";
import BaseModal from "@/components/BaseModal.vue";
import MultiImageUpload from "@/components/MultiImageUpload.vue";
import { formatPrice } from "@/utils/format";
import { orderTypeLabels, executionTypeLabels } from "@/utils/labels";

const props = defineProps({
  trade: { type: Object, required: true },
  error: { type: String, default: "" },
  loading: { type: Boolean, default: false },
});
const emit = defineEmits(["close", "submit", "cancel-trade"]);

const quantity = ref(Number(props.trade.quantity));
const limitPrice = ref(props.trade.price ? Number(props.trade.price) : null);
const imageFiles = ref([]);

const total = computed(
  () => (Number(quantity.value) || 0) * (Number(limitPrice.value) || 0),
);
const canSubmit = computed(
  () => quantity.value > 0 && limitPrice.value > 0 && !props.loading,
);

function submit() {
  if (!canSubmit.value) return;
  emit("submit", {
    quantity: quantity.value,
    price: limitPrice.value,
    new_images: imageFiles.value,
  });
}
</script>

<template>
  <BaseModal
    title="Изменить заявку"
    form
    @close="$emit('close')"
    @submit="submit"
  >
    <div class="inline-row trade-badges">
      <span class="badge" :class="`badge-${trade.order_type}`">
        {{ orderTypeLabels[trade.order_type] }}
      </span>
      <span class="badge badge-exec">{{
        executionTypeLabels[trade.execution_type]
      }}</span>
      <span class="badge badge-pending">Ожидает</span>
      <span class="text-muted text-sm">
        {{ trade.instrument_info?.ticker }} · создана
        {{ new Date(trade.created_at).toLocaleString() }}
      </span>
    </div>

    <div class="form-row">
      <div class="form-field">
        <label class="form-label" for="trade-qty">Количество</label>
        <input
          id="trade-qty"
          v-model.number="quantity"
          class="form-input"
          type="number"
          min="0"
          step="any"
        />
      </div>
      <div class="form-field">
        <label class="form-label" for="trade-limit">Лимитная цена, ₽</label>
        <input
          id="trade-limit"
          v-model.number="limitPrice"
          class="form-input"
          type="number"
          min="0"
          step="any"
        />
      </div>
    </div>

    <div class="form-field">
      <span class="form-label">
        Изображения сделки
        <span class="form-label-hint">(необязательно)</span>
      </span>
      <MultiImageUpload id="trade-images" v-model="imageFiles" />
      <span v-if="trade.images?.length" class="form-hint">
        Уже прикреплено: {{ trade.images.length }}
      </span>
    </div>

    <div class="order-summary">
      <div class="order-summary-row order-summary-total">
        <span>Сумма заявки</span>
        <span class="num">{{ formatPrice(total) }} ₽</span>
      </div>
    </div>

    <div v-if="error" class="alert alert-error" role="alert">
      <AppIcon name="alert" />
      <span>{{ error }}</span>
    </div>

    <template #footer>
      <button
        class="btn btn-danger push-left"
        type="button"
        @click="$emit('cancel-trade')"
        :disabled="loading"
      >
        Отменить заявку
      </button>
      <button class="btn btn-secondary" type="button" @click="$emit('close')">
        Закрыть
      </button>
      <button class="btn btn-primary" type="submit" :disabled="!canSubmit">
        Сохранить
      </button>
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
