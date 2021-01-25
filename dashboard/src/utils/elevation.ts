/* Queries elevation from USGS The National Map Elevation Point Query Service */
export async function getElevation(lat: number, lon: number) {
  const resp = await fetch(
    `https://nationalmap.gov/epqs/pqs.php?x=${lon}&y=${lat}&units=Meters&output=json`
  );
  if (resp.ok) {
    const respJSON = await resp.json();
    const elevation =
      respJSON["USGS_Elevation_Point_Query_Service"]["Elevation_Query"]
        .Elevation;
    if (elevation != "-1000000") {
      return elevation;
    } else {
      throw new Error("Elevation could not be found");
    }
  } else {
    throw new Error(`Elevation fetch failed with code ${resp.status}`);
  }
}
