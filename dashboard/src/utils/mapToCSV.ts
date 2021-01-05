export default function(
  data: Record<string, Array<any>>,
  Mapping: Record<string, string>
) {
  const headers: Array<string> = [];
  const columns: Array<any> = [];

  // collect headers and columns in order
  for (const mapped in Mapping) {
    const orig = Mapping[mapped];
    headers.push(mapped);
    if (mapped == "time") {
      columns.push(data[orig]);
    } else {
      columns.push(Float32Array.from(data[orig]));
    }
  }
  // zip columns of values into rows
  const rows: Array<any> = []
  columns[0].forEach((v: Array<any>, i: number) => {
    const row = [v];
    for (let j = 1; j < columns.length; j++) {
      row.push(columns[j][i]);
    }
    rows.push(row);
  });
  // append headers
  let csv = headers.join(",") + "\n";
  // append rows of values
  rows.map((row: Array<any>) => {
    csv += row.join(",") + "\n";
  });
  return csv;
}
