<script setup>
import { ref } from "vue";
import axios from "axios";
import AppIcon from "@/components/AppIcon.vue";
import { errorText } from "@/utils/apiHelper";

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

async function downloadExcel() {
  isExporting.value = true;
  exportError.value = "";
  try {
    const { data, headers } = await axios.get(props.url, {
      params: props.params,
      responseType: "blob",
    });
    const downloadUrl = URL.createObjectURL(data);
    const link = document.createElement("a");
    const filename = headers["content-disposition"]?.match(
      /filename="?([^";]+)"?/i,
    )?.[1];
    link.href = downloadUrl;
    link.download = filename ?? "export.xlsx";
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
      @click="downloadExcel"
    >
      <AppIcon name="download" />
      Excel
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
