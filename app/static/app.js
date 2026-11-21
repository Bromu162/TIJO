/* =============================================
   API CLIENT
   ============================================= */
const API = {
  async get(path) {
    const res = await fetch(path);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  },

  async post(path, body) {
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  },
};

/* =============================================
   TOAST UTILITY
   ============================================= */
let _toastTimer = null;

function showToast(message, type = "info") {
  const el = document.getElementById("toast");
  el.textContent = message;
  el.className = `toast toast--visible${type !== "info" ? ` toast--${type}` : ""}`;
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => {
    el.className = "toast";
  }, 3500);
}

/* =============================================
   HELPERS
   ============================================= */
function formatDateTime(iso) {
  if (!iso) return "—";
  const d = new Date(iso.endsWith("Z") ? iso : iso + "Z");
  return d.toLocaleString("pl-PL", { hour12: false });
}

function formatDuration(minutes) {
  if (minutes < 60) return `${Math.round(minutes)} min`;
  const h = Math.floor(minutes / 60);
  const m = Math.round(minutes % 60);
  return m ? `${h}h ${m}m` : `${h}h`;
}

function spotIcon(type) {
  const icons = { STANDARD: "🚗", VIP: "⭐", ELECTRIC: "⚡", DISABLED: "♿" };
  return icons[type] || "🅿";
}

function typeBadge(type) {
  return `<span class="badge badge--${type.toLowerCase()}">${type}</span>`;
}

/* =============================================
   GLOBAL STATE
   ============================================= */
const state = { spots: [], activeFilter: "ALL", currentTicketId: null };

/* =============================================
   STATS BAR
   ============================================= */
async function refreshStats() {
  try {
    const [occ, rev] = await Promise.all([
      API.get("/api/spots/stats"),
      API.get("/api/stats/revenue"),
    ]);
    document.getElementById("statTotal").textContent = occ.total_spots;
    document.getElementById("statFree").textContent = occ.free;
    document.getElementById("statOccupied").textContent = occ.occupied;
    document.getElementById("statRate").textContent = `${occ.occupancy_rate_percent}%`;
    document.getElementById("statRevenue").textContent = `${rev.total_revenue.toFixed(2)} PLN`;
  } catch (_) { /* non-critical */ }
}

/* =============================================
   SPOTS TAB
   ============================================= */
async function loadSpots() {
  try {
    state.spots = await API.get("/api/spots");
    renderSpots();
  } catch (e) {
    document.getElementById("spotGrid").innerHTML =
      `<div class="empty-state">Failed to load spots: ${e.message}</div>`;
  }
}

function renderSpots() {
  const grid = document.getElementById("spotGrid");
  const filter = state.activeFilter;

  const filtered = state.spots.filter((s) => {
    if (filter === "ALL") return true;
    if (filter === "FREE" || filter === "OCCUPIED") return s.status === filter;
    return s.spot_type === filter;
  });

  if (!filtered.length) {
    grid.innerHTML = `<div class="empty-state">No spots match the selected filter.</div>`;
    return;
  }

  grid.innerHTML = filtered
    .map(
      (s) => `
      <div class="spot-card spot-card--${s.status.toLowerCase()}" title="Floor ${s.floor}">
        <span class="spot-card__icon">${spotIcon(s.spot_type)}</span>
        <span class="spot-card__number">${s.spot_number}</span>
        <span class="spot-card__type">${s.spot_type}</span>
        <span class="spot-card__status">${s.status}</span>
        <span class="spot-card__floor">Floor ${s.floor}</span>
      </div>`
    )
    .join("");
}

function setupSpotFilters() {
  document.querySelectorAll(".filter-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-btn").forEach((b) =>
        b.classList.remove("filter-btn--active")
      );
      btn.classList.add("filter-btn--active");
      state.activeFilter = btn.dataset.filter;
      renderSpots();
    });
  });
}

/* =============================================
   ENTRY TAB
   ============================================= */
