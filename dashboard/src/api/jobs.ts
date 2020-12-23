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
export async function read(token: string, jobid: string) {
  return jobsRequest(token, "get", null, null, `/${jobid}`);
}
