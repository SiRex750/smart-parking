import { describe, expect, it } from "vitest";
import { day, duration, rupees, time } from "./format.js";

describe("format helpers", () => {
  it("formats clock time", () => {
    expect(time("2026-11-20T09:05:00")).toBe("09:05");
    expect(time(null)).toBe("");
  });
  it("formats rupees without decimals", () => {
    expect(rupees(60)).toBe("₹60");
    expect(rupees(1240)).toBe("₹1,240");
    expect(rupees(undefined)).toBe("₹0");
  });
  it("formats durations", () => {
    expect(duration("2026-11-20T09:00:00", "2026-11-20T09:10:00")).toBe("10 min");
    expect(duration("2026-11-20T09:00:00", "2026-11-20T10:01:00")).toBe("1 h 01 min");
  });
  it("formats the day", () => {
    expect(day("2026-11-20T09:00:00")).toMatch(/20/);
    expect(day("")).toBe("");
  });
});
