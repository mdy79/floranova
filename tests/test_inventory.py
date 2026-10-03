import pytest


@pytest.mark.asyncio
async def test_inventory_batches_and_summary(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create a flower batch
    batch_payload = {
        "batch_code": "BATCH-TEST-PEONY",
        "flower_species": "پیونی هلندی صورتی ممتاز",
        "stems_received": 100,
        "stems_remaining": 80,
        "unit_cost_toman": 35000,
        "max_freshness_days": 5,
        "notes": "بار آزمایشی",
    }
    create_resp = await client.post("/api/v1/inventory/batches", headers=headers, json=batch_payload)
    assert create_resp.status_code == 201
    batch_data = create_resp.json()
    batch_id = batch_data["id"]
    assert batch_data["batch_code"] == "BATCH-TEST-PEONY"
    assert batch_data["status"] == "FRESH"

    # 2. Update batch: mark rotation needed
    update_payload = {
        "stems_remaining": 40,
        "status": "NEEDS_ROTATION",
        "notes": "روز سوم ماندگاری، تخفیف فروش ویژه اعمال شود",
    }
    update_resp = await client.patch(f"/api/v1/inventory/batches/{batch_id}", headers=headers, json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "NEEDS_ROTATION"
    assert update_resp.json()["stems_remaining"] == 40

    # 3. Check inventory summary
    summary_resp = await client.get("/api/v1/inventory/summary", headers=headers)
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["total_stems_rotating"] == 40
    assert summary["spoilage_risk_percentage"] == 100.0


@pytest.mark.asyncio
async def test_unauthorized_inventory_access_blocked(client):
    resp = await client.get("/api/v1/inventory/batches")
    assert resp.status_code == 401
