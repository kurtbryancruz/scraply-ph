const API_BASE = "http://127.0.0.1:8000";

let currentPage = 1;
let lastKeyword = "";
let lastLocation = "";
let lastSource = "";
let lastJobs = [];

const $ = (id) => document.getElementById(id);

function setStatus(msg) { $("status").textContent = msg; }

function renderJobs(jobs) {
  const tbody = $("jobs-body");
  tbody.innerHTML = "";

  if (!jobs.length) {
    $("jobs-table").classList.add("hidden");
    $("no-results").classList.remove("hidden");
    $("export-btn").disabled = true;
    return;
  }

  $("no-results").classList.add("hidden");
  $("jobs-table").classList.remove("hidden");
  $("export-btn").disabled = false;

  jobs.forEach((job) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${job.title ?? "—"}</td>
      <td>${job.company ?? "—"}</td>
      <td>${job.location ?? "—"}</td>
      <td>${job.salary ?? "—"}</td>
      <td>${job.source ?? "—"}</td>
      <td>${job.url ? `<a href="${job.url}" target="_blank" rel="noreferrer">View</a>` : "—"}</td>
    `;
    tbody.appendChild(tr);
  });
}

async function fetchJobs(keyword, location, source, page) {
  const params = new URLSearchParams({ keyword, location, source, page });
  const res = await fetch(`${API_BASE}/scrape?${params}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? res.statusText);
  }
  return res.json();
}

async function search(page = 1) {
  const keyword = $("keyword").value.trim();
  const location = $("location").value.trim();
  const source = $("source").value;

  if (!keyword) { setStatus("Please enter a keyword."); return; }

  lastKeyword = keyword;
  lastLocation = location;
  lastSource = source;
  currentPage = page;

  setStatus("Searching…");
  $("search-btn").disabled = true;
  $("export-btn").disabled = true;
  $("jobs-table").classList.add("hidden");
  $("no-results").classList.add("hidden");
  $("pagination").classList.add("hidden");

  try {
    const data = await fetchJobs(keyword, location, source, page);
    lastJobs = data.jobs ?? [];
    renderJobs(lastJobs);
    setStatus(`Found ${data.count} result(s) on page ${page}.`);
    updatePagination(page, data.count);
  } catch (err) {
    setStatus(`Error: ${err.message}`);
  } finally {
    $("search-btn").disabled = false;
  }
}

function updatePagination(page, count) {
  $("pagination").classList.remove("hidden");
  $("page-label").textContent = `Page ${page}`;
  $("prev-btn").disabled = page <= 1;
  $("next-btn").disabled = count === 0;
}

function exportCSV() {
  if (!lastJobs.length) return;
  const params = new URLSearchParams({
    keyword: lastKeyword,
    location: lastLocation,
    source: lastSource,
    page: currentPage,
    format: "csv",
  });
  window.open(`${API_BASE}/scrape?${params}`, "_blank");
}

$("search-btn").addEventListener("click", () => search(1));
$("keyword").addEventListener("keydown", (e) => e.key === "Enter" && search(1));
$("prev-btn").addEventListener("click", () => search(currentPage - 1));
$("next-btn").addEventListener("click", () => search(currentPage + 1));
$("export-btn").addEventListener("click", exportCSV);
