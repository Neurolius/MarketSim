<script setup>
import { computed, ref } from "vue";
import AppIcon from "@/components/AppIcon.vue";
import BaseModal from "@/components/BaseModal.vue";
import ImageUpload from "@/components/ImageUpload.vue";
import { useImagePreview } from "@/composables/useImagePreview";

const props = defineProps({
  instrument: { type: Object, default: null },
  instrumentTypes: { type: Array, default: () => [] },
  error: { type: String, default: "" },
  loading: { type: Boolean, default: false },
});
const emit = defineEmits(["close", "submit"]);

const ticker = ref(props.instrument?.ticker ?? "");
const name = ref(props.instrument?.name ?? "");
const typeId = ref(
  props.instrument?.typeId ?? props.instrumentTypes[0]?.id ?? null,
);
const price = ref(props.instrument?.rawPrice ?? null);

const {
  file: logoFile,
  preview: logoPreview,
  onFileChange: onLogoChange,
} = useImagePreview(props.instrument?.logo);

const canSubmit = computed(
  () =>
    ticker.value.trim() &&
    name.value.trim() &&
    typeId.value &&
    price.value !== null &&
    price.value !== "" &&
    price.value >= 0 &&
    !props.loading,
);

function submit() {
  if (!canSubmit.value) return;
  emit("submit", {
    ticker: ticker.value.trim().toUpperCase(),
    name: name.value.trim(),
    instrument_type: typeId.value,
    current_price: price.value,
    logo: logoFile.value,
  });
}
</script>

<template>
  <BaseModal
    :title="instrument ? 'Изменить инструмент' : 'Новый инструмент'"
    form
    @close="$emit('close')"
    @submit="submit"
  >
    <div class="form-row">
      <div class="form-field">
        <label class="form-label" for="instrument-ticker">Тикер</label>
        <input
          id="instrument-ticker"
          v-model="ticker"
          class="form-input"
          type="text"
          placeholder="SBER"
        />
      </div>
      <div class="form-field">
        <label class="form-label" for="instrument-type">Тип</label>
        <select id="instrument-type" v-model="typeId" class="form-select">
          <option
            v-for="type in instrumentTypes"
            :key="type.id"
            :value="type.id"
          >
            {{ type.name }}
          </option>
        </select>
      </div>
    </div>
    <div class="form-field">
      <label class="form-label" for="instrument-name">Название</label>
      <input
        id="instrument-name"
        v-model="name"
        class="form-input"
        type="text"
        placeholder="Сбербанк"
      />
    </div>
    <div class="form-field">
      <label class="form-label" for="instrument-price">Текущая цена, ₽</label>
      <input
        id="instrument-price"
        v-model.number="price"
        class="form-input"
        type="number"
        min="0"
        step="any"
      />
    </div>
    <div class="form-field">
      <span class="form-label">Логотип</span>
      <ImageUpload
        id="instrument-logo"
        :preview-url="logoPreview"
        round
        :icon="''"
        text=""
        hint="Квадратное изображение"
        @change="onLogoChange"
      />
    </div>

    <div v-if="error" class="alert alert-error">
      <AppIcon name="alert" />
      <span>{{ error }}</span>
    </div>

    <template #footer>
      <button class="btn btn-secondary" type="button" @click="$emit('close')">
        Отмена
      </button>
      <button class="btn btn-primary" type="submit" :disabled="!canSubmit">
        {{ instrument ? "Сохранить" : "Создать" }}
      </button>
    </template>
  </BaseModal>
</template>
