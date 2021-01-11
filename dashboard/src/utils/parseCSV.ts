import Papa from "papaparse";

export default function(csvString: string, previewLines = 0) {
  const parsed = Papa.parse(csvString, {
    header: true,
    dynamicTyping: true,
    preview: previewLines
  });
  return parsed;
}
