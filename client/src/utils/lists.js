export const byId = (list) =>
  Object.fromEntries(list.map((item) => [item.id, item]));

export const sortByNewest = (list, field = "created_at") =>
  [...list].sort((a, b) => new Date(b[field]) - new Date(a[field]));

export const inRange = (value, from, to) =>
  (from === "" || value >= from) && (to === "" || value <= to);

export const matchesText = (text, search) =>
  !search.trim() || text.toLowerCase().includes(search.trim().toLowerCase());
