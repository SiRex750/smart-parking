import { useEffect, useState } from "react";
import { duration, rupees, time } from "../format.js";

export default function ExitPanel({ tickets, now, selectedId, onSelect, run }) {
  const open = tickets.filter((t) => !t.exit_time);
  const ticket = open.find((t) => t.ticket_id === selectedId) || null;
  const [fee, setFee] = useState(null);
  const [method, setMethod] = useState("upi");
  const [receipt, setReceipt] = useState("");

  useEffect(() => {
    setFee(null);
    setReceipt("");
  }, [selectedId]);

  async function checkFee() {
    await run((api) => api.fee(ticket.ticket_id), (t) => {
      setFee(t.amount_due);
      return t.paid ? `${t.plate} has already paid.` : `${t.plate} owes ${rupees(t.amount_due)}.`;
    });
  }

  async function pay() {
    await run((api) => api.pay(ticket.ticket_id, fee, method), (r) => {
      setReceipt(r.receipt);
      return `Paid ${rupees(fee)} for ${r.ticket.plate}.`;
    });
  }

  async function openGate() {
    const ok = await run((api) => api.exit(ticket.ticket_id), (t) => `${t.plate} has left. ${t.slot_id} is free.`);
    if (ok) onSelect("");
  }

  if (open.length === 0) {
    return <p className="empty">No vehicles are parked. Issue a ticket from Vehicle entry first.</p>;
  }

  return (
    <div className="panel-form">
      <label className="field" htmlFor="exit-ticket">
        <span>Parked vehicle</span>
        <select id="exit-ticket" value={selectedId} onChange={(e) => onSelect(e.target.value)}>
          <option value="">Choose a vehicle</option>
          {open.map((t) => (
            <option key={t.ticket_id} value={t.ticket_id}>
              {t.plate} in {t.slot_id}, since {time(t.entry_time)}
            </option>
          ))}
        </select>
      </label>

      {ticket && (
        <div className="exit-steps">
          <p className="hint">
            Parked {duration(ticket.entry_time, now)}. First 15 minutes are free; then each started hour is charged.
          </p>
          {!ticket.paid && fee === null && (
            <button className="btn" type="button" onClick={checkFee}>Check fee</button>
          )}
          {!ticket.paid && fee > 0 && (
            <div className="pay-row">
              <p className="amount">{rupees(fee)} due</p>
              <label className="field" htmlFor="pay-method">
                <span>Paid by</span>
                <select id="pay-method" value={method} onChange={(e) => setMethod(e.target.value)}>
                  <option value="upi">UPI</option>
                  <option value="card">Card</option>
                  <option value="cash">Cash</option>
                </select>
              </label>
              <button className="btn" type="button" onClick={pay}>Take payment of {rupees(fee)}</button>
            </div>
          )}
          {(ticket.paid || fee === 0) && (
            <button className="btn btn--go" type="button" onClick={openGate}>Open exit gate</button>
          )}
          {receipt && <pre className="receipt" aria-label="Receipt">{receipt}</pre>}
        </div>
      )}
    </div>
  );
}
