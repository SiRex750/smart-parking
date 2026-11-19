import { SLOT_NAMES } from "../format.js";

function Bolt() {
  return (
    <svg className="bolt" viewBox="0 0 12 18" aria-hidden="true">
      <path d="M7 0 0 10h5l-1 8 8-11H7z" />
    </svg>
  );
}

function Bay({ slot, onSelect }) {
  const label = `${slot.slot_id}, ${SLOT_NAMES[slot.slot_type]}${slot.is_ev ? ", EV charging" : ""}: ${
    slot.status === "occupied" ? `occupied by ${slot.occupied_by}` : slot.status
  }`;
  const clickable = slot.status === "occupied";
  return (
    <li
      className={`bay bay--${slot.slot_type} bay--${slot.status}`}
      aria-label={label}
      title={label}
      onClick={clickable ? () => onSelect(slot) : undefined}
      onKeyDown={clickable ? (e) => (e.key === "Enter" || e.key === " ") && onSelect(slot) : undefined}
      tabIndex={clickable ? 0 : undefined}
      role={clickable ? "button" : undefined}
    >
      <span className="bay__id">
        {slot.slot_id}
        {slot.is_ev && <Bolt />}
      </span>
      {slot.status === "occupied" && <span className="plate">{slot.occupied_by}</span>}
      {slot.status === "reserved" && <span className="bay__note">Reserved</span>}
      <span className="bay__type">{SLOT_NAMES[slot.slot_type]}</span>
    </li>
  );
}

export default function LotMap({ slots, onSelectOccupied }) {
  const levels = [...new Set(slots.map((s) => s.level))].sort((a, b) => a - b);
  return (
    <div className="lot">
      {levels.map((level) => (
        <section key={level} className="level" aria-label={`Level ${level}`}>
          <h3 className="level__name">Level {level}</h3>
          <ul className="bays">
            {slots.filter((s) => s.level === level).map((slot) => (
              <Bay key={slot.slot_id} slot={slot} onSelect={onSelectOccupied} />
            ))}
          </ul>
          <div className="lane" aria-hidden="true" />
        </section>
      ))}
    </div>
  );
}
