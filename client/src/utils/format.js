const priceFormat = new Intl.NumberFormat("ru-RU", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const quantityFormat = new Intl.NumberFormat("ru-RU", {
  maximumFractionDigits: 4,
});

export const formatPrice = (v) => priceFormat.format(Number(v));

export const formatQuantity = (v) => quantityFormat.format(Number(v));

export const formatSigned = (v) => {
  const n = Number(v);
  return (n > 0 ? "+" : n < 0 ? "−" : "") + priceFormat.format(Math.abs(n));
};

export const formatDate = (iso) =>
  iso
    ? new Date(iso).toLocaleString("ru-RU", {
        day: "2-digit",
        month: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "—";

export const toDateInputValue = (iso) => {
  if (!iso) return "";
  const d = new Date(iso);
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${month}-${day}`;
};
