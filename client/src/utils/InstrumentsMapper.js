import { formatPrice, formatSigned, formatDate } from "./format";

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
    rawPrice: price,
    price: formatPrice(price),
    diff: formatSigned(diff),
    change: formatSigned(percent) + "%",
    rawChange: percent,
    isUp: diff >= 0,
    updated: formatDate(raw.price_updated_at),
  };
}
