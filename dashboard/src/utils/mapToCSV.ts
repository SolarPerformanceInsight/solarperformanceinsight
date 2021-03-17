import papa from "papaparse";
import { getUnitConverter } from "@/utils/unitConversion";

export default function(
  data: Array<Record<string, any>>,
  Mapping: Record<string, Record<string, string>>
) {
  const originalHeaders: Array<string> = [];
  const mappedHeaders: Array<string> = [];
  for (const mapped in Mapping) {
    const originalHeader = Mapping[mapped].csv_header;
    originalHeaders.push(originalHeader);
    mappedHeaders.push(mapped);
    if ("units" in Mapping[mapped]) {
      const originalUnits = Mapping[mapped].units;
      const converter = getUnitConverter(originalUnits, "W");
      if (converter) {
        data.forEach((row: Record<string, number>) => {
          row[originalHeader] = converter(row[originalHeader]);
        });
      }
    }
  }
  const newHeaders = papa.unparse(
    { fields: mappedHeaders, data: [] },
    { header: true }
  );
  const newData = papa.unparse(
    { fields: originalHeaders, data: data },
    { header: false }
  );
  return newHeaders + newData;
}
