// ── Config ────────────────────────────────────
const API_BASE = "";      // ← เพิ่ม: relative URL ใช้ได้เสมอไม่ว่า ngrok จะเปลี่ยน
let MERCHANT_ID = "";
let LIFF_ID = "";

// ENTRY POINT — listener เดียว, รอ config ก่อน loadProducts()
window.addEventListener("DOMContentLoaded", async () => {
  const cfg = await fetch("/api/v1/config").then(r => r.json());
  MERCHANT_ID = cfg.merchant_id;
  LIFF_ID     = cfg.liff_id;
  loadProducts();   // ← เรียกครั้งเดียวหลังได้ MERCHANT_ID จริง
});



// ── State 
let products  = [];
let cart      = [];   // [{ id, name, price, cost, quantity }]
let salesChart = null;
let allTx      = [];
 

// PAGE NAVIGATION

function showPage(name) {
  document.querySelectorAll(".page").forEach(p => p.classList.add("hidden"));
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  document.getElementById("page-" + name).classList.remove("hidden");
  document.getElementById("nav-" + name).classList.add("active");
  if (name === "pos")      loadProducts();
  if (name === "products") loadProductTable();
  if (name === "report")   loadReport();
}
 

// PRODUCTS — POS GRID

async function loadProducts() {
  try {
    const res  = await fetch(`${API_BASE}/api/v1/product/list/${MERCHANT_ID}`);
    products   = await res.json();
    renderGrid(products);
  } catch (e) {
    console.error("loadProducts:", e);
  }
}
 
function renderGrid(list) {
  const grid = document.getElementById("product-grid");
  if (!list.length) {
    grid.innerHTML = `<div class="col-12 text-center text-muted py-5">ยังไม่มีสินค้า — กดเพิ่มสินค้าที่เมนู "คลังสินค้า"</div>`;
    return;
  }
  grid.innerHTML = list.map(p => `
    <div class="col-6 col-md-4 col-xl-3">
      <div class="product-card" onclick="addToCart('${p.id}','${escAttr(p.name)}',${p.price},${p.cost_price||0})">
        <div class="product-img">
          ${p.image_url
            ? `<img src="${escHtml(p.image_url)}" alt="${escHtml(p.name)}" loading="lazy">`
            : `<i class="fa-solid fa-box" style="font-size:2.5rem;color:#cbd5e1"></i>`}
        </div>
        <div class="product-info">
          <div class="product-name">${escHtml(p.name)}</div>
          <div class="product-price">฿${fmt(p.price)}</div>
        </div>
      </div>
    </div>`).join("");
}
 
function searchProduct(q) {
  const filtered = products.filter(p => p.name.toLowerCase().includes(q.toLowerCase()));
  renderGrid(filtered);
}
 

// CART

function addToCart(id, name, price, cost) {
  const existing = cart.find(c => c.id === id);
  if (existing) {
    existing.quantity++;
  } else {
    cart.push({ id, name, price, cost, quantity: 1 });
  }
  renderCart();
}
 
function removeFromCart(id) {
  cart = cart.filter(c => c.id !== id);
  renderCart();
}
 
function clearCart() {
  cart = [];
  renderCart();
}
 
function renderCart() {
  const body  = document.getElementById("cart-body");
  const total = cart.reduce((s, c) => s + c.price * c.quantity, 0);
 
  document.getElementById("cart-count").textContent = cart.reduce((s, c) => s + c.quantity, 0);
  document.getElementById("cart-total").textContent = "฿ " + fmt(total);
 
  if (!cart.length) {
    body.innerHTML = `<div class="cart-empty"><i class="fa-solid fa-cart-shopping"></i><p>ยังไม่มีสินค้า</p></div>`;
    return;
  }
 
  body.innerHTML = cart.map(c => `
    <div class="cart-item">
      <div>
        <div class="cart-item-name">${escHtml(c.name)}</div>
        <div class="cart-item-sub">฿${fmt(c.price)} × ${c.quantity}</div>
        <span class="cart-item-rm" onclick="removeFromCart('${c.id}')">ลบออก</span>
      </div>
      <div class="cart-item-amt">฿${fmt(c.price * c.quantity)}</div>
    </div>`).join("");
}
 

