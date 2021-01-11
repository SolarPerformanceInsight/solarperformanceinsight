import papa from "papaparse";

export default function(
  data: Array<Record<string, any>>,
  Mapping: Record<string, string>
) {
  const originalHeaders: Array<string> = [];
  const mappedHeaders: Array<string> = [];
  for (const mapped in Mapping) {
    originalHeaders.push(Mapping[mapped]);
    mappedHeaders.push(mapped);
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
