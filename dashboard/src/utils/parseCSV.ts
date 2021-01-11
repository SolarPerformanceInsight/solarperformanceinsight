import Papa from "papaparse";

export default function(
  csvString: string,
  previewLines = 0
): Papa.ParseResult<Record<string, Array<string | number>>> {
  const parsed: Papa.ParseResult<Record<
    string,
    Array<string | number>
  >> = Papa.parse(csvString, {
    header: true,
    dynamicTyping: true,
    preview: previewLines
  });
  return parsed;
}
