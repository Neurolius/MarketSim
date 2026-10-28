<script setup>
import BaseModal from '@/components/BaseModal.vue'
import ImageUpload from '@/components/ImageUpload.vue'

// instrument — редактируемый инструмент; без него модалка работает как «Новый инструмент»
defineProps({
  instrument: {
    type: Object,
    default: null,
  },
  instrumentTypes: {
    type: Array,
    default: () => [],
  },
})

defineEmits(['close', 'submit', 'open-logo'])
</script>

<template>
  <BaseModal
    :title="instrument ? 'Изменить инструмент' : 'Новый инструмент'"
    form
    @close="$emit('close')"
    @submit="$emit('submit')"
  >
    <div class="form-row">
      <div class="form-field">
        <label class="form-label" for="instrument-ticker">Тикер</label>
        <input
          id="instrument-ticker"
          class="form-input"
          type="text"
          placeholder="SBER"
          :value="instrument?.ticker"
        />
      </div>
      <div class="form-field">
        <label class="form-label" for="instrument-type">Тип</label>
        <select id="instrument-type" class="form-select">
          <option
            v-for="type in instrumentTypes"
            :key="type.id"
            :value="type.id"
            :selected="type.id === instrument?.instrument_type"
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
        class="form-input"
        type="text"
        placeholder="Сбербанк"
        :value="instrument?.name"
      />
    </div>
    <div class="form-field">
      <label class="form-label" for="instrument-price">Текущая цена, ₽</label>
      <input
        id="instrument-price"
        class="form-input"
        type="number"
        min="0"
        step="any"
        :value="instrument?.current_price"
      />
      <!-- при ошибке: class="form-input is-invalid" + <span class="form-error-text">…</span> -->
    </div>
    <div class="form-field">
      <span class="form-label">Логотип</span>
      <ImageUpload
        id="instrument-logo"
        :preview-url="instrument?.logo ?? ''"
        round
        :icon="''"
        text=""
        hint="Квадратное изображение"
        @open-preview="$emit('open-logo')"
      />
    </div>

    <template #footer>
      <button class="btn btn-secondary" type="button" @click="$emit('close')">Отмена</button>
      <button class="btn btn-primary" type="submit">{{ instrument ? 'Сохранить' : 'Создать' }}</button>
    </template>
  </BaseModal>
</template>
