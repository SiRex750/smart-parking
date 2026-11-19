import { useState } from "react";
import VehicleFields from "./VehicleFields.jsx";

const EMPTY = { plate: "", vehicle_type: "car", is_ev: false };

export default function EntryPanel({ run }) {
  const [vehicle, setVehicle] = useState(EMPTY);

  async function submit(e) {
    e.preventDefault();
    const ok = await run(
      (api) => api.enter(vehicle),
      (t) => `Ticket issued: ${t.plate} parks in ${t.slot_id}.`,
    );
    if (ok) setVehicle(EMPTY);
  }

  return (
    <form className="panel-form" onSubmit={submit}>
      <p className="hint">The best free bay for the vehicle is picked automatically: smallest suitable size, lowest level, EV bays kept for EVs.</p>
      <VehicleFields value={vehicle} onChange={setVehicle} idPrefix="entry" />
      <button className="btn" type="submit">Issue ticket</button>
    </form>
  );
}
