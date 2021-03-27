import Papa from "papaparse";

export default function(
  csvString: string,
  headerExists = true,
  previewLines = 0
): Papa.ParseResult<Record<string, Array<string | number>>> {
  const parsed: Papa.ParseResult<Record<
    string,
    Array<string | number>
  >> = Papa.parse(csvString, {
    header: headerExists,
    dynamicTyping: true,
    preview: previewLines
  });
  return parsed;
}
