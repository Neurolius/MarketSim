<script setup>
// type: 'stock' | 'crypto' | 'currency' — задаёт цвет заглушки, когда нет логотипа
defineProps({
  ticker: {
    type: String,
    default: '',
  },
  logo: {
    type: String,
    default: null,
  },
  type: {
    type: String,
    default: 'stock',
  },
  large: {
    type: Boolean,
    default: false,
  },
  // false — логотип внутри ссылки, без открытия в полном размере
  zoomable: {
    type: Boolean,
    default: true,
  },
})

defineEmits(['open'])
</script>

<template>
  <component
    :is="zoomable ? 'button' : 'span'"
    class="instrument-logo"
    :class="[`is-${type}`, { 'instrument-logo-lg': large, 'is-zoomable': zoomable }]"
    :type="zoomable ? 'button' : undefined"
    :aria-label="zoomable ? `Открыть логотип ${ticker}` : undefined"
    @click="zoomable && $emit('open')"
  >
    <img v-if="logo" :src="logo" :alt="ticker" />
    <template v-else>{{ ticker.length > 3 ? ticker.slice(0, 2) : ticker }}</template>
  </component>
</template>

<style scoped>
.instrument-logo {
  width: 32px;
  height: 32px;
  flex: none;
  padding: 0;
  overflow: hidden;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background: var(--color-neutral-soft);
  color: var(--color-text);
  display: inline-grid;
  place-items: center;
  font-size: 11px;
  font-weight: 700;
}

.instrument-logo.is-zoomable {
  cursor: zoom-in;
}

.instrument-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.instrument-logo-lg {
  width: 56px;
  height: 56px;
  font-size: 16px;
}

.instrument-logo.is-stock {
  background: #e6f0e9;
  color: #1f5d34;
}

.instrument-logo.is-crypto {
  background: #fff1d9;
  color: #7a4a00;
}

.instrument-logo.is-currency {
  background: #e7eefb;
  color: #1e3f8f;
}
</style>
