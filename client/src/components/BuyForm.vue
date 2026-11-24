<script setup>
import AppIcon from "@/components/AppIcon.vue";
import MultiImageUpload from "@/components/MultiImageUpload.vue";
import { formatPrice, formatQuantity } from "@/utils/format.js";
import { computed, ref, watch } from "vue";

const props = defineProps({
  instrument: {
    type: Object,
    required: true,
  },
  portfolios: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["submit"]);

const portfolioId = ref(null);
const executionType = ref("market");
const quantity = ref(null);
const limitPrice = ref(null);
const imageFiles = ref([]);

watch(
  () => props.portfolios,
  (list) => {
    if (!portfolioId.value && list.length) portfolioId.value = list[0].id;
  },
  { immediate: true },
);

const isLimit = computed(() => executionType.value === "limit");
const portfolio = computed(() =>
  props.portfolios.find((p) => p.id === portfolioId.value),
);
const available = computed(() => Number(portfolio.value?.balance ?? 0));
const unitPrice = computed(() =>
  isLimit.value ? Number(limitPrice.value) || 0 : props.instrument.rawPrice,
);
const total = computed(() => Number(quantity.value) * unitPrice.value);
const notEnough = computed(() => total.value > available.value);
const canSubmit = computed(
  () =>
    portfolioId.value &&
    quantity.value > 0 &&
    (!isLimit.value || limitPrice.value > 0) &&
    !notEnough.value &&
    !props.loading,
);

function submit() {
  emit("submit", {
    portfolio: portfolioId.value,
    execution_type: executionType.value,
    quantity: quantity.value,
    price: isLimit.value ? limitPrice.value : null,
    new_images: imageFiles.value,
  });
}

function reset() {
  quantity.value = null;
  limitPrice.value = null;
  imageFiles.value = [];
}
defineExpose({
  reset,
});
</script>

<template>
  <section class="card">
    <div class="card-header">
      <h2 class="card-title">Купить {{ instrument.ticker }}</h2>
    </div>
    <form class="card-body form" @submit.prevent="submit">
      <div class="form-field">
        <label class="form-label" for="buy-portfolio">Портфель</label>
        <select id="buy-portfolio" v-model="portfolioId" class="form-select">
          <option
            v-for="portfolio in portfolios"
            :key="portfolio.id"
            :value="portfolio.id"
          >
            {{ portfolio.name }} — баланс {{ formatPrice(portfolio.balance) }} ₽
          </option>
        </select>
      </div>

      <div class="form-field">
        <span class="form-label">Тип исполнения</span>
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
      </div>

      <div class="form-row">
        <div class="form-field">
          <label class="form-label" for="buy-qty">Количество</label>
          <div class="input-group">
            <input
              id="buy-qty"
              v-model.number="quantity"
              class="form-input"
              type="number"
              min="0"
              step="any"
            />
            <span class="input-addon">шт</span>
          </div>
        </div>
        <div class="form-field">
          <label class="form-label" for="buy-limit">Лимитная цена</label>
          <div class="input-group">
            <input
              id="buy-limit"
              v-model.number="limitPrice"
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
        <label class="form-label" for="buy-images">
          Изображения сделки
          <span class="form-label-hint">(необязательно)</span>
        </label>
        <MultiImageUpload id="buy-images" v-model="imageFiles" />
      </div>

      <div class="order-summary">
        <div class="order-summary-row">
          <span class="text-muted">Цена</span>
          <span class="num"
            >{{
              isLimit
                ? limitPrice
                  ? formatPrice(limitPrice)
                  : "-"
                : instrument.price
            }}
            ₽</span
          >
        </div>
        <div class="order-summary-row">
          <span class="text-muted">Количество</span>
          <span class="num">{{ formatQuantity(quantity || 0) }} шт</span>
        </div>
        <div class="order-summary-row">
          <span class="text-muted">Доступно</span>
          <span class="num">{{ formatPrice(available) }} ₽</span>
        </div>
        <div class="order-summary-row order-summary-total">
          <span>Итого</span>
          <span class="num">{{ formatPrice(total) }} ₽</span>
        </div>
      </div>

      <div v-if="error || notEnough" class="alert alert-error" role="alert">
        <AppIcon name="alert" />
        <span>{{ error || "Недостаточно средств в портфеле" }}</span>
      </div>

      <button
        class="btn btn-buy btn-lg btn-block"
        type="submit"
        :disabled="!canSubmit"
      >
        {{ loading ? "Отправка..." : isLimit ? "Выставить заявку" : "Купить" }}
      </button>
    </form>
  </section>
</template>
