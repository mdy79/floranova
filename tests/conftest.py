import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from floranova.database import Base, get_db
from floranova.main import app
from floranova.models.user import User, UserRole
from floranova.models.product import Category, Product, AddonItem, ArrangementType, AddonType
from floranova.models.slot import DeliverySlot
from floranova.core.security import hash_password, create_access_token
from floranova.core.dates import get_today_jalali

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestSessionFactory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionFactory() as session:
        # Seed core fixtures
        admin = User(
            email="admin@test.ir",
            phone_number="09120000001",
            full_name="مدیر تست",
            hashed_password=hash_password("Pass@1234"),
            role=UserRole.ADMIN,
            is_active=True,
        )
        florist = User(
            email="florist@test.ir",
            phone_number="09120000002",
            full_name="دیزاینر تست",
            hashed_password=hash_password("Pass@1234"),
            role=UserRole.FLORIST,
            is_active=True,
        )
        customer = User(
            email="customer@test.ir",
            phone_number="09120000003",
            full_name="مشتری تست",
            hashed_password=hash_password("Pass@1234"),
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        cat = Category(
            slug="roses",
            name_fa="دسته گل رز",
            name_en="Roses",
            description="انواع رز هلندی",
        )
        session.add_all([admin, florist, customer, cat])
        await session.flush()

        prod = Product(
            slug="classic-red-roses",
            title_fa="دسته گل رز هلندی کلاسیک",
            title_en="Classic Red Roses",
            description_fa="۲۰ شاخه رز هلندی ممتاز",
            price=2000000,
            discount_price=1800000,
            category_id=cat.id,
            arrangement_type=ArrangementType.BOUQUET,
            flower_types=["رز هلندی"],
            stem_count=20,
            vase_included=False,
            estimated_prep_time_minutes=30,
            primary_image="https://example.com/rose.jpg",
            is_featured=True,
            is_available=True,
        )
        addon = AddonItem(
            slug="calligraphy-card",
            title_fa="کارت دستنویس",
            addon_type=AddonType.GREETING_CARD,
            price=50000,
            image_url="https://example.com/card.jpg",
            is_active=True,
        )
        today_j = get_today_jalali()
        slot = DeliverySlot(
            date_jalali=today_j,
            time_window="09:00-13:00",
            label_fa="صبح",
            max_capacity=5,
            reserved_count=0,
            is_active=True,
        )
        session.add_all([prod, addon, slot])
        await session.commit()

        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_token():
    return create_access_token({"sub": "1", "role": "ADMIN"})


@pytest_asyncio.fixture
async def customer_token():
    return create_access_token({"sub": "3", "role": "CUSTOMER"})
