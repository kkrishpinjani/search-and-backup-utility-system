function tsToLocal(ts) {
  if (!ts) return "-";
  const d = new Date(ts * 1000);
  return d.toLocaleString();
}

async function browseFolder() {
  try {
    const res = await fetch("/api/browse");
    const data = await res.json();
    if (data.path) {
      document.getElementById("scanRoot").value = data.path;
    }
  } catch (e) {
    console.error("Failed to open folder picker", e);
  }
}

function dateToTs(dateStr, endOfDay=false) {
  if (!dateStr) return null;
  const d = new Date(dateStr + "T00:00:00");
  if (endOfDay) d.setHours(23,59,59,999);
  return Math.floor(d.getTime() / 1000);
}

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body)
  });
  const data = await res.json();
  if (!data.ok) throw new Error(data.error || "Request failed");
  return data;
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function showMsg(containerId, msg, type="success") {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `<div class="alert alert-${type} py-2 mb-0">${escapeHtml(msg)}</div>`;
}

/* -----------------------------
   Autocomplete
--------------------------------*/
let suggestTimer = null;

function hideSuggest() {
  const box = document.getElementById("suggestBox");
  box.classList.add("d-none");
  box.innerHTML = "";
}

function showSuggest(items) {
  const box = document.getElementById("suggestBox");
  box.innerHTML = "";

  if (!items || items.length === 0) {
    hideSuggest();
    return;
  }

  for (const it of items) {
    const div = document.createElement("div");
    div.className = "suggestItem";
    div.innerHTML = `
      <div class="fw-semibold small">${escapeHtml(it.name)}</div>
      <div class="text-muted small mono">${escapeHtml(it.path)}</div>
    `;
    div.addEventListener("mousedown", () => {
      document.getElementById("qName").value = it.name;
      hideSuggest();
    });
    box.appendChild(div);
  }

  box.classList.remove("d-none");
}

async function fetchSuggest(q) {
  const res = await fetch(`/api/suggest?q=${encodeURIComponent(q)}&limit=10`);
  const data = await res.json();
  return data.ok ? (data.suggestions || []) : [];
}

function setupAutocomplete() {
  const input = document.getElementById("qName");
  const box = document.getElementById("suggestBox");

  input.addEventListener("input", () => {
    const q = input.value.trim();
    if (suggestTimer) clearTimeout(suggestTimer);

    if (q.length < 1) {
      hideSuggest();
      return;
    }

    suggestTimer = setTimeout(async () => {
      try {
        const items = await fetchSuggest(q);
        showSuggest(items);
      } catch {
        hideSuggest();
      }
    }, 180);
  });

  input.addEventListener("blur", () => setTimeout(hideSuggest, 120));

  document.addEventListener("click", (e) => {
    if (e.target === input || box.contains(e.target)) return;
    hideSuggest();
  });
}

/* -----------------------------
   Selection helpers
--------------------------------*/
function selectAllResults(checked) {
  document.querySelectorAll(".pickRow").forEach(cb => {
    cb.checked = checked;
    toggleRowHighlight(cb);
  });
}

function toggleRowHighlight(cb) {
  const tr = cb.closest("tr");
  if (!tr) return;
  if (cb.checked) tr.classList.add("row-selected");
  else tr.classList.remove("row-selected");
}

function getSelectedPaths() {
  const paths = [];
  document.querySelectorAll(".pickRow:checked").forEach(cb => {
    paths.push(cb.getAttribute("data-path"));
  });
  return paths;
}

async function backupSelected() {
  try {
    const paths = getSelectedPaths();
    if (paths.length === 0) {
      showMsg("selOut", "Select at least one file from results.", "warning");
      return;
    }

    const root_for_arcname = document.getElementById("selRoot").value.trim() || null;
    const hash_detect = document.getElementById("selHash").checked;
    const notes = document.getElementById("selNotes").value.trim() || "Backup from selected items";

    showMsg("selOut", "Creating ZIP backup for selected items...", "info");
    const data = await postJSON("/api/backup_selection", { paths, root_for_arcname, hash_detect, notes });

    showMsg("selOut", `Backup created successfully. Backup ID: ${data.backup_id}`, "success");
    await loadBackups();
  } catch (e) {
    showMsg("selOut", e.message, "danger");
  }
}

