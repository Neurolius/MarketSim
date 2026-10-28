<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  large: {
    type: Boolean,
    default: false,
  },
})

const icons = {
  plus: '<path d="M12 5v14M5 12h14"/>',
  download: '<path d="M12 3v12m0 0l-4-4m4 4l4-4M5 21h14"/>',
  upload: '<path d="M12 16V4m0 0l-4 4m4-4l4 4M5 20h14"/>',
  edit: '<path d="M4 20h4L19 9l-4-4L4 16v4z"/>',
  trash: '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>',
  close: '<path d="M6 6l12 12M18 6L6 18"/>',
  shield: '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/>',
  'shield-alert': '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M12 9v4M12 16v.5"/>',
  'shield-check': '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M9 12l2 2 4-4"/>',
  logout: '<path d="M15 4h4v16h-4M10 8l-4 4 4 4M6 12h10"/>',
  alert: '<circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16v.5"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8v.5"/>',
  check: '<path d="M5 12l5 5 9-10"/>',
  image: '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="M21 17l-5-5-9 8"/>',
  briefcase: '<rect x="3" y="6" width="18" height="14" rx="2"/><path d="M8 6V4h8v2"/>',
  chart: '<path d="M4 17l5-5 4 4 7-8"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
  lock: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/>',
}

const content = computed(() => icons[props.name] ?? '')
</script>

<template>
  <svg
    class="icon"
    :class="{ 'icon-lg': large }"
    viewBox="0 0 24 24"
    aria-hidden="true"
    v-html="content"
  ></svg>
</template>

<style scoped>
.icon {
  width: 16px;
  height: 16px;
  flex: none;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.icon-lg {
  width: 22px;
  height: 22px;
}
</style>
