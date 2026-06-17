const BASE = "/api/v1";

async function request(method, path, body) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const res = await fetch(BASE + path, opts);
  if (res.status === 204) return null;
  const data = await res.json();
  if (!res.ok) throw { status: res.status, detail: data.detail ?? JSON.stringify(data) };
  return data;
}

export const api = {
  listAntennas: () => request("GET", "/antennas"),
  createAntenna: (spec) => request("POST", "/antennas", spec),
  getAntenna: (id) => request("GET", `/antennas/${id}`),
  updateAntenna: (id, spec) => request("PUT", `/antennas/${id}`, spec),
  deleteAntenna: (id) => request("DELETE", `/antennas/${id}`),
  previewAntenna: (req) => request("POST", "/sandbox/preview", req),
  createScenario: (scenario) => request("POST", "/scenarios", scenario),
  getScenario: (id) => request("GET", `/scenarios/${id}`),
  calculateScenario: (id) => request("POST", `/scenarios/${id}/calculate`),
};
