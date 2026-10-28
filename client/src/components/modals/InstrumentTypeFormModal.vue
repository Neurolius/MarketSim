<script setup>
import BaseModal from '@/components/BaseModal.vue'

// instrumentType — редактируемый тип; без него модалка работает как «Новый тип»
defineProps({
  instrumentType: {
    type: Object,
    default: null,
  },
})

defineEmits(['close', 'submit'])
</script>

<template>
  <BaseModal
    :title="instrumentType ? 'Тип инструмента' : 'Новый тип инструмента'"
    size="sm"
    form
    @close="$emit('close')"
    @submit="$emit('submit')"
  >
    <div class="form-field">
      <label class="form-label" for="instrument-type-name">Название</label>
      <input
        id="instrument-type-name"
        class="form-input"
        type="text"
        placeholder="Например, «Облигация»"
        :value="instrumentType?.name"
      />
    </div>

    <template #footer>
      <button class="btn btn-secondary" type="button" @click="$emit('close')">Отмена</button>
      <button class="btn btn-primary" type="submit">Сохранить</button>
    </template>
  </BaseModal>
</template>
