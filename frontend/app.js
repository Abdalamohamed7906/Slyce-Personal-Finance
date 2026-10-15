// Slyce frontend: plain JS talking to the FastAPI backend.
const $ = (id) => document.getElementById(id);
let token = localStorage.getItem("token");

// ---------- helpers ----------
async function api(path, { method = "GET", body, form } = {}) {
  const headers = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  let payload;
  if (form) payload = new URLSearchParams(form);
  else if (body) { headers["Content-Type"] = "application/json"; payload = JSON.stringify(body); }

  const res = await fetch(path, { method, headers, body: payload });
  if (res.status === 401 && token) { logout(); throw new Error("Session expired, log in again"); }
  if (res.status === 204) return null;
  const data = await res.json();
  if (!res.ok) {
    const d = data.detail;
    throw new Error(Array.isArray(d) ? d.map((e) => e.msg).join(", ") : d);
  }
  return data;
}
const money = (n) => "£" + Number(n).toFixed(2);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

function showApp(loggedIn) {
  $("auth-section").hidden = loggedIn;
  $("app-section").hidden = !loggedIn;
  $("logout").hidden = !loggedIn;
  if (loggedIn) loadHistory();
}
function logout() { token = null; localStorage.removeItem("token"); showApp(false); }

// ---------- auth ----------
$("auth-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const action = e.submitter.dataset.action;
  const email = $("email").value, password = $("password").value;
  $("auth-msg").textContent = "";
  try {
    if (action === "register") await api("/auth/register", { method: "POST", body: { email, password } });
    const t = await api("/auth/login", { method: "POST", form: { username: email, password } });
    token = t.access_token;
    localStorage.setItem("token", token);
    showApp(true);
  } catch (err) { $("auth-msg").textContent = err.message; }
});
$("logout").addEventListener("click", logout);

// ---------- paychecks ----------
$("paid-on").valueAsDate = new Date();
$("paycheck-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    const p = await api("/paychecks", {
      method: "POST",
      body: { amount: $("amount").value, paid_on: $("paid-on").value },
    });
    $("split-result").innerHTML = `
      <div class="bars">
        <div class="bar needs">Needs<b>${money(p.needs)}</b></div>
        <div class="bar wants">Wants<b>${money(p.wants)}</b></div>
        <div class="bar savings">Savings<b>${money(p.savings)}</b></div>
      </div>
      ${p.tip ? `<div class="tip">💡 ${esc(p.tip)}</div>` : ""}`;
    loadHistory();
  } catch (err) { $("split-result").textContent = err.message; }
});

async function loadHistory() {
  const rows = await api("/paychecks");
  $("history").innerHTML = rows.length
    ? rows.map((p) => `
      <tr><td>${p.paid_on}</td><td>${money(p.amount)}</td><td>${money(p.needs)}</td>
      <td>${money(p.wants)}</td><td>${money(p.savings)}</td>
      <td><button class="link" data-id="${p.id}">Delete</button></td></tr>`).join("")
    : `<tr><td colspan="6">No paychecks yet.</td></tr>`;
}
$("history").addEventListener("click", async (e) => {
  const id = e.target.dataset.id;
  if (id && confirm("Delete this paycheck?")) {
    await api(`/paychecks/${id}`, { method: "DELETE" });
    loadHistory();
  }
});

// ---------- savings tracker ----------
$("savings-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const params = new URLSearchParams({ annual_rate: ($("rate").value || 0) / 100 });
  if ($("since").value) params.set("since", $("since").value);
  if ($("actual").value) params.set("actual", $("actual").value);
  try {
    const r = await api(`/savings/target?${params}`);
    $("savings-result").innerHTML = `
      <p>From <b>${r.paychecks_counted}</b> paychecks you should have saved
      <b>${money(r.target_savings)}</b>${r.annual_rate ? ` (<b>${money(r.target_with_interest)}</b> with interest)` : ""}.</p>
      <div class="tip">${esc(r.commentary)}</div>`;
  } catch (err) { $("savings-result").textContent = err.message; }
});

// ---------- stock explorer ----------
$("stock-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    const items = await api(`/stocks/instruments?q=${encodeURIComponent($("stock-q").value)}&limit=20`);
    $("stock-list").innerHTML = items.length
      ? items.map((i) => `<li data-ticker="${esc(i.ticker)}">${esc(i.name)} · ${esc(i.ticker)} (${esc(i.type)})</li>`).join("")
      : "<li>No matches.</li>";
  } catch (err) { $("stock-list").textContent = err.message; }
});
$("stock-list").addEventListener("click", async (e) => {
  const ticker = e.target.dataset.ticker;
  if (!ticker) return;
  $("stock-detail").textContent = "Loading…";
  try {
    const s = await api(`/stocks/${encodeURIComponent(ticker)}/summary?period=${$("period").value}`);
    const g = s.growth_pct == null ? "price data unavailable"
      : `<span class="${s.growth_pct >= 0 ? "up" : "down"}">${s.growth_pct >= 0 ? "+" : ""}${s.growth_pct}%</span> over ${s.period}`;
    $("stock-detail").innerHTML = `
      <h3>${esc(s.name || s.ticker)}</h3><p>${g}</p><p>${esc(s.summary)}</p>
      <p class="disclaimer">${esc(s.disclaimer)}</p>`;
  } catch (err) { $("stock-detail").textContent = err.message; }
});

showApp(!!token);
