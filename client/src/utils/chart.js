import { formatPrice } from "@/utils/format.js";

export function buildChart(records, width, height) {
  if (records.length < 2) return null;

  const top = 20;
  const baseline = height - 20;
  const prices = records.map((r) => Number(r.price));
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const range = max - min || 1;

  const step = width / (records.length - 1);

  const points = prices
    .map((price, i) => {
      const x = i * step;
      const y = baseline - ((price - min) / range) * (baseline - top);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  const yLabels = [0, 1, 2, 3, 4].map((i) =>
    formatPrice(max - (range * i) / 4),
  );

  const xLabels = [0, 0.25, 0.5, 0.75, 1].map((i) => {
    const record = records[Math.round(i * (records.length - 1))];
    return new Date(record.timestamp).toLocaleTimeString("ru-RU", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  });

  return {
    points,
    yLabels,
    xLabels,
    min,
    max,
    first: prices[0],
    last: prices.at(-1),
  };
}
