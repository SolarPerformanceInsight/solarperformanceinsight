import { DateTime } from "luxon";

export default function(timestamp: number, tz: string): Date {
  const dt = DateTime.fromMillis(timestamp);
  return dt.minus({ minutes: dt.offset - dt.setZone(tz).offset }).toJSDate();
}
