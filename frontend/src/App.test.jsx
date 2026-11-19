import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "./App.jsx";

const slot = (slot_id, slot_type, level, status = "free", occupied_by = null) =>
  ({ slot_id, slot_type, level, is_ev: false, status, occupied_by });

const STATE = {
  lot: "PES Campus Lot",
  now: "2026-11-20T10:01:00",
  occupancy: { total: 4, occupied: 1, reserved: 1, available: 2 },
  slots: [
    slot("L0-C1", "compact", 0, "occupied", "KA01AB1234"),
    slot("L0-C2", "compact", 0, "reserved"),
    slot("L0-L1", "large", 0),
    slot("L1-B1", "two_wheeler", 1),
  ],
  tickets: [{ ticket_id: "t1", plate: "KA01AB1234", slot_id: "L0-C1", vehicle_type: "car",
    entry_time: "2026-11-20T09:00:00", exit_time: null, amount_due: 0, paid: false }],
  reservations: [{ reservation_id: "r1", plate: "MH12XY0001", vehicle_type: "car", slot_id: "L0-C2",
    start_time: "2026-11-20T10:30:00", status: "ACTIVE" }],
};

function mockApi(handlers = {}) {
  const calls = [];
  global.fetch = vi.fn(async (url, opts = {}) => {
    const key = `${opts.method || "GET"} ${url}`;
    calls.push({ key, body: opts.body ? JSON.parse(opts.body) : undefined });
    const [status, body] = handlers[key] || [200, STATE];
    return { ok: status < 400, status, json: async () => body };
  });
  return calls;
}

afterEach(() => { cleanup(); vi.restoreAllMocks(); });

describe("App", () => {
  it("draws the lot from the API state", async () => {
    mockApi();
    render(<App />);
    expect(await screen.findByRole("heading", { name: "PES Campus Lot" })).toBeInTheDocument();
    expect(screen.getByLabelText("L0-C1, Compact: occupied by KA01AB1234")).toBeInTheDocument();
    expect(screen.getByLabelText("L0-C2, Compact: reserved")).toBeInTheDocument();
    expect(screen.getByText("2 free")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Level 1" })).toBeInTheDocument();
  });

  it("shows a clear message when the API is down", async () => {
    global.fetch = vi.fn(async () => { throw new Error("Failed to fetch"); });
    render(<App />);
    expect(await screen.findByText(/Can't reach the parking API/)).toBeInTheDocument();
  });

  it("issues a ticket from the entry form", async () => {
    const calls = mockApi({
      "POST /api/entries": [201, { ticket_id: "t2", plate: "KA05MN4321", slot_id: "L0-L1" }],
    });
    render(<App />);
    fireEvent.change(await screen.findByLabelText("Number plate"), { target: { value: "ka05mn4321" } });
    fireEvent.click(screen.getByLabelText("SUV"));
    fireEvent.click(screen.getByRole("button", { name: "Issue ticket" }));
    expect(await screen.findByText("Ticket issued: KA05MN4321 parks in L0-L1.")).toBeInTheDocument();
    expect(calls.find((c) => c.key === "POST /api/entries").body)
      .toEqual({ plate: "KA05MN4321", vehicle_type: "suv", is_ev: false });
  });

  it("shows the API error message when entry is refused", async () => {
    mockApi({ "POST /api/entries": [409, { error: "Lot full for suv" }] });
    render(<App />);
    fireEvent.change(await screen.findByLabelText("Number plate"), { target: { value: "KA05MN4321" } });
    fireEvent.click(screen.getByRole("button", { name: "Issue ticket" }));
    expect(await screen.findByText("Lot full for suv")).toBeInTheDocument();
  });

  it("checks the fee, takes payment and opens the gate", async () => {
    const paid = { ...STATE.tickets[0], amount_due: 60, paid: true };
    mockApi({
      "GET /api/tickets/t1/fee": [200, { ...STATE.tickets[0], amount_due: 60 }],
      "POST /api/payments": [201, { ticket: paid, gateway_ref: "MOCK-1", receipt: "SMART PARKING - RECEIPT\nAmount   : Rs 60.00" }],
      "POST /api/exits/t1": [200, { ...paid, exit_time: "2026-11-20T10:02:00" }],
    });
    render(<App />);
    fireEvent.click(await screen.findByLabelText("L0-C1, Compact: occupied by KA01AB1234"));
    fireEvent.click(await screen.findByRole("button", { name: "Check fee" }));
    fireEvent.click(await screen.findByRole("button", { name: "Take payment of ₹60" }));
    expect(await screen.findByLabelText("Receipt")).toHaveTextContent("Rs 60.00");
  });

  it("checks in and cancels reservations", async () => {
    const calls = mockApi({
      "POST /api/reservations/r1/check-in": [201, { plate: "MH12XY0001", slot_id: "L0-C2" }],
    });
    render(<App />);
    fireEvent.click(await screen.findByRole("button", { name: "Check in" }));
    expect(await screen.findByText("MH12XY0001 checked in to L0-C2.")).toBeInTheDocument();
    await waitFor(() => expect(calls.some((c) => c.key === "POST /api/reservations/r1/check-in")).toBe(true));
  });
});
