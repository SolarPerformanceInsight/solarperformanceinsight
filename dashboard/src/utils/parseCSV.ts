import Papa from "papaparse";

export default async function(csvString: string, previewLines: number) {
  const parsed = Papa.parse(csvString, {
    header: true,
    dynamicTyping: true,
    preview: previewLines
  });
  return parsed;
}
