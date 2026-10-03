let currentTab = "orders";
let authHeader = null;

const STATUS_MAP = {
    "PENDING_PAYMENT": { fa: "در انتظار پرداخت", next: "CONFIRMED", nextFa: "تایید سفارش" },
    "CONFIRMED": { fa: "تایید شده", next: "ARRANGING", nextFa: "شروع گلآرایی" },
    "ARRANGING": { fa: "در حال گلآرایی", next: "QUALITY_APPROVED", nextFa: "تایید کیفیت و عکاسی" },
    "QUALITY_APPROVED": { fa: "تایید کیفی", next: "OUT_FOR_DELIVERY", nextFa: "تحویل به سفیر" },
    "OUT_FOR_DELIVERY": { fa: "ارسال با سفیر", next: "DELIVERED", nextFa: "تکمیل تحویل" },
    "DELIVERED": { fa: "تحویل شد", next: null, nextFa: null },
    "CANCELLED": { fa: "لغو شده", next: null, nextFa: null }
};

async function getAuthToken() {
    // Check localStorage first
    let token = localStorage.getItem("floranova_admin_token");
    if (!token) {
        // Auto-authenticate as florist/admin
        try {
            const resp = await fetch("/api/v1/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: "admin@floranova.ir", password: "Floranova@2026!" })
            });
            if (resp.ok) {
                const data = await resp.json();
                token = data.access_token;
                localStorage.setItem("floranova_admin_token", token);
            }
        } catch (e) {
            console.error("Auth auto-login error", e);
        }
    }
    return token ? `Bearer ${token}` : "";
}

async function fetchStats() {
    try {
        const token = await getAuthToken();
        const res = await fetch("/api/v1/admin/stats", {
            headers: { "Authorization": token }
        });
        if (!res.ok) return;
        const stats = await res.json();
        
        document.getElementById("statRevenue").innerText = Number(stats.total_revenue_toman).toLocaleString("fa-IR");
        document.getElementById("statToday").innerText = Number(stats.today_orders_count).toLocaleString("fa-IR");
        document.getElementById("statArranging").innerText = Number(stats.active_arranging_count).toLocaleString("fa-IR");
        document.getElementById("statStems").innerText = Number(stats.active_fresh_stems).toLocaleString("fa-IR");
        document.getElementById("statSpoilage").innerText = stats.spoilage_risk_percent + "%";
    } catch (e) {
        console.error("Stats refresh error", e);
    }
}

async function fetchOrders() {
    try {
        const token = await getAuthToken();
        const statusFilter = document.getElementById("filterStatus").value;
        let url = "/api/v1/orders/manage/list?limit=50";
        if (statusFilter) {
            url += `&status_filter=${statusFilter}`;
        }
        
        const res = await fetch(url, {
            headers: { "Authorization": token }
        });
        if (!res.ok) return;
        const orders = await res.json();
        
        renderOrdersTable(orders);
    } catch (e) {
        console.error("Orders refresh error", e);
    }
}

function renderOrdersTable(orders) {
    const tbody = document.getElementById("ordersTableBody");
    if (!orders || orders.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 2rem; color: #94a3b8;">هیچ سفارشی مطابق فیلتر یافت نشد.</td></tr>`;
        return;
    }

    tbody.innerHTML = orders.map(ord => {
        const meta = STATUS_MAP[ord.status] || { fa: ord.status, next: null, nextFa: null };
        const actionBtn = meta.next 
            ? `<button class="btn-action-sm primary" onclick="transitionStatus(${ord.id}, '${meta.next}')">${meta.nextFa}</button>`
            : `<span style="color:#94a3b8; font-size:0.75rem;">—</span>`;

        return `
            <tr>
                <td><strong>${ord.tracking_code}</strong></td>
                <td><span class="status-badge ${ord.status}">${meta.fa}</span></td>
                <td>${ord.recipient_name} ${ord.is_surprise ? '<span title="تحویل سورپرایز" style="color:#c48b71; font-size:0.75rem;">🎁</span>' : ''}</td>
                <td>${ord.buyer_name}</td>
                <td>${ord.delivery_date_jalali} <br><span style="font-size:0.75rem; color:#64748b;">${ord.delivery_time_window}</span></td>
                <td><strong>${Number(ord.final_total).toLocaleString("fa-IR")}</strong> <span style="font-size:0.75rem;">تومان</span></td>
                <td>
                    <button class="btn-action-sm" onclick="viewOrderModal(${ord.id})">مشاهده جزئیات</button>
                    ${actionBtn}
                </td>
            </tr>
        `;
    }).join("");
}