function setupEntryForm() {
  document.getElementById("entryForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const plate = document.getElementById("entryPlate").value.trim();
    const type = document.getElementById("entryType").value;
    const resultEl = document.getElementById("entryResult");

    try {
      const ticket = await API.post("/api/tickets/entry", {
        license_plate: plate,
        spot_type: type,
      });
      resultEl.className = "result-box result-box--success";
      resultEl.innerHTML = `
        <strong>✅ Entry registered!</strong><br>
        Ticket: <strong>${ticket.ticket_code}</strong><br>
        Plate: <strong>${ticket.license_plate}</strong><br>
        Spot: <strong>${ticket.spot?.spot_number ?? "—"}</strong> (${ticket.spot_type})<br>
        Entry time: ${formatDateTime(ticket.entry_time)}
      `;
      resultEl.hidden = false;
      e.target.reset();
      showToast(`Entry registered for ${plate}`, "success");
      await Promise.all([loadSpots(), refreshStats(), loadActiveTickets()]);
    } catch (err) {
      resultEl.className = "result-box result-box--error";
      resultEl.textContent = `❌ ${err.message}`;
      resultEl.hidden = false;
      showToast(err.message, "error");
    }
  });
}

/* =============================================
   EXIT TAB — ACTIVE TICKETS LIST
   ============================================= */
async function loadActiveTickets() {
  const container = document.getElementById("activeTicketsList");
  try {
    const tickets = await API.get("/api/tickets/active");
    if (!tickets.length) {
      container.innerHTML = `<div class="empty-state">No active parkings at the moment.</div>`;
      return;
    }
    container.innerHTML = tickets
      .map((t) => {
        const sinceMs = Date.now() - new Date(t.entry_time.endsWith("Z") ? t.entry_time : t.entry_time + "Z").getTime();
        const sinceMin = Math.round(sinceMs / 60000);
        return `
          <div class="ticket-row">
            <span class="ticket-row__plate">${t.license_plate}</span>
            <span class="ticket-row__info">${t.spot_type} · ${t.spot?.spot_number ?? "—"} · ${formatDuration(sinceMin)} ago</span>
            <button class="ticket-row__btn" data-id="${t.id}">Checkout →</button>
          </div>`;
      })
      .join("");

    container.querySelectorAll(".ticket-row__btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.getElementById("exitTicketId").value = btn.dataset.id;
        previewFee(parseInt(btn.dataset.id));
      });
    });
  } catch (e) {
    container.innerHTML = `<div class="empty-state">Failed to load active tickets.</div>`;
  }
}

/* =============================================
   EXIT TAB — FEE PREVIEW & PAYMENT
   ============================================= */
async function previewFee(ticketId) {
  const previewEl = document.getElementById("feePreview");
  const tableEl = document.getElementById("feeTable");
  const exitResultEl = document.getElementById("exitResult");
  exitResultEl.hidden = true;

  try {
    const data = await API.get(`/api/tickets/${ticketId}/calculate`);
    state.currentTicketId = ticketId;

    tableEl.innerHTML = `
      <tr><td>Plate</td><td><strong>${data.license_plate}</strong></td></tr>
      <tr><td>Spot type</td><td>${typeBadge(data.spot_type)}</td></tr>
      <tr><td>Entry time</td><td>${formatDateTime(data.entry_time)}</td></tr>
      <tr><td>Total duration</td><td>${formatDuration(data.total_duration_minutes)}</td></tr>
      <tr><td>Grace period</td><td>${data.grace_period_applied ? "✅ Applied (free)" : "❌ Not applied"}</td></tr>
      <tr><td>Charged hours</td><td>${data.charged_hours} h</td></tr>
      <tr><td>Hourly rate</td><td>${data.hourly_rate} PLN/h</td></tr>
      <tr><td>Daily cap</td><td>${data.daily_cap} PLN</td></tr>
      <tr class="fee-total"><td>Total fee</td><td>${parseFloat(data.estimated_fee).toFixed(2)} PLN</td></tr>
    `;

    previewEl.hidden = false;
  } catch (e) {
    showToast(e.message, "error");
  }
}

function setupExitForm() {
  document.getElementById("exitSearchForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = parseInt(document.getElementById("exitTicketId").value);
    if (!id) return;
    await previewFee(id);
  });

  document.getElementById("payForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!state.currentTicketId) return;
    const method = document.getElementById("paymentMethod").value;
    const resultEl = document.getElementById("exitResult");

    try {
      const receipt = await API.post(`/api/tickets/${state.currentTicketId}/pay`, {
        payment_method: method,
      });
      resultEl.className = "result-box result-box--success";
      resultEl.innerHTML = `
        <strong>✅ Checkout complete!</strong><br>
        Ticket: <strong>${receipt.ticket_code}</strong><br>
        Plate: <strong>${receipt.license_plate}</strong><br>
        Exit time: ${formatDateTime(receipt.exit_time)}<br>
        Amount paid: <strong>${receipt.total_amount.toFixed(2)} PLN</strong> via ${receipt.payment?.payment_method ?? "N/A"}
      `;
      resultEl.hidden = false;
      document.getElementById("feePreview").hidden = true;
      document.getElementById("exitTicketId").value = "";
      state.currentTicketId = null;
      showToast(`Checkout complete — ${receipt.total_amount.toFixed(2)} PLN paid`, "success");
      await Promise.all([loadSpots(), refreshStats(), loadActiveTickets(), loadHistory()]);
    } catch (err) {
      resultEl.className = "result-box result-box--error";
      resultEl.textContent = `❌ ${err.message}`;
      resultEl.hidden = false;
      showToast(err.message, "error");
    }
  });
}

