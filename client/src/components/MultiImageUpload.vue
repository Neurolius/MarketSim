<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
  modelValue: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["update:modelValue"]);
const input = ref(null);

watch(
  () => props.modelValue,
  (files) => {
    if (!files.length && input.value) input.value.value = "";
  },
);

function onChange(event) {
  emit("update:modelValue", Array.from(event.target.files || []));
}
</script>

<template>
  <div class="multi-image-upload">
    <input
      ref="input"
      :id="id"
      class="form-input"
      type="file"
      accept="image/*"
      multiple
      @change="onChange"
    />
    <span v-if="modelValue.length" class="form-hint">
      Выбрано изображений: {{ modelValue.length }}
    </span>
  </div>
</template>
