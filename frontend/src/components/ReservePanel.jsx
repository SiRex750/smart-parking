import { useState } from "react";
import VehicleFields from "./VehicleFields.jsx";
import { time } from "../format.js";

const EMPTY = { plate: "", vehicle_type: "car", is_ev: false };

export default function ReservePanel({ run }) {
  const [vehicle, setVehicle] = useState(EMPTY);
  const [minutes, setMinutes] = useState(30);

  async function submit(e) {
    e.preventDefault();
    const ok = await run(
      (api) => api.reserve(vehicle, Number(minutes)),
      (r) => `${r.slot_id} is held for ${r.plate} from ${time(r.start_time)}.`,
    );
    if (ok) setVehicle(EMPTY);
  }

  return (
    <form className="panel-form" onSubmit={submit}>
      <p className="hint">The bay is held until 15 minutes after the arrival time, then released automatically.</p>
      <VehicleFields value={vehicle} onChange={setVehicle} idPrefix="reserve" />
      <label className="field" htmlFor="reserve-minutes">
        <span>Arriving in (minutes)</span>
        <input id="reserve-minutes" type="number" min="0" step="5" value={minutes}
          onChange={(e) => setMinutes(e.target.value)} />
      </label>
      <button className="btn" type="submit">Reserve bay</button>
    </form>
  );
}
