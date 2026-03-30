// ── Config ────────────────────────────────────
const API_BASE = "";
let MERCHANT_ID = "";
let LIFF_ID = "";

// ENTRY POINT

document.addEventListener("DOMContentLoaded", async () => {
    try {
        // 1. ดึง config จาก backend ก่อน — ต้องได้ LIFF_ID จริงก่อนเรียก liff.init()
        const cfg = await fetch("/api/v1/config").then(r => r.json());
        MERCHANT_ID = cfg.merchant_id;
        LIFF_ID     = cfg.liff_id;

        // 2. init LIFF หลังได้ ID จริง
        await liff.init({ liffId: LIFF_ID });

        if (!liff.isLoggedIn()) {
            liff.login();
            return;
        }

        const profile = await liff.getProfile();
        const params  = new URLSearchParams(window.location.search);
        const qrId    = params.get("qr_id");

        if (qrId) {
            await showClaimScreen(profile, qrId);
        } else {
            await showProfileScreen(profile);
        }

    } catch (err) {
        showError(err.message || "กรุณาเปิดใน LINE app");
    }
});

// ══════════════════════════════════════════════
// SCREEN: CLAIM POINTS (สแกน QR)
// ══════════════════════════════════════════════
let _currentProfile = null;
let _currentQrId = null;
let _claimAmount = 0;

async function showClaimScreen(profile, qrId) {
    _currentProfile = profile;
    _currentQrId = qrId;

    // โหลดข้อมูลบิลก่อนแสดง
    try {
        const res = await fetch(`${API_BASE}/api/v1/qr/info/${qrId}`).catch(() => null);

        // แสดงรูป + ชื่อ LINE
        const avatarEl = document.getElementById("claim-avatar");
        if (profile.pictureUrl) {
            avatarEl.innerHTML = `<img src="${esc(profile.pictureUrl)}" alt="avatar">`;
        }
        document.getElementById("claim-name").textContent = `สวัสดี คุณ${profile.displayName}!`;

        // ถ้า API มี /qr/info ก็ใช้ ถ้าไม่มีก็แสดงแค่ปุ่ม claim
        if (res && res.ok) {
            const data = await res.json();
            _claimAmount = data.amount || 0;
            document.getElementById("claim-amount").textContent = "฿ " + fmt(_claimAmount);
            document.getElementById("claim-receipt").textContent = "เลขที่: " + (data.receipt_id || qrId.slice(0, 8).toUpperCase());
        } else {
            document.getElementById("claim-amount").textContent = "฿ —";
            document.getElementById("claim-receipt").textContent = "QR: " + qrId.slice(0, 8).toUpperCase();
        }

        switchScreen("claim");

    } catch (e) {
        showError(e.message);
    }
}

async function claimPoints() {
    if (!_currentProfile || !_currentQrId) return;

    const btn = document.getElementById("btn-claim");
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> กำลังสะสม...';

    try {
        const res = await fetch(`${API_BASE}/api/v1/qr/claim`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                line_user_id: _currentProfile.userId,
                qr_id: _currentQrId,
                display_name: _currentProfile.displayName,
                picture_url: _currentProfile.pictureUrl || ""
            })
        });
        const data = await res.json();

        if (data.status !== "success") {
            throw new Error(data.message || "ไม่สามารถสะสมแต้มได้");
        }

        // โหลดสถิติสมาชิก
        const summary = await fetchMemberSummary(_currentProfile.userId);
        showSuccessScreen(_currentProfile, data.amount, summary);

    } catch (e) {
        alert(e.message);
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-star"></i> สะสมแต้มเลย!';
    }
}

