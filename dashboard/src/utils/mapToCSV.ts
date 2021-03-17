import papa from "papaparse";
import { getUnitConverter } from "@/utils/unitConversion";

export interface CSVHeader {
  header?: string;
  header_index: number;
}
export interface Mapping {
  csv_header: CSVHeader;
  units?: string;
}

export function mapToCSV(
  data: Array<Record<string, any>> | Array<Array<string>>,
  Mapping: Record<string, Mapping>
) {
  const originalHeaders: Array<string | number> = [];
  const mappedHeaders: Array<string | number> = [];
  const hasHeaders = !Array.isArray(data[0]);

  for (const mapped in Mapping) {
    let originalHeader: string | number;
    if (Mapping[mapped].csv_header.header) {
      // @ts-expect-error
      originalHeader = Mapping[mapped].csv_header.header;
    } else {
      originalHeader = Mapping[mapped].csv_header.header_index;
    }
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
