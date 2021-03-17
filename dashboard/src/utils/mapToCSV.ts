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
  mapping: Record<string, Mapping>
) {
  const originalHeaders: Array<CSVHeader> = [];
  let mappedHeaders: Array<string | number> = [];
  const hasHeaders = !Array.isArray(data[0]);
  for (const mapped in mapping) {
    let originalIndex: string | number;
    const originalHeader = mapping[mapped].csv_header;
    if (originalHeader.header !== undefined) {
      originalIndex = originalHeader.header;
    } else {
      originalIndex = originalHeader.header_index;
    }
    originalHeaders.push(originalHeader);
    mappedHeaders.push(mapped);
    const originalUnits = mapping[mapped].units;

    if (originalUnits !== undefined) {
      const converter = getUnitConverter(originalUnits, "W");
      if (converter) {
        data.forEach((row: Record<string, number>) => {
          row[originalIndex] = converter(row[originalIndex]);
        });
      }
    }
  }
  if (!hasHeaders) {
    // If headers were not provided, we cannot unparse particular columns,
    // so generate the expected headers.
    const headersOut = data[0].map(() => "");
    for (let i = 0; i < originalHeaders.length; i++) {
      const columnIndex = originalHeaders[i].header_index;
      const newHeader = mappedHeaders[i];
      headersOut[columnIndex] = newHeader;
    }
    mappedHeaders = headersOut;
  }
  const newHeaders = papa.unparse(
    { fields: mappedHeaders, data: [] },
    { header: true }
  );
  let dataOut: string;
  if (hasHeaders) {
    // Headers were provided, we can use papa.unparse to parse those fields from objects
    dataOut = papa.unparse(
      {
        fields: originalHeaders.map((x: CSVHeader) => x.header),
        data: data
      },
      {
        header: false
      }
    );
  } else {
    dataOut = papa.unparse(data, {
      header: false
    });
  }
  return newHeaders + dataOut;
}