// ══════════════════════════════════════════════
// SCREEN: SUCCESS
// ══════════════════════════════════════════════
function showSuccessScreen(profile, amount, summary) {
    document.getElementById("success-name").textContent =
        "ขอบคุณคุณ " + profile.displayName + " ครับ!";

    const points = Math.floor((summary.total_spent || 0) / 100);
    document.getElementById("success-points").textContent = "+" + Math.floor(amount / 100) + " แต้ม";
    document.getElementById("success-total-spent").textContent = "฿" + fmt(summary.total_spent || 0);
    document.getElementById("success-tx-count").textContent = (summary.tx_count || 0).toLocaleString();

    // ประวัติ
    const historyEl = document.getElementById("history-list");
    const txList = summary.recent_transactions || [];
    if (txList.length) {
        historyEl.innerHTML = txList.slice(0, 5).map(tx => `
      <div class="history-item">
        <div>
          <div>${tx.receipt_id || "—"}</div>
          <div class="history-date">${new Date(tx.created_at).toLocaleDateString("th-TH", { dateStyle: "medium" })}</div>
        </div>
        <div class="history-amt">฿${fmt(tx.amount)}</div>
      </div>`).join("");
    } else {
        historyEl.innerHTML = `<div class="history-empty">ยังไม่มีประวัติ</div>`;
    }

    switchScreen("success");
}

// ══════════════════════════════════════════════
// SCREEN: PROFILE (เปิดผ่าน Rich Menu)
// ══════════════════════════════════════════════
async function showProfileScreen(profile) {
    // รูปโปรไฟล์
    const avatarEl = document.getElementById("profile-avatar-img");
    if (profile.pictureUrl) {
        avatarEl.innerHTML = `<img src="${esc(profile.pictureUrl)}" alt="avatar">`;
    } else {
        avatarEl.style.display = "flex";
        avatarEl.style.alignItems = "center";
        avatarEl.style.justifyContent = "center";
        avatarEl.innerHTML = `<i class="fa-solid fa-user" style="font-size:2.5rem;color:white"></i>`;
    }
    document.getElementById("profile-name").textContent = profile.displayName;

    try {
        const summary = await fetchMemberSummary(profile.userId);
        const points = Math.floor((summary.total_spent || 0) / 100);

        document.getElementById("profile-total-spent").textContent = "฿" + fmt(summary.total_spent || 0);
        document.getElementById("profile-points").textContent = points.toLocaleString();
        document.getElementById("profile-tx-count").textContent = (summary.tx_count || 0).toLocaleString();

        // ประวัติ
        const histEl = document.getElementById("profile-history-list");
        const txList = summary.recent_transactions || [];
        if (txList.length) {
            histEl.innerHTML = txList.slice(0, 8).map(tx => `
        <div class="history-item">
          <div>
            <div>${tx.receipt_id || "—"}</div>
            <div class="history-date">${new Date(tx.created_at).toLocaleDateString("th-TH", { dateStyle: "medium" })}</div>
          </div>
          <div class="history-amt">฿${fmt(tx.amount)}</div>
        </div>`).join("");
        } else {
            histEl.innerHTML = `<div class="history-empty">ยังไม่มีประวัติการซื้อ</div>`;
        }
    } catch (e) {
        console.error("profile summary:", e);
    }

    switchScreen("profile");
}

// ══════════════════════════════════════════════
// HELPERS
// ══════════════════════════════════════════════
async function fetchMemberSummary(lineUserId) {
    try {
        const res = await fetch(
            `${API_BASE}/api/v1/analytics/member-summary/${lineUserId}?merchant_id=${MERCHANT_ID}`
        );
        return await res.json();
    } catch {
        return { total_spent: 0, tx_count: 0, recent_transactions: [] };
    }
}

function switchScreen(name) {
    document.querySelectorAll(".screen").forEach(s => s.classList.add("hidden"));
    document.getElementById("screen-" + name).classList.remove("hidden");
}

function showError(msg) {
    document.getElementById("error-msg").textContent = msg || "เกิดข้อผิดพลาด";
    switchScreen("error");
}

function closeLiff() {
    if (liff.isInClient()) {
        liff.closeWindow();
    } else {
        window.close();
    }
}

function fmt(n) {
    return parseFloat(n || 0).toLocaleString("th-TH", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function esc(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}
