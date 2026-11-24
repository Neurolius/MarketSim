export function toFormData(data) {
  const formData = new FormData();
  for (const [key, value] of Object.entries(data)) {
    if (Array.isArray(value)) {
      value.forEach((item) => formData.append(key, item));
    } else if (value !== null && value !== undefined && value !== "") {
      formData.append(key, value);
    }
  }
  return formData;
}

export function errorText(e, fallback = "Не удалось выполнить запрос") {
  const data = e.response?.data;
  if (!data || typeof data !== "object") return fallback;
  if (data.detail) return data.detail;
  return Object.values(data).flat().join(" ");
}