// CHECKOUT — สร้าง QR

async function checkout() {
  if (!cart.length) return alert("กรุณาเพิ่มสินค้าก่อนชำระเงิน");
 
  const total = cart.reduce((s, c) => s + c.price * c.quantity, 0);
  const body  = {
    merchant_id:  MERCHANT_ID,
    total_amount: total,
    discount: 0,
    items: cart.map(c => ({
      product_id: c.id,
      name: c.name,
      price: c.price,
      cost: c.cost,
      quantity: c.quantity
    }))
  };
 
  try {
    const res  = await fetch(`${API_BASE}/api/v1/qr/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    if (data.status !== "ok") throw new Error(data.detail || "error");
 
    // สร้าง QR URL สำหรับ LIFF scan
    const liffUrl = `${window.location.origin}/liff?qr_id=${data.qr_id}`;
    const qrApi   = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(liffUrl)}`;
 
    document.getElementById("qr-img").src    = qrApi;
    document.getElementById("qr-amount").textContent = "฿ " + fmt(total);
 
    new bootstrap.Modal(document.getElementById("qrModal")).show();
  } catch (e) {
    alert("เกิดข้อผิดพลาด: " + e.message);
  }
}
 

// PRODUCT MANAGEMENT — คลังสินค้า

async function loadProductTable() {
  try {
    const res   = await fetch(`${API_BASE}/api/v1/product/list/${MERCHANT_ID}`);
    const prods = await res.json();
    const tbody = document.getElementById("product-table-body");
    tbody.innerHTML = prods.map(p => {
      const margin = p.cost_price > 0
        ? (((p.price - p.cost_price) / p.price) * 100).toFixed(1)
        : "—";
      return `<tr>
        <td>${p.image_url ? `<img src="${escHtml(p.image_url)}" style="width:42px;height:42px;object-fit:cover;border-radius:8px">` : "—"}</td>
        <td><strong>${escHtml(p.name)}</strong></td>
        <td>฿${fmt(p.price)}</td>
        <td>฿${fmt(p.cost_price || 0)}</td>
        <td><span class="badge bg-success bg-opacity-10 text-success fw-semibold">${margin}%</span></td>
        <td>
          <button class="btn btn-sm btn-outline-danger" onclick="deleteProduct('${p.id}')">
            <i class="fa-solid fa-trash-can"></i>
          </button>
        </td>
      </tr>`;
    }).join("");
  } catch (e) {
    console.error("loadProductTable:", e);
  }
}
 
function openAddModal() {
  document.getElementById("new-name").value  = "";
  document.getElementById("new-price").value = "";
  document.getElementById("new-cost").value  = "";
  document.getElementById("uploaded-url").value = "";
  document.getElementById("img-preview").classList.add("hidden");
  document.getElementById("img-preview").src = "";
  document.getElementById("upload-status").classList.add("hidden");
  new bootstrap.Modal(document.getElementById("addProductModal")).show();
}
 
async function saveProduct() {
  const name  = document.getElementById("new-name").value.trim();
  const price = parseFloat(document.getElementById("new-price").value.replace(/,/g, "")) || 0;
  const cost  = parseFloat(document.getElementById("new-cost").value.replace(/,/g, "")) || 0;
  const url   = document.getElementById("uploaded-url").value;
 
  if (!name)  return alert("กรุณาใส่ชื่อสินค้า");
  if (!price) return alert("กรุณาใส่ราคาขาย");
 
  const btn = document.getElementById("btn-save");
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> กำลังบันทึก...';
 
  try {
    const res = await fetch(`${API_BASE}/api/v1/product/add`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ merchant_id: MERCHANT_ID, name, price, cost_price: cost, image_url: url })
    });
    const data = await res.json();
    if (data.status !== "ok") throw new Error(data.detail || "error");
 
    bootstrap.Modal.getInstance(document.getElementById("addProductModal")).hide();
    loadProductTable();
    loadProducts();
  } catch (e) {
    alert("บันทึกไม่สำเร็จ: " + e.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-check"></i> บันทึก';
  }
}
 
