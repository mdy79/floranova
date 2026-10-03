import pytest


@pytest.mark.asyncio
async def test_catalog_categories_and_products(client):
    # 1. Fetch categories
    cats_resp = await client.get("/api/v1/catalog/categories")
    assert cats_resp.status_code == 200
    categories = cats_resp.json()
    assert len(categories) >= 1
    assert categories[0]["slug"] == "roses"

    # 2. Fetch products
    prods_resp = await client.get("/api/v1/catalog/products")
    assert prods_resp.status_code == 200
    products = prods_resp.json()
    assert len(products) >= 1
    assert products[0]["slug"] == "classic-red-roses"
    assert products[0]["stem_count"] == 20

    # 3. Filter by category
    filter_resp = await client.get("/api/v1/catalog/products?category_slug=roses")
    assert filter_resp.status_code == 200
    assert len(filter_resp.json()) >= 1

    # 4. Search query
    search_resp = await client.get("/api/v1/catalog/products?search=کلاسیک")
    assert search_resp.status_code == 200
    assert len(search_resp.json()) >= 1

    # 5. Product detail
    detail_resp = await client.get("/api/v1/catalog/products/classic-red-roses")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["title_fa"] == "دسته گل رز هلندی کلاسیک"
    assert detail["category"]["slug"] == "roses"

    # 6. Fetch addons
    addons_resp = await client.get("/api/v1/catalog/addons")
    assert addons_resp.status_code == 200
    addons = addons_resp.json()
    assert len(addons) >= 1
    assert addons[0]["slug"] == "calligraphy-card"