/* =============================================
   HISTORY TAB
   ============================================= */
async function loadHistory() {
  const tbody = document.getElementById("historyBody");
  try {
    const tickets = await API.get("/api/tickets/history?limit=50");
    if (!tickets.length) {
      tbody.innerHTML = `<tr><td colspan="8" class="empty-state">No completed parkings yet.</td></tr>`;
      return;
    }
    tbody.innerHTML = tickets
      .map((t) => {
        const durationMin =
          t.entry_time && t.exit_time
            ? Math.round(
                (new Date(t.exit_time.endsWith("Z") ? t.exit_time : t.exit_time + "Z") -
                  new Date(t.entry_time.endsWith("Z") ? t.entry_time : t.entry_time + "Z")) /
                  60000
              )
            : null;
        return `<tr>
          <td>${t.ticket_code}</td>
          <td><strong>${t.license_plate}</strong></td>
          <td>${typeBadge(t.spot_type)}</td>
          <td>${formatDateTime(t.entry_time)}</td>
          <td>${formatDateTime(t.exit_time)}</td>
          <td>${durationMin !== null ? formatDuration(durationMin) : "—"}</td>
          <td>${t.total_amount !== null ? `${parseFloat(t.total_amount).toFixed(2)} PLN` : "—"}</td>
          <td><span class="badge badge--${t.status.toLowerCase()}">${t.status}</span></td>
        </tr>`;
      })
      .join("");
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="8" class="empty-state">Failed to load history.</td></tr>`;
  }
}

document.getElementById("refreshHistory").addEventListener("click", loadHistory);

/* =============================================
   PRICING TAB
   ============================================= */
async function loadPricing() {
  const container = document.getElementById("pricingInfo");
  try {
    const data = await API.get("/api/pricing");
    const icons = { STANDARD: "🚗", VIP: "⭐", ELECTRIC: "⚡", DISABLED: "♿" };
    container.innerHTML = `
      <div class="pricing-grid">
        ${data.rates
          .map(
            (r) => `
          <div class="pricing-card">
            <div class="pricing-card__icon">${icons[r.spot_type] ?? "🅿"}</div>
            <div class="pricing-card__type">${r.spot_type}</div>
            <div class="pricing-card__rate">${parseFloat(r.hourly_rate).toFixed(2)} PLN/h</div>
            <div class="pricing-card__cap">Daily cap: ${parseFloat(r.daily_cap).toFixed(2)} PLN</div>
          </div>`
          )
          .join("")}
      </div>
      <div class="pricing-note">
        ⏱ First <strong>${data.grace_period_minutes} minutes are free</strong>. 
        Billing unit: <strong>${data.billing_unit}</strong>.
      </div>
    `;
  } catch (e) {
    container.innerHTML = `<div class="empty-state">Failed to load pricing info.</div>`;
  }
}

/* =============================================
   TAB NAVIGATION
   ============================================= */
function setupTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  const sections = document.querySelectorAll(".tab-content");

  tabs.forEach((btn) => {
    btn.addEventListener("click", async () => {
      tabs.forEach((t) => t.classList.remove("tab-btn--active"));
      sections.forEach((s) => s.classList.remove("tab-content--active"));
      btn.classList.add("tab-btn--active");
      const target = document.getElementById(`tab-${btn.dataset.tab}`);
      if (target) target.classList.add("tab-content--active");

      if (btn.dataset.tab === "exit") await loadActiveTickets();
      if (btn.dataset.tab === "history") await loadHistory();
      if (btn.dataset.tab === "pricing") await loadPricing();
    });
  });
}

/* =============================================
   BOOT
   ============================================= */
async function init() {
  setupTabs();
  setupSpotFilters();
  setupEntryForm();
  setupExitForm();

  await Promise.all([loadSpots(), refreshStats()]);

  // Refresh stats every 60 seconds
  setInterval(async () => {
    await Promise.all([loadSpots(), refreshStats()]);
  }, 60_000);
}

init();
