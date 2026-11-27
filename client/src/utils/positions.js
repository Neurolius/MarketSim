export function calcPosition(position) {
  const quantity = Number(position.quantity);
  const average = Number(position.average_price);
  const current = Number(position.instrument_info.current_price);
  const value = Number(position.position_value);
  const profit = Number(position.position_profit);
  const cost = quantity * average;
  const percent = cost ? (profit / cost) * 100 : 0;

  return {
    quantity,
    average,
    current,
    value,
    profit,
    percent,
  };
}
