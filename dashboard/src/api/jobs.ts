async function jobsRequest(
  token: string,
  method: string,
  headers: Record<string, any> | null = null,
  body: any = null,
  endpoint = ""
) {
  return fetch(`/api/jobs/${endpoint}`, {
    headers: new Headers({
      Authorization: `Bearer ${token}`,
      ...headers
    }),
    method,
    body
  });
}
export async function create(token: string, job: Record<string, any>) {
  return jobsRequest(token, "post", null, JSON.stringify(job));
}
export async function read(token: string, jobId: string) {
  return jobsRequest(token, "get", null, null, `${jobId}`);
}
export async function addData(
  token: string,
  jobId: string,
  dataId: string,
  csv: string
) {
  const data = new FormData();
  data.append("file", new Blob([csv], { type: "text/csv" }));
  return jobsRequest(token, "post", null, data, `${jobId}/data/${dataId}`);
}
export async function getData(
  token: string,
  jobId: string,
  dataId: string,
  accept = "application/vnd.apache.arrow.file"
) {
  return jobsRequest(
    token,
    "get",
    { Accept: accept },
    null,
    `${jobId}/data/${dataId}`
  );
}
export async function getResults(token: string, jobId: string) {
  return jobsRequest(token, "get", null, null, `${jobId}/results`);
}
export async function getSingleResults(
  token: string,
  jobId: string,
  resultId: string
) {
  return jobsRequest(token, "get", null, null, `${jobId}/results/${resultId}`);
}
export async function compute(token: string, jobId: string) {
  return jobsRequest(token, "post", null, null, `${jobId}/compute`);
}