/* -----------------------------
   Core actions
--------------------------------*/
async function scan() {
  try {
    showMsg("scanOut", "Scanning... please wait", "info");
    const root = document.getElementById("scanRoot").value.trim();
    const compute_hash = document.getElementById("scanHash").checked;
    
    const data = await postJSON("/api/scan", {root, compute_hash});
    
    // 1. Clear UI tables so old results disappear
    const searchBody = document.querySelector("#resultsTable tbody");
    if (searchBody) searchBody.innerHTML = "";
    
    const badge = document.getElementById("resultCount");
    if (badge) badge.textContent = "0";

    // 2. Refresh history tables (now they will be empty)
    await loadBackups();
    await loadRestores();

    // ✅ 3. UPDATE THE BACKUP PATH AUTOMATICALLY
    // This finds the "Root for Arcname" box and fills it with the path you just scanned
    const selRoot = document.getElementById("selRoot");
    if (selRoot) {
        selRoot.value = root; 
    }

    showMsg("scanOut", `Scan complete. Indexed ${data.indexed} files.`, "success");

  } catch (e) {
    showMsg("scanOut", e.message, "danger");
  }
}
function clearSearch() {
  document.getElementById("qName").value = "";
  document.getElementById("qExt").value = "";
  document.getElementById("qMin").value = "";
  document.getElementById("qMax").value = "";
  document.getElementById("qFrom").value = "";
  document.getElementById("qTo").value = "";
  document.getElementById("qSort").value = "name";
  document.getElementById("qDesc").checked = false;
  document.getElementById("qLimit").value = 50;
  showMsg("searchOut", "Cleared search filters.", "secondary");
}

async function search() {
  try {
    showMsg("searchOut", "Searching...", "info");

    const name_like = document.getElementById("qName").value.trim() || null;
    const extension = document.getElementById("qExt").value.trim() || null;

    const size_min = document.getElementById("qMin").value;
    const size_max = document.getElementById("qMax").value;

    const date_from_ts = dateToTs(document.getElementById("qFrom").value, false);
    const date_to_ts = dateToTs(document.getElementById("qTo").value, true);

    const sort_by = document.getElementById("qSort").value;
    const descending = document.getElementById("qDesc").checked;
    const limit = parseInt(document.getElementById("qLimit").value || "50", 10);

    const payload = {
      name_like,
      extension,
      size_min: size_min === "" ? null : parseInt(size_min, 10),
      size_max: size_max === "" ? null : parseInt(size_max, 10),
      date_from_ts,
      date_to_ts,
      sort_by,
      descending,
      limit
    };

    const data = await postJSON("/api/search", payload);

    const tbody = document.querySelector("#resultsTable tbody");
    tbody.innerHTML = "";

    for (const r of data.results) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>
          <input class="form-check-input pickRow" type="checkbox" data-path="${escapeHtml(r.path)}">
        </td>
        <td class="fw-semibold">${escapeHtml(r.name)}</td>
        <td>${r.size_bytes}</td>
        <td>${escapeHtml(r.extension || "-")}</td>
        <td>${escapeHtml(tsToLocal(r.modified_ts))}</td>
        <td class="mono">${escapeHtml(r.path)}</td>
      `;

      const cb = tr.querySelector(".pickRow");
      cb.addEventListener("change", () => toggleRowHighlight(cb));

      tbody.appendChild(tr);
    }

    const badge = document.getElementById("resultCount");
    if (badge) badge.textContent = String(data.results.length);

    showMsg("searchOut", `Found ${data.results.length} result(s). Select files to backup.`, "success");
  } catch (e) {
    showMsg("searchOut", e.message, "danger");
  }
}

async function restore() {
  try {
    showMsg("restoreOut", "Restoring...", "info");

    const backup_id = parseInt(document.getElementById("rId").value, 10);
    const target_dir = document.getElementById("rTarget").value.trim();
    const overwrite_mode = document.getElementById("rMode").value;

    await postJSON("/api/restore", {backup_id, target_dir, overwrite_mode});
    showMsg("restoreOut", "Restore completed successfully.", "success");
    await loadRestores();
  } catch (e) {
    showMsg("restoreOut", e.message, "danger");
  }
}

async function loadBackups() {
  const res = await fetch("/api/backups");
  const data = await res.json();

  const tbody = document.querySelector("#backupsTable tbody");
  tbody.innerHTML = "";

  for (const b of data.backups || []) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="fw-semibold">${b.id}</td>
      <td>${escapeHtml(tsToLocal(b.created_ts))}</td>
      <td class="mono">${escapeHtml(b.source_path)}</td>
      <td class="small text-muted">${escapeHtml(b.file_list || "No files")}</td> <td>${b.incremental ? "yes" : "no"}</td>
      <td class="mono">${escapeHtml(b.zip_path)}</td>
      <td>${escapeHtml(b.notes || "")}</td>
    `;
    tbody.appendChild(tr);
  }
}

async function loadRestores() {
  const res = await fetch("/api/restores");
  const data = await res.json();

  const tbody = document.querySelector("#restoresTable tbody");
  tbody.innerHTML = "";

  for (const r of data.restores || []) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="fw-semibold">${r.id}</td>
      <td>${escapeHtml(tsToLocal(r.restored_ts))}</td>
      <td class="mono">${escapeHtml(r.target_dir)}</td>
      <td>${escapeHtml(r.overwrite_mode)}</td>
      <td>${escapeHtml(r.summary || "")}</td>
      <td class="mono">${escapeHtml(r.zip_path)}</td>
    `;
    tbody.appendChild(tr);
  }
}

window.addEventListener("load", async () => {
  setupAutocomplete();
  await loadBackups();
  await loadRestores();
});