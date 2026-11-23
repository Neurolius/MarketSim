<script setup>
import { computed, ref } from "vue";
import AppIcon from "@/components/AppIcon.vue";
import BaseModal from "@/components/BaseModal.vue";

const props = defineProps({
  instrumentType: { type: Object, default: null },
  error: { type: String, default: "" },
  loading: { type: Boolean, default: false },
});
const emit = defineEmits(["close", "submit"]);

const name = ref(props.instrumentType?.name ?? "");
const canSubmit = computed(() => name.value.trim() && !props.loading);

function submit() {
  if (!canSubmit.value) return;
  emit("submit", { name: name.value.trim() });
}
</script>

<template>
  <BaseModal
    :title="instrumentType ? 'Изменить тип' : 'Новый тип инструмента'"
    size="sm"
    form
    @close="$emit('close')"
    @submit="submit"
  >
    <div class="form-field">
      <label class="form-label" for="instrument-type-name">Название</label>
      <input
        id="instrument-type-name"
        class="form-input"
        type="text"
        placeholder="Например, «Облигация»"
        v-model="name"
      />
    </div>

    <div v-if="error" class="alert alert-error" role="alert">
      <AppIcon name="alert" />
      <span>{{ error }}</span>
    </div>

    <template #footer>
      <button class="btn btn-secondary" type="button" @click="$emit('close')">
        Отмена
      </button>
      <button class="btn btn-primary" type="submit" :disabled="!canSubmit">
        Сохранить
      </button>
    </template>
  </BaseModal>
</template>
