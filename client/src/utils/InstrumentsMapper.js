const nf = new Intl.NumberFormat("ru-RU", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const formatPrice = (v) => nf.format(Number(v));

const formatSigned = (v) => {
  const n = Number(v);
  return (n > 0 ? "+" : n < 0 ? "−" : "") + nf.format(Math.abs(n));
};

const formatDate = (iso) =>
  iso
    ? new Date(iso).toLocaleString("ru-RU", {
        day: "2-digit",
        month: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "—";

export function mapInstrument(raw, typesById) {
  const price = Number(raw.current_price);
  const prev = raw.prev_price != null ? Number(raw.prev_price) : null;
  const diff = prev != null ? price - prev : 0;
  const percent = prev ? (diff / prev) * 100 : 0;

  return {
    id: raw.id,
    ticker: raw.ticker,
    name: raw.name,
    typeName: typesById[raw.instrument_type]?.name ?? "—",
    typeId: raw.instrument_type,
    logo: raw.logo,
    price: formatPrice(price),
    diff: formatSigned(diff),
    change: formatSigned(percent) + "%",
    isUp: diff >= 0,
    updated: formatDate(raw.price_updated_at),
  };
}
