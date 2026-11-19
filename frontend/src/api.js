// Thin client for the Flask REST API (smart_parking/api.py). Errors carry the API's message.
async function request(path, { method = "GET", body } = {}) {
  const res = await fetch(`/api${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

export const api = {
  state: () => request("/state"),
  report: () => request("/report"),
  enter: (vehicle) => request("/entries", { method: "POST", body: vehicle }),
  fee: (ticketId) => request(`/tickets/${ticketId}/fee`),
  pay: (ticketId, amount, method) => request("/payments", { method: "POST", body: { ticket_id: ticketId, amount, method } }),
  exit: (ticketId) => request(`/exits/${ticketId}`, { method: "POST" }),
  reserve: (vehicle, minutesFromNow) =>
    request("/reservations", { method: "POST", body: { ...vehicle, minutes_from_now: minutesFromNow } }),
  cancel: (reservationId) => request(`/reservations/${reservationId}`, { method: "DELETE" }),
  checkIn: (reservationId) => request(`/reservations/${reservationId}/check-in`, { method: "POST" }),
  advance: (minutes) => request("/clock", { method: "POST", body: { advance_minutes: minutes } }),
  reset: () => request("/reset", { method: "POST" }),
};