async function deleteProduct(id) {
  if (!confirm("ลบสินค้านี้ออกจากระบบ?")) return;
  await fetch(`${API_BASE}/api/v1/product/delete/${id}`, { method: "DELETE" });
  loadProductTable();
  loadProducts();
}
 
// ── อัปโหลดรูปสินค้า 
async function handleUpload(input) {
  if (!input.files[0]) return;
  const status = document.getElementById("upload-status");
  const preview = document.getElementById("img-preview");
  status.classList.remove("hidden");
  preview.classList.add("hidden");
 
  const form = new FormData();
  form.append("file", input.files[0]);
 
  try {
    const res  = await fetch(`${API_BASE}/api/v1/upload/`, { method: "POST", body: form });
    const data = await res.json();
    if (data.status !== "ok") throw new Error(data.detail);
    document.getElementById("uploaded-url").value = data.url;
    preview.src = data.url;
    preview.classList.remove("hidden");
  } catch (e) {
    alert("อัปโหลดไม่สำเร็จ: " + e.message);
  } finally {
    status.classList.add("hidden");
  }
}
 
// ── Format ตัวเลขขณะพิมพ์
function fmtNum(input) {
  const raw = input.value.replace(/[^0-9.]/g, "");
  input.value = raw;
}
 

// REPORT & ANALYTICS

async function loadReport() {
  try {
    const [summary, txRes] = await Promise.all([
      fetch(`${API_BASE}/api/v1/analytics/summary/${MERCHANT_ID}`).then(r => r.json()),
      fetch(`${API_BASE}/api/v1/analytics/transactions/${MERCHANT_ID}`).then(r => r.json())
    ]);
    allTx = txRes;
    renderStatCards(summary);
    renderTopTables(txRes);
    renderTxTable(txRes);
    buildChart(txRes, "daily");
  } catch (e) {
    console.error("loadReport:", e);
  }
}
 
function renderStatCards(s) {
  document.getElementById("stat-revenue").textContent = "฿" + fmt(s.total_revenue || 0);
  document.getElementById("stat-orders").textContent  = (s.total_orders  || 0).toLocaleString();
  document.getElementById("stat-members").textContent = (s.member_orders || 0).toLocaleString();
  document.getElementById("stat-walkin").textContent  = (s.walkin_orders || 0).toLocaleString();
}
 
function buildChart(txList, mode) {
  const ctx = document.getElementById("salesChart").getContext("2d");
  if (salesChart) salesChart.destroy();
 
  const grouped = {};
  txList.forEach(tx => {
    const d = new Date(tx.created_at);
    const key = mode === "daily"
      ? d.toLocaleDateString("th-TH", { day: "2-digit", month: "short" })
      : d.toLocaleDateString("th-TH", { month: "short", year: "2-digit" });
    grouped[key] = (grouped[key] || 0) + parseFloat(tx.amount || 0);
  });
 
  const labels = Object.keys(grouped).slice(-14).reverse();
  const data   = labels.map(k => grouped[k]);
 
  salesChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "รายได้ (฿)",
        data,
        backgroundColor: "rgba(79,110,247,0.18)",
        borderColor: "rgba(79,110,247,0.9)",
        borderWidth: 2,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, ticks: { callback: v => "฿" + v.toLocaleString() } },
        x: { grid: { display: false } }
      }
    }
  });
}
 
function switchChart(mode) {
  document.getElementById("btn-daily").classList.toggle("active",   mode === "daily");
  document.getElementById("btn-monthly").classList.toggle("active", mode === "monthly");
  buildChart(allTx, mode);
}
 
