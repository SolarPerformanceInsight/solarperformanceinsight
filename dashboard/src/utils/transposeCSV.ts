import csvToJson from "csvtojson";

export default async function(csvString: string) {
  /* Parses a csv file into an object mapping csv headers to column data. This
   * is useful for later producing an Arrow Table from the data.
   */
  const csvJson = await csvToJson().fromString(csvString);
  const transposed: Record<string, Array<any>> = {};
  const headers: Array<string> = Object.keys(csvJson[0]);
  for (const header of headers) {
    transposed[header] = csvJson.map(e => e[header]);
  }
  return transposed;
}
