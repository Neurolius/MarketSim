<script setup>
import { ref } from "vue";
import axios from "axios";
import AppIcon from "@/components/AppIcon.vue";
import { errorText } from "@/utils/requestFormatter";

const props = defineProps({
  small: {
    type: Boolean,
    default: true,
  },
  url: {
    type: String,
    required: true,
  },
  params: {
    type: Object,
    default: () => ({}),
  },
});

const isExporting = ref(false);
const exportError = ref("");

async function download(format) {
  isExporting.value = true;
  exportError.value = "";
  try {
    const { data, headers } = await axios.get(props.url, {
      params: { ...props.params, export_format: format },
      responseType: "blob",
    });
    const downloadUrl = URL.createObjectURL(data);
    const link = document.createElement("a");
    const filename = headers["content-disposition"]?.match(
      /filename="?([^";]+)"?/i,
    )?.[1];
    link.href = downloadUrl;
    link.download =
      filename ?? `export.${format === "excel" ? "xlsx" : "docx"}`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000);
  } catch (error) {
    exportError.value =
      error.response?.data instanceof Blob
        ? "Не удалось экспортировать файл"
        : errorText(error);
  } finally {
    isExporting.value = false;
  }
}
</script>

<template>
  <div class="export-buttons">
    <button
      class="btn btn-secondary"
      :class="{ 'btn-sm': small }"
      type="button"
      :disabled="isExporting"
      @click="download('excel')"
    >
      <AppIcon name="download" />
      Excel
    </button>
    <button
      class="btn btn-secondary"
      :class="{ 'btn-sm': small }"
      type="button"
      :disabled="isExporting"
      @click="download('word')"
    >
      <AppIcon name="download" />
      Word
    </button>
    <span v-if="exportError" class="form-error-text">
      {{ exportError }}
    </span>
  </div>
</template>

<style scoped>
.export-buttons {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
}
</style>
