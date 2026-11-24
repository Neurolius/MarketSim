<script setup>
import { computed, ref } from "vue";
import AppIcon from "@/components/AppIcon.vue";
import BaseModal from "@/components/BaseModal.vue";
import ImageUpload from "@/components/ImageUpload.vue";
import { useImagePreview } from "@/composables/useImagePreview";

const props = defineProps({
  portfolio: { type: Object, default: null },
  error: { type: String, default: "" },
  loading: { type: Boolean, default: false },
});
const emit = defineEmits(["close", "submit"]);

const name = ref(props.portfolio?.name ?? "");
const balance = ref(100000);

const {
  file: coverFile,
  preview: coverPreview,
  onFileChange: onCoverChange,
} = useImagePreview(props.portfolio?.cover_image);

const canSubmit = computed(
  () =>
    name.value.trim() &&
    (props.portfolio || (balance.value != "" && balance.value >= 0)) &&
    !props.loading,
);

function submit() {
  if (!canSubmit.value) return;
  emit("submit", {
    name: name.value.trim(),
    balance: props.portfolio ? null : balance.value,
    cover_image: coverFile.value,
  });
}
</script>

<template>
  <BaseModal
    :title="portfolio ? 'Изменить портфель' : 'Новый портфель'"
    form
    @close="$emit('close')"
    @submit="submit"
  >
    <div class="form-field">
      <label class="form-label" for="portfolio-name">Название</label>
      <input
        id="portfolio-name"
        class="form-input"
        type="text"
        placeholder="Например, «Основной»"
        v-model="name"
      />
    </div>
    <div v-if="!portfolio" class="form-field">
      <label class="form-label" for="portfolio-balance">Стартовый баланс</label>
      <div class="input-group">
        <input
          id="portfolio-balance"
          v-model.number="balance"
          class="form-input"
          type="number"
          min="0"
        />
        <span class="input-addon">₽</span>
      </div>
      <span class="form-hint">Дальше баланс меняется только сделками</span>
    </div>
    <div class="form-field">
      <span class="form-label">Обложка</span>
      <ImageUpload
        id="portfolio-cover"
        :preview-url="coverPreview"
        :action-text="coverPreview ? 'Заменить файл' : 'Выберите файл'"
        text="или перетащите"
        @change="onCoverChange"
      />
    </div>

    <div v-if="error" class="alert alert-error">
      <AppIcon name="alert" />
      <span>{{ error }}</span>
    </div>

    <template #footer>
      <button class="btn btn-primary" type="submit" :disabled="!canSubmit">
        Отмена
      </button>
      <button class="btn btn-primary" type="submit">
        {{ portfolio ? "Сохранить" : "Создать" }}
      </button>
    </template>
  </BaseModal>
</template>
