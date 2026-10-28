<script setup>
import AppIcon from '@/components/AppIcon.vue'

defineProps({
  small: {
    type: Boolean,
    default: true,
  },
})

defineEmits(['excel', 'word'])
</script>

<template>
  <button class="btn btn-secondary" :class="{ 'btn-sm': small }" type="button" @click="$emit('excel')">
    <AppIcon name="download" />
    Excel
  </button>
  <button class="btn btn-secondary" :class="{ 'btn-sm': small }" type="button" @click="$emit('word')">
    <AppIcon name="download" />
    Word
  </button>
</template>
