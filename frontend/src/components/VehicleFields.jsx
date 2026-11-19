import { TYPE_NAMES } from "../format.js";

// Shared plate / vehicle type / EV inputs for entry and reservation.
export default function VehicleFields({ value, onChange, idPrefix }) {
  const set = (patch) => onChange({ ...value, ...patch });
  return (
    <>
      <label className="field" htmlFor={`${idPrefix}-plate`}>
        <span>Number plate</span>
        <input
          id={`${idPrefix}-plate`}
          className="plate-input"
          value={value.plate}
          onChange={(e) => set({ plate: e.target.value.toUpperCase() })}
          placeholder="KA01AB1234"
          autoComplete="off"
          required
        />
      </label>
      <fieldset className="field">
        <legend>Vehicle</legend>
        <div className="segmented">
          {Object.entries(TYPE_NAMES).map(([key, name]) => (
            <label key={key} className={value.vehicle_type === key ? "is-on" : ""}>
              <input
                type="radio"
                name={`${idPrefix}-type`}
                value={key}
                checked={value.vehicle_type === key}
                onChange={() => set({ vehicle_type: key })}
              />
              {name}
            </label>
          ))}
        </div>
      </fieldset>
      <label className="check">
        <input type="checkbox" checked={value.is_ev} onChange={(e) => set({ is_ev: e.target.checked })} />
        Electric vehicle
      </label>
    </>
  );
}
