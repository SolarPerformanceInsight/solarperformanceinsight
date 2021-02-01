import { DateTime } from "luxon";

export default function(timestamp: number, tz: string): Date {
  const dt = DateTime.fromMillis(timestamp).setZone(tz);
  return new Date(
    dt.year,
    dt.month - 1, // 0-indexed
    dt.day,
    dt.hour,
    dt.minute,
    dt.second,
    dt.millisecond
  );
}
