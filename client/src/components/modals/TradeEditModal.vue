<script setup>
import { computed, onBeforeUnmount, ref } from "vue";
import AppIcon from "@/components/AppIcon.vue";
import BaseModal from "@/components/BaseModal.vue";
import ImageUpload from "@/components/ImageUpload.vue";
import { formatPrice } from "@/utils/format";

const props = defineProps({
  trade: { type: Object, required: true },
  error: { type: String, default: "" },
  loading: { type: Boolean, default: false },
});
const emit = defineEmits(["close", "submit", "cancel-trade"]);

const orderTypeLabels = { buy: "Покупка", sell: "Продажа" };
const executionTypeLabels = { market: "Рыночная", limit: "Лимитная" };

const quantity = ref(Number(props.trade.quantity));
const limitPrice = ref(props.trade.price ? Number(props.trade.price) : null);
const imageFile = ref(null);
const imagePreview = ref(props.trade.image ?? "");

function onImageChange(event) {
  const file = event.target.files[0];
  if (!file) return;
  imageFile.value = file;
  if (imagePreview.value.startsWith("blob:"))
    URL.revokeObjectURL(imagePreview.value);
  imagePreview.value = URL.createObjectURL(file);
}

onBeforeUnmount(() => {
  if (imagePreview.value.startsWith("blob:"))
    URL.revokeObjectURL(imagePreview.value);
});

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
    image: imageFile.value,
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
        Изображение <span class="form-label-hint">(необязательно)</span>
      </span>
      <ImageUpload
        id="trade-image"
        :preview-url="imagePreview"
        icon="image"
        :action-text="
          imagePreview ? 'Заменить скриншот' : 'Прикрепить скриншот'
        "
        text="графика"
        hint=""
        @change="onImageChange"
      />
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
