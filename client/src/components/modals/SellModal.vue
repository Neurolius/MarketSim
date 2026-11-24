<script setup>
import { computed, ref } from "vue";
import BaseModal from "@/components/BaseModal.vue";
import InstrumentLogo from "@/components/InstrumentLogo.vue";
import AppIcon from "@/components/AppIcon.vue";
import MultiImageUpload from "@/components/MultiImageUpload.vue";
import { formatPrice, formatQuantity, formatSigned } from "@/utils/format";

const props = defineProps({
  position: {
    type: Object,
    required: true,
  },
  portfolioName: {
    type: String,
    default: "",
  },
  error: {
    type: String,
    default: "",
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close", "submit"]);

const executionType = ref("market");
const quantity = ref(null);
const limitPrice = ref(null);
const imageFiles = ref([]);

const isLimit = computed(() => executionType.value === "limit");
const maxQuantity = computed(() => Number(props.position.quantity));
const avarage = computed(() => Number(props.position.average_price));
const unitPrice = computed(() =>
  isLimit.value
    ? Number(limitPrice.value) || 0
    : Number(props.position.instrument_info.current_price),
);
const qty = computed(() => Number(quantity.value) || 0);
const revenue = computed(() => qty.value * unitPrice.value);
const result = computed(() => (unitPrice.value - avarage.value) * qty.value);

const canSubmit = computed(
  () =>
    qty.value > 0 &&
    qty.value <= maxQuantity.value &&
    (!isLimit.value || limitPrice.value > 0) &&
    !props.loading,
);

function submit() {
  if (!canSubmit.value) return;
  emit("submit", {
    execution_type: executionType.value,
    quantity: quantity.value,
    price: isLimit.value ? limitPrice.value : null,
    new_images: imageFiles.value,
  });
}
</script>

<template>
  <BaseModal
    :title="`Продать ${position.instrument_info.ticker}`"
    form
    @close="$emit('close')"
    @submit="submit"
  >
    <div class="cell-instrument">
      <InstrumentLogo
        :ticker="position.instrument_info.ticker"
        :logo="position.instrument_info.logo"
        :zoomable="false"
      />
      <span class="cell-instrument-text">
        <span class="cell-instrument-ticker">
          {{ position.instrument_info.ticker }} ·
          {{ formatPrice(position.instrument_info.current_price) }} ₽
        </span>
        <span class="cell-instrument-name">
          В портфеле «{{ portfolioName }}»: {{ formatQuantity(maxQuantity) }} шт,
          ср. цена {{ formatPrice(avarage) }} ₽
        </span>
      </span>
    </div>

    <div
      class="segmented segmented-block"
      role="group"
      aria-label="Тип исполнения"
    >
      <button
        class="segmented-btn"
        :class="{ 'is-active': !isLimit }"
        type="button"
        @click="executionType = 'market'"
      >
        Рыночная
      </button>
      <button
        class="segmented-btn"
        :class="{ 'is-active': isLimit }"
        type="button"
        @click="executionType = 'limit'"
      >
        Лимитная
      </button>
    </div>

    <div class="form-row">
      <div class="form-field">
        <label class="form-label" for="sell-qty">Количество</label>
        <input
          id="sell-qty"
          v-model.number="quantity"
          class="form-input"
          type="number"
          min="0"
          step="any"
          :max="maxQuantity"
        />
        <span class="form-hint"
          >Максимум {{ formatQuantity(maxQuantity) }}</span
        >
      </div>
      <div class="form-field">
        <label class="form-label" for="sell-limit">Лимитная цена, ₽</label>
        <input
          id="sell-limit"
          class="form-input"
          v-model.number="limitPrice"
          type="number"
          min="0"
          step="any"
          :disabled="!isLimit"
          :placeholder="isLimit ? '' : '—'"
        />
      </div>
    </div>

    <div class="form-field">
      <label class="form-label" for="sell-images">
        Изображения сделки
        <span class="form-label-hint">(необязательно)</span>
      </label>
      <MultiImageUpload id="sell-images" v-model="imageFiles" />
    </div>

    <div class="order-summary">
      <div class="order-summary-row">
        <span class="text-muted">Выручка</span>
        <span class="num">{{ formatPrice(revenue) }} ₽</span>
      </div>
      <div class="order-summary-row">
        <span class="text-muted">Ожидаемый результат</span>
        <span class="price-change" :class="result >= 0 ? 'is-up' : 'is-down'"
          >{{ formatSigned(result) }} ₽</span
        >
      </div>
    </div>

    <div v-if="error" class="alert alert-error" role="alert">
      <AppIcon name="alert" />
      <span>{{ error }}</span>
    </div>

    <template #footer>
      <button class="btn btn-secondary" type="button" @click="$emit('close')">
        Отмена
      </button>
      <button class="btn btn-sell" type="submit" :disabled="!canSubmit">
        {{ isLimit ? "Выставить заявку" : "Продать" }}
      </button>
    </template>
  </BaseModal>
</template>