function renderTopTables(txList) {
  // Top customers
  const custMap = {};
  txList.forEach(tx => {
    if (tx.customer_name) {
      custMap[tx.customer_name] = custMap[tx.customer_name] || { name: tx.customer_name, pic: tx.customer_picture, total: 0 };
      custMap[tx.customer_name].total += parseFloat(tx.amount || 0);
    }
  });
  const topCust = Object.values(custMap).sort((a, b) => b.total - a.total).slice(0, 5);
  const maxC    = topCust[0]?.total || 1;
 
  document.querySelector("#top-customers-table tbody").innerHTML = topCust.length
    ? topCust.map((c, i) => `
        <tr>
          <td><div class="rank-num ${["gold","silver","bronze"][i]||""}">${i+1}</div></td>
          <td>
            ${c.pic ? `<img src="${escHtml(c.pic)}" class="rank-avatar me-2">` : ""}
            <span class="fw-semibold">${escHtml(c.name)}</span>
            <div class="mini-bar"><div class="mini-fill" style="width:${(c.total/maxC*100).toFixed(1)}%"></div></div>
          </td>
          <td class="text-end fw-bold">฿${fmt(c.total)}</td>
        </tr>`).join("")
    : `<tr><td colspan="3" class="empty-row">ยังไม่มีข้อมูลสมาชิก</td></tr>`;
 
  // Top products
  const prodMap = {};
  txList.forEach(tx => {
    (tx.transaction_items || []).forEach(item => {
      const name = item.products?.name || item.product_id;
      prodMap[name] = (prodMap[name] || 0) + (item.quantity || 1);
    });
  });
  const topProd = Object.entries(prodMap).sort((a, b) => b[1] - a[1]).slice(0, 5);
  const maxP    = topProd[0]?.[1] || 1;
 
  document.querySelector("#top-products-table tbody").innerHTML = topProd.length
    ? topProd.map(([name, qty], i) => `
        <tr>
          <td><div class="rank-num ${["gold","silver","bronze"][i]||""}">${i+1}</div></td>
          <td>
            <span class="fw-semibold">${escHtml(name)}</span>
            <div class="mini-bar"><div class="mini-fill g" style="width:${(qty/maxP*100).toFixed(1)}%"></div></div>
          </td>
          <td class="text-end fw-bold">${qty} ชิ้น</td>
        </tr>`).join("")
    : `<tr><td colspan="2" class="empty-row">ยังไม่มีข้อมูล</td></tr>`;
}
 
function renderTxTable(txList) {
  const tbody = document.getElementById("report-table-body");
  tbody.innerHTML = txList.slice(0, 50).map(tx => `
    <tr>
      <td>${new Date(tx.created_at).toLocaleString("th-TH", {dateStyle:"short",timeStyle:"short"})}</td>
      <td>
        <div class="member-row">
          ${tx.customer_picture ? `<img src="${escHtml(tx.customer_picture)}" class="rank-avatar">` : ""}
          <div>
            <div class="member-name">${escHtml(tx.customer_name || "ขาจร")}</div>
            ${tx.customer_name ? `<div class="member-tag">LINE Member</div>` : ""}
          </div>
        </div>
      </td>
      <td>${(tx.transaction_items||[]).map(i => `${i.products?.name||"?"} ×${i.quantity}`).join(", ") || "—"}</td>
      <td class="fw-bold">฿${fmt(tx.amount)}</td>
      <td><span class="badge-${tx.status}">${tx.status === "claimed" ? "✅ claimed" : "⏳ pending"}</span></td>
    </tr>`).join("") || `<tr><td colspan="5" class="empty-row">ยังไม่มีรายการขาย</td></tr>`;
}
 

// UTILITIES

function fmt(n) {
  return parseFloat(n || 0).toLocaleString("th-TH", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function escHtml(str) {
  return String(str).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}
function escAttr(str) {
  return String(str)
    .replace(/&/g,"&amp;").replace(/</g,"&lt;")
    .replace(/>/g,"&gt;").replace(/"/g,"&quot;")
    .replace(/'/g,"&#x27;");
}
 
