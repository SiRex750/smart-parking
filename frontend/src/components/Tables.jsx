import { SLOT_NAMES, TYPE_NAMES, rupees, time } from "../format.js";

export function ParkedTable({ tickets, onSelect }) {
  const open = tickets.filter((t) => !t.exit_time);
  if (open.length === 0) return <p className="empty">The lot is empty.</p>;
  return (
    <table>
      <thead>
        <tr><th>Plate</th><th>Vehicle</th><th>Bay</th><th>Since</th><th>Payment</th><th /></tr>
      </thead>
      <tbody>
        {open.map((t) => (
          <tr key={t.ticket_id}>
            <td><span className="plate plate--small">{t.plate}</span></td>
            <td>{TYPE_NAMES[t.vehicle_type]}</td>
            <td>{t.slot_id}</td>
            <td>{time(t.entry_time)}</td>
            <td>{t.paid ? `Paid ${rupees(t.amount_due)}` : "Not paid"}</td>
            <td><button className="link" type="button" onClick={() => onSelect(t.ticket_id)}>Exit</button></td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

const STATUS = { ACTIVE: "Held", USED: "Checked in", CANCELLED: "Cancelled", EXPIRED: "Expired (no-show)" };

export function ReservationsTable({ reservations, run }) {
  if (reservations.length === 0) return <p className="empty">No reservations yet. Reserve a bay from the Reservation tab.</p>;
  const sorted = [...reservations].sort((a, b) => (a.status === "ACTIVE" ? -1 : 0) - (b.status === "ACTIVE" ? -1 : 0));
  return (
    <table>
      <thead>
        <tr><th>Plate</th><th>Bay</th><th>Arrives</th><th>Status</th><th /></tr>
      </thead>
      <tbody>
        {sorted.map((r) => (
          <tr key={r.reservation_id} className={r.status === "ACTIVE" ? "" : "is-done"}>
            <td><span className="plate plate--small">{r.plate}</span></td>
            <td>{r.slot_id}</td>
            <td>{time(r.start_time)}</td>
            <td>{STATUS[r.status]}</td>
            <td className="actions">
              {r.status === "ACTIVE" && (
                <>
                  <button className="link" type="button"
                    onClick={() => run((api) => api.checkIn(r.reservation_id), (t) => `${t.plate} checked in to ${t.slot_id}.`)}>
                    Check in
                  </button>
                  <button className="link link--danger" type="button"
                    onClick={() => run((api) => api.cancel(r.reservation_id), (x) => `Reservation for ${x.plate} cancelled. ${x.slot_id} is free.`)}>
                    Cancel
                  </button>
                </>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function ReportTable({ slots }) {
  const levels = [...new Set(slots.map((s) => s.level))].sort((a, b) => a - b);
  const types = Object.keys(SLOT_NAMES).filter((t) => slots.some((s) => s.slot_type === t));
  const cell = (level, type) => {
    const here = slots.filter((s) => s.level === level && s.slot_type === type);
    return { free: here.filter((s) => s.status === "free").length, total: here.length };
  };
  return (
    <table className="report" aria-label="Free bays by level and size">
      <thead>
        <tr><th>Free bays</th>{levels.map((l) => <th key={l}>Level {l}</th>)}</tr>
      </thead>
      <tbody>
        {types.map((type) => (
          <tr key={type}>
            <td>{SLOT_NAMES[type]}</td>
            {levels.map((level) => {
              const c = cell(level, type);
              return <td key={level} className={c.total && !c.free ? "none" : ""}>{c.total ? `${c.free} of ${c.total}` : "–"}</td>;
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
