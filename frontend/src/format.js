// Display helpers. Times come from the API as local ISO strings without a zone.
const pad = (n) => String(n).padStart(2, "0");

export function time(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function day(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short" });
}

export function rupees(amount) {
  return `₹${Number(amount || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

export function duration(fromIso, toIso) {
  const minutes = Math.max(0, Math.round((new Date(toIso) - new Date(fromIso)) / 60000));
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h ? `${h} h ${pad(m)} min` : `${m} min`;
}

export const TYPE_NAMES = { bike: "Bike", car: "Car", suv: "SUV" };
export const SLOT_NAMES = { two_wheeler: "Two-wheeler", compact: "Compact", large: "Large" };
