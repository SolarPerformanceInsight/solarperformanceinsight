import adjustPlotTime from "@/utils/adjustPlotTimes";

describe("test adjustPlotTime", () => {
  const std_time = 1612094400000; // 2021-01-31T12:00:00Z
  const std_date = new Date("2021-01-31T05:00:00");
  const daylight_time = 1619784000000; // 2021-04-30T12:00:00Z
  const daylight_date = new Date("2021-04-30T06:00:00");
  it("checks the timezone", () => {
    expect(process.env.TZ).toBe("America/Denver");
    expect(daylight_date.toString()).toBe(
      "Fri Apr 30 2021 06:00:00 GMT-0600 (Mountain Daylight Time)"
    );
    expect(std_date.toString()).toBe(
      "Sun Jan 31 2021 05:00:00 GMT-0700 (Mountain Standard Time)"
    );
  });
  it("checks standard time to standard time", () => {
    expect(adjustPlotTime(std_time, "America/Denver")).toStrictEqual(std_date);
    expect(adjustPlotTime(std_time, "Etc/GMT+7")).toStrictEqual(std_date);
    expect(adjustPlotTime(std_time, "America/New_York")).toStrictEqual(
      new Date("2021-01-31T07:00:00")
    );
  });
  it("checks daylight time to daylight time", () => {
    expect(adjustPlotTime(daylight_time, "America/Denver")).toStrictEqual(
      daylight_date
    );
    expect(adjustPlotTime(daylight_time, "America/New_York")).toStrictEqual(
      new Date("2021-04-30T08:00:00")
    );
    expect(adjustPlotTime(daylight_time, "America/Los_Angeles")).toStrictEqual(
      new Date("2021-04-30T05:00:00")
    );
  });
  it("checks daylight to standard zone", () => {
    expect(adjustPlotTime(daylight_time, "Etc/GMT+7")).toStrictEqual(
      new Date("2021-04-30T05:00:00")
    );
    expect(adjustPlotTime(daylight_time, "America/Phoenix")).toStrictEqual(
      new Date("2021-04-30T05:00:00")
    );
    expect(adjustPlotTime(daylight_time, "Etc/GMT+5")).toStrictEqual(
      new Date("2021-04-30T07:00:00")
    );
    // check 2021-03-15T12:00:00Z, dst in US, still standard in germany +1
    expect(adjustPlotTime(1615809600000, "Europe/Berlin")).toStrictEqual(
      new Date("2021-03-15T13:00:00")
    );
  });
  it("checks transition periods", () => {
    const dst_start_ts = 1615712400000; // start of DST, 2021-03-14T09:00:00Z
    expect(adjustPlotTime(dst_start_ts, "America/Denver")).toStrictEqual(
      new Date("2021-03-14T03:00:00")
    );
    expect(adjustPlotTime(dst_start_ts, "Etc/GMT+7")).toStrictEqual(
      new Date("2021-03-14T02:00:00")
    );
    expect(adjustPlotTime(1615716000000, "Etc/GMT+7")).toStrictEqual(
      new Date("2021-03-14T03:00:00")
    );
    const dst_end_ts = 1636272000000; // 2021-11-07T08:00:00Z
    expect(adjustPlotTime(dst_end_ts - 1000, "America/Denver")).toStrictEqual(
      new Date("2021-11-07T01:59:59")
    );
    expect(adjustPlotTime(dst_end_ts, "America/Denver")).toStrictEqual(
      new Date("2021-11-07T01:00:00")
    );
    expect(adjustPlotTime(dst_end_ts, "America/New_York")).toStrictEqual(
      new Date("2021-11-07T03:00:00")
    );
    expect(adjustPlotTime(dst_end_ts, "Etc/GMT+7")).toStrictEqual(
      new Date("2021-11-07T01:00:00")
    );
  });
});
