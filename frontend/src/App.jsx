import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";
import { day, time } from "./format.js";
import LotMap from "./components/LotMap.jsx";
import EntryPanel from "./components/EntryPanel.jsx";
import ExitPanel from "./components/ExitPanel.jsx";
import ReservePanel from "./components/ReservePanel.jsx";
import { ParkedTable, ReportTable, ReservationsTable } from "./components/Tables.jsx";

const TABS = [
  ["entry", "Vehicle entry"],
  ["exit", "Exit and payment"],
  ["reserve", "Reservation"],
];

export default function App() {
  const [state, setState] = useState(null);
  const [loadError, setLoadError] = useState("");
  const [notice, setNotice] = useState(null);
  const [tab, setTab] = useState("entry");
  const [selectedTicket, setSelectedTicket] = useState("");

  const refresh = useCallback(async () => {
    try {
      setState(await api.state());
      setLoadError("");
    } catch (err) {
      setLoadError(err.message);
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 5000);
    return () => clearInterval(id);
  }, [refresh]);

  // Runs one API action, shows its outcome, then reloads the lot. Returns true on success.
  const run = useCallback(async (action, describe) => {
    try {
      const result = await action(api);
      setNotice({ kind: "ok", text: describe(result) });
      await refresh();
      return true;
    } catch (err) {
      setNotice({ kind: "error", text: err.message });
      await refresh();
      return false;
    }
  }, [refresh]);

  const selectForExit = (ticketId) => {
    setSelectedTicket(ticketId);
    setTab("exit");
  };

  if (!state) {
    return (
      <main className="boot">
        <p>{loadError ? `Can't reach the parking API: ${loadError}. Start it with: python -m smart_parking.api` : "Loading the lot…"}</p>
      </main>
    );
  }

  const occ = state.occupancy;
  const occupiedBySlot = Object.fromEntries(state.tickets.filter((t) => !t.exit_time).map((t) => [t.slot_id, t.ticket_id]));

  return (
    <div className="app">
      <header className="top">
        <div className="brand">
          <span className="sign" aria-hidden="true">P</span>
          <div>
            <h1>{state.lot}</h1>
            <p className="legend">
              <span className="key key--free" /><span>{`${occ.available} free`}</span>
              <span className="key key--occupied" /><span>{`${occ.occupied} parked`}</span>
              <span className="key key--reserved" /><span>{`${occ.reserved} reserved`}</span>
              <span className="of">{`of ${occ.total} bays`}</span>
            </p>
          </div>
        </div>
        <div className="clock">
          <p><span className="clock__day">{day(state.now)}</span> <strong>{time(state.now)}</strong></p>
          <div className="clock__actions">
            <button className="btn btn--quiet" type="button" onClick={() => run((a) => a.advance(15), () => "Clock moved forward 15 minutes.")}>+15 min</button>
            <button className="btn btn--quiet" type="button" onClick={() => run((a) => a.advance(60), () => "Clock moved forward 1 hour.")}>+1 hour</button>
            <button className="btn btn--quiet" type="button" onClick={() => run((a) => a.reset(), () => "Lot reset: all bays are free.")}>Reset lot</button>
          </div>
        </div>
      </header>

      {notice && (
        <p className={`notice notice--${notice.kind}`} role="status">
          {notice.text}
          <button className="link" type="button" onClick={() => setNotice(null)} aria-label="Dismiss message">Dismiss</button>
        </p>
      )}

      <main className="grid">
        <section className="map-area" aria-label="Lot map">
          <LotMap slots={state.slots} onSelectOccupied={(slot) => selectForExit(occupiedBySlot[slot.slot_id])} />
          <ReportTable slots={state.slots} />
        </section>

        <section className="desk" aria-label="Gate desk">
          <div className="tabs" role="tablist">
            {TABS.map(([key, name]) => (
              <button key={key} role="tab" type="button" aria-selected={tab === key}
                className={tab === key ? "tab is-on" : "tab"} onClick={() => setTab(key)}>
                {name}
              </button>
            ))}
          </div>
          <div className="tab-body" role="tabpanel">
            {tab === "entry" && <EntryPanel run={run} />}
            {tab === "exit" && (
              <ExitPanel tickets={state.tickets} now={state.now} selectedId={selectedTicket}
                onSelect={setSelectedTicket} run={run} />
            )}
            {tab === "reserve" && <ReservePanel run={run} />}
          </div>
        </section>

        <section className="list" aria-label="Parked vehicles">
          <h2>Parked vehicles</h2>
          <ParkedTable tickets={state.tickets} onSelect={selectForExit} />
        </section>
        <section className="list" aria-label="Reservations">
          <h2>Reservations</h2>
          <ReservationsTable reservations={state.reservations} run={run} />
        </section>
      </main>
    </div>
  );
}
