export const byId = (list) =>
  Object.fromEntries(list.map((item) => [item.id, item]));

export const listResults = (data) => data.results ?? [];