async function transitionStatus(orderId, newStatus) {
    const token = await getAuthToken();
    try {
        const resp = await fetch(`/api/v1/orders/manage/${orderId}/transition`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": token
            },
            body: JSON.stringify({
                new_status: newStatus,
                note: `تغییر وضعیت توسط پرسنل کارگاه`
            })
        });

        if (!resp.ok) {
            const err = await resp.json();
            alert("خطا در تغییر وضعیت: " + (err.detail || "انتقال غیرمجاز"));
            return;
        }

        // Silent refresh
        fetchOrders();
        fetchStats();
    } catch (e) {
        console.error("Transition status error", e);
    }
}

async function viewOrderModal(orderId) {
    const token = await getAuthToken();
    try {
        const resp = await fetch(`/api/v1/orders/manage/${orderId}`, {
            headers: { "Authorization": token }
        });
        if (!resp.ok) return;
        const ord = await resp.json();

        document.getElementById("modalTrackingCode").innerText = ord.tracking_code;
        document.getElementById("modalRecipientInfo").innerHTML = `
            <strong>${ord.recipient_name}</strong> (${ord.recipient_phone})<br>
            آدرس: ${ord.recipient_city}، ${ord.recipient_address}
        `;
        document.getElementById("modalBuyerInfo").innerHTML = `
            <strong>${ord.buyer_name}</strong> (${ord.buyer_phone})
        `;
        document.getElementById("modalDeliverySlot").innerText = `${ord.delivery_date_jalali} (${ord.delivery_time_window})`;
        
        document.getElementById("modalCardMessage").innerText = ord.greeting_card_message ? `"${ord.greeting_card_message}"` : "بدون متن کارت پستال";
        document.getElementById("modalRibbon").innerText = ord.ribbon_text ? `متن روبان: ${ord.ribbon_text}` : "بدون روبان اختصاصی";
        
        const itemsHtml = ord.items.map(it => `<li>${it.product_title} × ${it.quantity} — ${Number(it.subtotal).toLocaleString("fa-IR")} تومان</li>`).join("");
        const addonsHtml = (ord.addons || []).map(ad => `<li>[جانبی] ${ad.addon_title} × ${ad.quantity} — ${Number(ad.subtotal).toLocaleString("fa-IR")} تومان</li>`).join("");
        document.getElementById("modalItemsList").innerHTML = itemsHtml + addonsHtml;

        document.getElementById("orderDetailModal").classList.add("active");
    } catch (e) {
        console.error("View order error", e);
    }
}

function closeOrderModal() {
    document.getElementById("orderDetailModal").classList.remove("active");
}

async function fetchInventoryBatches() {
    const token = await getAuthToken();
    try {
        const resp = await fetch("/api/v1/inventory/batches", {
            headers: { "Authorization": token }
        });
        if (!resp.ok) return;
        const batches = await resp.json();

        const tbody = document.getElementById("batchesTableBody");
        tbody.innerHTML = batches.map(b => `
            <tr>
                <td><strong>${b.batch_code}</strong></td>
                <td>${b.flower_species}</td>
                <td>${b.stems_remaining} / ${b.stems_received} شاخه</td>
                <td>${Number(b.unit_cost_toman).toLocaleString("fa-IR")} تومان</td>
                <td>${b.max_freshness_days} روز</td>
                <td>
                    <span class="status-badge ${b.status === 'FRESH' ? 'DELIVERED' : (b.status === 'NEEDS_ROTATION' ? 'QUALITY_APPROVED' : 'CANCELLED')}">
                        ${b.status === 'FRESH' ? 'شاداب' : (b.status === 'NEEDS_ROTATION' ? 'چرخش سریع' : 'ضایعات')}
                    </span>
                </td>
            </tr>
        `).join("");
    } catch (e) {
        console.error("Batches error", e);
    }
}

function switchTab(tab) {
    currentTab = tab;
    document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
    document.querySelectorAll(".admin-tab-pane").forEach(pane => pane.style.display = "none");

    if (tab === "orders") {
        document.getElementById("tabBtnOrders").classList.add("active");
        document.getElementById("paneOrders").style.display = "block";
        fetchOrders();
    } else if (tab === "inventory") {
        document.getElementById("tabBtnInventory").classList.add("active");
        document.getElementById("paneInventory").style.display = "block";
        fetchInventoryBatches();
    }
}

// Initialization and silent polling loop
document.addEventListener("DOMContentLoaded", () => {
    fetchStats();
    fetchOrders();

    // Silent polling every 15 seconds (no banners, no sound, pure background state refresh)
    setInterval(() => {
        fetchStats();
        if (currentTab === "orders") {
            fetchOrders();
        } else if (currentTab === "inventory") {
            fetchInventoryBatches();
        }
    }, 15000);
});
