import papa from "papaparse";
import { getUnitConverter } from "@/utils/unitConversion";

export interface Mapping {
  csv_header: string | number;
  units?: string;
}

export function mapToCSV(
  data: Array<Record<string, any>>| Array<Array<string>>,
  Mapping: Record<string, Mapping>
) {
  const originalHeaders: Array<string | number> = [];
  const mappedHeaders: Array<string | number> = [];
  if (Array.isArray(data[0])){
    // Handle no-header array data
  }
  for (const mapped in Mapping) {
    const originalHeader = Mapping[mapped].csv_header;
    originalHeaders.push(originalHeader);
    mappedHeaders.push(mapped);
    const originalUnits = Mapping[mapped].units;
    if (originalUnits !== undefined) {
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
