let currentProduct = null;
let selectedAddons = new Map();
let currentBasePrice = 0;
const deliveryFee = 75000;
const freeThreshold = 2500000;

function openCustomizer(productJson) {
    try {
        currentProduct = typeof productJson === 'string' ? JSON.parse(productJson) : productJson;
    } catch (e) {
        console.error("Failed to parse product data", e);
        return;
    }

    currentBasePrice = currentProduct.discount_price || currentProduct.price;
    selectedAddons.clear();

    document.getElementById("modalTitle").innerText = currentProduct.title_fa;
    document.getElementById("modalImg").src = currentProduct.primary_image;
    document.getElementById("modalDesc").innerText = currentProduct.description_fa;
    document.getElementById("modalStems").innerText = `ترکیب ${currentProduct.stem_count} شاخه گل طبیعی و تازه`;

    // Reset addons selection
    document.querySelectorAll(".addon-card-check").forEach(el => {
        el.classList.remove("selected");
    });

    // Reset inputs
    document.getElementById("orderForm").reset();
    
    // Load initial slots
    const dateSelect = document.getElementById("deliveryDateSelect");
    if (dateSelect && dateSelect.value) {
        loadWindowsForDate(dateSelect.value);
    }

    updatePriceSummary();
    document.getElementById("customizerModal").classList.add("active");
}

function closeCustomizer() {
    document.getElementById("customizerModal").classList.remove("active");
}

function toggleAddon(id, title, price, elem) {
    if (selectedAddons.has(id)) {
        selectedAddons.delete(id);
        elem.classList.remove("selected");
    } else {
        selectedAddons.set(id, { id: id, title: title, price: price, quantity: 1 });
        elem.classList.add("selected");
    }
    updatePriceSummary();
}

function updatePriceSummary() {
    let addonsTotal = 0;
    selectedAddons.forEach(item => {
        addonsTotal += item.price * item.quantity;
    });

    const subtotal = currentBasePrice + addonsTotal;
    const finalFee = subtotal >= freeThreshold ? 0 : deliveryFee;
    const finalTotal = subtotal + finalFee;

    document.getElementById("summaryBasePrice").innerText = currentBasePrice.toLocaleString("fa-IR") + " تومان";
    document.getElementById("summaryAddonsPrice").innerText = addonsTotal.toLocaleString("fa-IR") + " تومان";
    document.getElementById("summaryDeliveryFee").innerText = finalFee === 0 ? "رایگان (سفارش بالای ۲.۵ م)" : finalFee.toLocaleString("fa-IR") + " تومان";
    document.getElementById("summaryFinalTotal").innerText = finalTotal.toLocaleString("fa-IR") + " تومان";
}

async function loadWindowsForDate(jalaliDate) {
    const windowSelect = document.getElementById("timeWindowSelect");
    windowSelect.innerHTML = "<option value=''>در حال بارگذاری بازههای تحویل...</option>";
    try {
        const resp = await fetch(`/api/v1/slots/windows?date_jalali=${encodeURIComponent(jalaliDate)}`);
        const windows = await resp.json();
        windowSelect.innerHTML = "";
        
        windows.forEach(w => {
            const opt = document.createElement("option");
            opt.value = w.time_window;
            opt.textContent = `${w.label_fa} — (${w.remaining_capacity} ظرفیت خالی)`;
            if (!w.is_available) {
                opt.disabled = true;
                opt.textContent += " (تکمیل ظرفیت)";
            }
            windowSelect.appendChild(opt);
        });
    } catch (e) {
        console.error("Error fetching windows", e);
        windowSelect.innerHTML = "<option value=''>خطا در دریافت بازهها</option>";
    }
}

async function submitOrder(e) {
    e.preventDefault();
    if (!currentProduct) return;

    const btn = document.getElementById("btnSubmitOrder");
    btn.disabled = true;
    btn.innerText = "در حال ثبت سفارش و صدور شناسنامه...";

    const addonsArray = [];
    selectedAddons.forEach(item => {
        addonsArray.push({ addon_id: item.id, quantity: item.quantity });
    });

    const payload = {
        buyer_name: document.getElementById("buyerName").value.trim(),
        buyer_phone: document.getElementById("buyerPhone").value.trim(),
        buyer_email: document.getElementById("buyerEmail").value.trim() || null,
        recipient_name: document.getElementById("recipientName").value.trim(),
        recipient_phone: document.getElementById("recipientPhone").value.trim(),
        recipient_address: document.getElementById("recipientAddress").value.trim(),
        recipient_city: "تهران",
        district_zone: document.getElementById("districtZone").value || null,
        is_surprise: document.getElementById("isSurprise").checked,
        greeting_card_message: document.getElementById("cardMessage").value.trim() || null,
        greeting_card_sender: document.getElementById("cardSender").value.trim() || null,
        ribbon_text: document.getElementById("ribbonText").value.trim() || null,
        delivery_date_jalali: document.getElementById("deliveryDateSelect").value,
        delivery_time_window: document.getElementById("timeWindowSelect").value,
        delivery_notes: document.getElementById("deliveryNotes").value.trim() || null,
        items: [
            {
                product_id: currentProduct.id,
                quantity: 1
            }
        ],
        addons: addonsArray
    };

    try {
        const resp = await fetch("/api/v1/orders/checkout", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!resp.ok) {
            const errData = await resp.json();
            alert("خطا در ثبت سفارش: " + (errData.detail || "اطلاعات ارسالی معتبر نیست"));
            btn.disabled = false;
            btn.innerText = "ثبت نهایی و دریافت کد رهگیری";
            return;
        }

        const createdOrder = await resp.json();
        // Redirect immediately to order tracking page
        window.location.href = `/track/${createdOrder.tracking_code}`;
    } catch (err) {
        console.error("Order submit exception", err);
        alert("خطای ارتباط با سرور کارگاه");
        btn.disabled = false;
        btn.innerText = "ثبت نهایی و دریافت کد رهگیری";
    }
}

// Global hook for date change
document.addEventListener("DOMContentLoaded", () => {
    const dateSelect = document.getElementById("deliveryDateSelect");
    if (dateSelect) {
        dateSelect.addEventListener("change", (e) => {
            loadWindowsForDate(e.target.value);
        });
    }

    const orderForm = document.getElementById("orderForm");
    if (orderForm) {
        orderForm.addEventListener("submit", submitOrder);
    }
});
