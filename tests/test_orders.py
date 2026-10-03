import pytest
from floranova.core.dates import get_today_jalali


@pytest.mark.asyncio
async def test_checkout_and_lifecycle_flow(client, admin_token):
    today_j = get_today_jalali()

    # 1. Place checkout order
    payload = {
        "buyer_name": "بهرام رادان",
        "buyer_phone": "09121234567",
        "buyer_email": "bahram@example.com",
        "recipient_name": "میترا حبیبی",
        "recipient_phone": "09129876543",
        "recipient_address": "زعفرانیه، خیابان آصف، پلاک ۲۰",
        "recipient_city": "تهران",
        "district_zone": "منطقه ۱",
        "is_surprise": True,
        "greeting_card_message": "با تمام وجودم دوستت دارم",
        "greeting_card_sender": "بهرام",
        "ribbon_text": "عشق جاودان",
        "delivery_date_jalali": today_j,
        "delivery_time_window": "09:00-13:00",
        "items": [
            {
                "product_id": 1,
                "quantity": 1,
            }
        ],
        "addons": [
            {
                "addon_id": 1,
                "quantity": 1,
            }
        ],
    }

    checkout_resp = await client.post("/api/v1/orders/checkout", json=payload)
    assert checkout_resp.status_code == 201
    order_data = checkout_resp.json()
    tracking_code = order_data["tracking_code"]
    order_id = order_data["id"]

    assert order_data["status"] == "CONFIRMED"
    assert order_data["is_surprise"] is True
    # Product discounted price: 1,800,000 + Addon: 50,000 = 1,850,000 (< 2.5M so delivery fee 75,000 applied)
    assert order_data["items_total"] == 1800000
    assert order_data["addons_total"] == 50000
    assert order_data["delivery_fee"] == 75000
    assert order_data["final_total"] == 1925000

    # 2. Public Tracking endpoint
    track_resp = await client.get(f"/api/v1/orders/track/{tracking_code}")
    assert track_resp.status_code == 200
    track_data = track_resp.json()
    assert track_data["tracking_code"] == tracking_code
    assert track_data["status"] == "CONFIRMED"
    # Verify name is masked for privacy
    assert "*" in track_data["recipient_name_masked"]
    assert track_data["recipient_name_masked"] != "میترا حبیبی"

    # 3. Staff Advance Status: CONFIRMED -> ARRANGING
    trans1 = await client.post(
        f"/api/v1/orders/manage/{order_id}/transition",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "new_status": "ARRANGING",
            "note": "شروع گلآرایی رزها در آتلیه",
        },
    )
    assert trans1.status_code == 200
    assert trans1.json()["status"] == "ARRANGING"

    # 4. Staff Advance Status: ARRANGING -> QUALITY_APPROVED
    trans2 = await client.post(
        f"/api/v1/orders/manage/{order_id}/transition",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "new_status": "QUALITY_APPROVED",
            "photo_url": "https://example.com/qc_rose.jpg",
            "note": "بررسی شادابی شاخهها و تایید فرم چیدمان",
        },
    )
    assert trans2.status_code == 200
    assert trans2.json()["status"] == "QUALITY_APPROVED"
    assert trans2.json()["arrangement_photo_url"] == "https://example.com/qc_rose.jpg"

    # 5. Invalid Transition: Cannot jump straight from QUALITY_APPROVED to DELIVERED (Must go through OUT_FOR_DELIVERY)
    invalid_trans = await client.post(
        f"/api/v1/orders/manage/{order_id}/transition",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "new_status": "DELIVERED",
        },
    )
    assert invalid_trans.status_code == 400
    assert "امکان تغییر وضعیت" in invalid_trans.json()["detail"]

    # 6. Advance QUALITY_APPROVED -> OUT_FOR_DELIVERY -> DELIVERED
    trans3 = await client.post(
        f"/api/v1/orders/manage/{order_id}/transition",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"new_status": "OUT_FOR_DELIVERY", "note": "تحویل به سفیر"},
    )
    assert trans3.status_code == 200

    trans4 = await client.post(
        f"/api/v1/orders/manage/{order_id}/transition",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"new_status": "DELIVERED", "note": "تحویل موفق به گیرنده"},
    )
    assert trans4.status_code == 200
    assert trans4.json()["status"] == "DELIVERED"
