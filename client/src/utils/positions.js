export function calcPosition(position) {
  const quantity = Number(position.quantity);
  const average = Number(position.average_price);
  const current = Number(position.instrument_info.current_price);
  const value = quantity * current;
  const cost = quantity * average;
  const profit = value - cost;
  return {
    quantity,
    average,
    current,
    value,
    cost,
    profit,
    percent: cost ? (profit / cost) * 100 : 0,
  };
}
