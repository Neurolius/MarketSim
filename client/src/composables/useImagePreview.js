import { onBeforeUnmount, ref } from "vue";

export function useImagePreview(initialUrl) {
  const file = ref(null);
  const preview = ref(initialUrl ?? "");

  function revoke() {
    if (preview.value.startsWith("blob:")) URL.revokeObjectURL(preview.value);
  }

  function onFileChange(event) {
    const selected = event.target.files[0];
    if (!selected) return;
    revoke();
    file.value = selected;
    preview.value = URL.createObjectURL(selected);
  }

  onBeforeUnmount(revoke);

  return { file, preview, onFileChange };
}
