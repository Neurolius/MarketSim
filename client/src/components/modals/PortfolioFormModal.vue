<script setup>
import BaseModal from '@/components/BaseModal.vue'
import ImageUpload from '@/components/ImageUpload.vue'

// portfolio — редактируемый портфель; без него модалка работает как «Новый портфель»
defineProps({
  portfolio: {
    type: Object,
    default: null,
  },
})

defineEmits(['close', 'submit', 'open-cover'])
</script>

<template>
  <BaseModal
    :title="portfolio ? 'Изменить портфель' : 'Новый портфель'"
    form
    @close="$emit('close')"
    @submit="$emit('submit')"
  >
    <div class="form-field">
      <label class="form-label" for="portfolio-name">Название</label>
      <input
        id="portfolio-name"
        class="form-input"
        type="text"
        placeholder="Например, «Основной»"
        :value="portfolio?.name"
      />
    </div>
    <div class="form-field">
      <label class="form-label" for="portfolio-balance">Баланс</label>
      <div class="input-group">
        <input
          id="portfolio-balance"
          class="form-input"
          type="number"
          min="0"
          :value="portfolio?.balance"
        />
        <span class="input-addon">₽</span>
      </div>
      <span class="form-hint">При создании — стартовый виртуальный баланс</span>
    </div>
    <div class="form-field">
      <span class="form-label">Обложка</span>
      <ImageUpload
        id="portfolio-cover"
        :preview-url="portfolio ? (portfolio.cover_image ?? '') : null"
        :action-text="portfolio?.cover_image ? 'Заменить файл' : 'Выберите файл'"
        text="или перетащите"
        @open-preview="$emit('open-cover')"
      />
    </div>

    <template #footer>
      <button class="btn btn-secondary" type="button" @click="$emit('close')">Отмена</button>
      <button class="btn btn-primary" type="submit">{{ portfolio ? 'Сохранить' : 'Создать' }}</button>
    </template>
  </BaseModal>
</template>
