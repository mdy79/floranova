import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from floranova.database import async_session_factory, init_db
from floranova.models.user import User, UserRole
from floranova.models.product import Category, Product, AddonItem, ArrangementType, AddonType
from floranova.models.inventory import FlowerFreshnessBatch, FreshnessStatus
from floranova.models.slot import DeliverySlot
from floranova.models.order import Order, OrderItem, OrderAddon, OrderStatus
from floranova.core.security import hash_password
from floranova.core.dates import get_available_delivery_dates, get_today_jalali


async def seed():
    print("🌱 Initializing database schema...")
    await init_db()

    async with async_session_factory() as db:
        # Check if already seeded
        admin_check = await db.execute(select(User).where(User.email == "admin@floranova.ir"))
        if admin_check.scalar_one_or_none():
            print("Database already contains seed data. Skipping.")
            return

        print("👤 Creating staff and customer accounts...")
        admin = User(
            email="admin@floranova.ir",
            phone_number="09121111111",
            full_name="مهراد دادگر (مدیر ارشد آتلیه)",
            hashed_password=hash_password("Floranova@2026!"),
            role=UserRole.ADMIN,
            is_active=True,
        )
        florist = User(
            email="florist@floranova.ir",
            phone_number="09122222222",
            full_name="سارا احمدی (سرپرست گلآرایی)",
            hashed_password=hash_password("Florist@2026!"),
            role=UserRole.FLORIST,
            is_active=True,
        )
        customer = User(
            email="customer@floranova.ir",
            phone_number="09123333333",
            full_name="کیانوش راد",
            hashed_password=hash_password("Customer@2026!"),
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        db.add_all([admin, florist, customer])
        await db.flush()

        print("📁 Creating floral categories...")
        cat_bouquets = Category(
            slug="bouquets",
            name_fa="دسته گل لوکس",
            name_en="Luxury Bouquets",
            description="دسته گلهای دستپیچ ژورنالی با کاغذ ضدآب و روبان ابریشمی",
        )
        cat_boxes = Category(
            slug="flower-boxes",
            name_fa="باکس گل اختصاصی",
            name_en="Bespoke Boxes",
            description="جعبههای مخمل و هاردباکس چیدمان شده با اسفنج آبکش خارجی",
        )
        cat_baskets = Category(
            slug="baskets",
            name_fa="سبد گل تشریفاتی",
            name_en="Ceremonial Baskets",
            description="سبدهای چوبی دستبافت مناسب مراسم تبریک، افتتاحیه و خواستگاری",
        )
        cat_orchids = Category(
            slug="orchids",
            name_fa="ارکیده و گلهای ماندگار",
            name_en="Orchids & Living Blooms",
            description="گلدانهای ارکیده فالانوپسیس وارداتی با ماندگاری بالا",
        )
        db.add_all([cat_bouquets, cat_boxes, cat_baskets, cat_orchids])
        await db.flush()

        print("🌸 Creating artisan flower products...")
        products = [
            Product(
                slug="royal-velvet-red-roses",
                title_fa="دسته گل رویال رز مخملی هلندی",
                title_en="Royal Velvet Dutch Red Roses",
                description_fa="۳۶ شاخه رز سوپر هلندی دستچین با پوشش اکالیپتوس نقرهای و بستهبندی ژورنالی مشکی مات",
                price=3400000,
                discount_price=2950000,
                category_id=cat_bouquets.id,
                arrangement_type=ArrangementType.BOUQUET,
                flower_types=["رز هلندی قرمز سوپر", "اکالیپتوس معطر", "ورونیکا"],
                stem_count=36,
                vase_included=False,
                estimated_prep_time_minutes=45,
                primary_image="https://images.unsplash.com/photo-1561181286-d3fee7d55364?auto=format&fit=crop&w=800&q=80",
                gallery_images=["https://images.unsplash.com/photo-1561181286-d3fee7d55364?auto=format&fit=crop&w=800&q=80"],
                is_featured=True,
                is_available=True,
            ),
            Product(
                slug="aurora-pastel-peony-bouquet",
                title_fa="دسته گل آتلیهای پاستلی شفق",
                title_en="Aurora Pastel Garden Bouquet",
                description_fa="ترکیب رمانتیک پیونی صورتی هلندی، رز مینیاتوری نباتی و لیسیانتوس با دیزاین ارگانیک فرانسوی",
                price=2800000,
                discount_price=None,
                category_id=cat_bouquets.id,
                arrangement_type=ArrangementType.BOUQUET,
                flower_types=["پیونی هلندی", "رز مینیاتوری", "لیسیانتوس", "عروس (ژیپسوفیلا)"],
                stem_count=24,
                vase_included=False,
                estimated_prep_time_minutes=50,
                primary_image="https://images.unsplash.com/photo-1526047932273-341f2a7631f9?auto=format&fit=crop&w=800&q=80",
                gallery_images=["https://images.unsplash.com/photo-1526047932273-341f2a7631f9?auto=format&fit=crop&w=800&q=80"],
                is_featured=True,
                is_available=True,
            ),
            Product(
                slug="emerald-luxury-flower-box",
                title_fa="باکس هاردباکس زمردین ارکیده و رز",
                title_en="Emerald Box of Orchids & White Roses",
                description_fa="باکس سبز زمردی لاکچری همراه با شاخههای ارکیده سفید فالانوپسیس، رز هلندی سفید و مروارید تزیینی",
                price=4200000,
                discount_price=3850000,
                category_id=cat_boxes.id,
                arrangement_type=ArrangementType.BOX,
                flower_types=["ارکیده فالانوپسیس", "رز سفید هلندی", "هورتانسیا (ادریس)"],
                stem_count=30,
                vase_included=True,
                estimated_prep_time_minutes=60,
                primary_image="https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11?auto=format&fit=crop&w=800&q=80",
                gallery_images=["https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11?auto=format&fit=crop&w=800&q=80"],
                is_featured=True,
                is_available=True,
            ),
            Product(
                slug="solace-grand-ceremonial-basket",
                title_fa="سبد گل تشریفاتی لوکس آیرین",
                title_en="Irene Grand Ceremonial Basket",
                description_fa="سبد بزرگ دستبافت چوبی پر شده با گلهای آنتوریوم زرشکی، لیلیوم اورینتال معطر و برگهای استرلیتزیا",
                price=6500000,
                discount_price=None,
                category_id=cat_baskets.id,
                arrangement_type=ArrangementType.BASKET,
                flower_types=["آنتوریوم", "لیلیوم اورینتال", "رز هلندی", "برگ پالم"],
                stem_count=48,
                vase_included=True,
                estimated_prep_time_minutes=90,
                primary_image="https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=800&q=80",
                gallery_images=["https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=800&q=80"],
                is_featured=False,
                is_available=True,
            ),
            Product(
                slug="zen-phalaenopsis-orchid-pot",
                title_fa="گلدان سرامیکی دوقلوی ارکیده فالانوپسیس",
                title_en="Twin Phalaenopsis Orchid in Ceramic Pot",
                description_fa="دو بوته ارکیده وارداتی ارغوانی با غنچههای فراوان در گلدان سرامیکی وارداتی با ماندگاری بیش از ۴۵ روز",
                price=3100000,
                discount_price=2750000,
                category_id=cat_orchids.id,
                arrangement_type=ArrangementType.VASE,
                flower_types=["ارکیده فالانوپسیس ارغوانی"],
                stem_count=4,
                vase_included=True,
                estimated_prep_time_minutes=30,
                primary_image="https://images.unsplash.com/photo-1508610048659-a06b669e3321?auto=format&fit=crop&w=800&q=80",
                gallery_images=["https://images.unsplash.com/photo-1508610048659-a06b669e3321?auto=format&fit=crop&w=800&q=80"],
                is_featured=True,
                is_available=True,
            ),
        ]
        db.add_all(products)
        await db.flush()

        print("🎁 Creating curated floral add-ons...")
        addons = [
            AddonItem(
                slug="handwritten-luxury-card",
                title_fa="کارت دستنویس نفیس با مرکب",
                addon_type=AddonType.GREETING_CARD,
                price=65000,
                image_url="https://images.unsplash.com/photo-1607344645866-009c320c5ab8?auto=format&fit=crop&w=200&q=80",
                is_active=True,
            ),
            AddonItem(
                slug="belgian-artisan-chocolates",
                title_fa="جعبه شکلات دستساز بلژیکی (۱۲ عددی)",
                addon_type=AddonType.CHOCOLATE,
                price=380000,
                image_url="https://images.unsplash.com/photo-1549007994-cb92caebd54b?auto=format&fit=crop&w=200&q=80",
                is_active=True,
            ),
            AddonItem(
                slug="nordic-ceramic-vase",
                title_fa="گلدان سرامیکی مینیمال کرم",
                addon_type=AddonType.VASE,
                price=490000,
                image_url="https://images.unsplash.com/photo-1612196808214-b8e1d6145a8c?auto=format&fit=crop&w=200&q=80",
                is_active=True,
            ),
            AddonItem(
                slug="celebration-helium-balloon",
                title_fa="بادکنک هلیومی کروم بژ/رزگلد",
                addon_type=AddonType.BALLOON,
                price=120000,
                image_url="https://images.unsplash.com/photo-1530103862676-de8c9debad1d?auto=format&fit=crop&w=200&q=80",
                is_active=True,
            ),
        ]
        db.add_all(addons)
        await db.flush()

        print("❄️ Creating flower freshness batches in cold storage...")
        batches = [
            FlowerFreshnessBatch(
                batch_code="BATCH-202610-ROSE",
                flower_species="رز هلندی قرمز سوپر ممتاز",
                stems_received=400,
                stems_remaining=265,
                unit_cost_toman=42000,
                received_date=datetime.now(timezone.utc) - timedelta(days=1),
                max_freshness_days=6,
                status=FreshnessStatus.FRESH,
                notes="بار تازه از گلخانه ورامین، ساقههای درشت و بدون آفت",
            ),
            FlowerFreshnessBatch(
                batch_code="BATCH-202610-ORCHID",
                flower_species="ارکیده فالانوپسیس سفید وارداتی",
                stems_received=80,
                stems_remaining=54,
                unit_cost_toman=110000,
                received_date=datetime.now(timezone.utc) - timedelta(days=2),
                max_freshness_days=14,
                status=FreshnessStatus.FRESH,
                notes="بار پرواز آمستردام، رطوبت سردخانه روی ۸۵٪ تنظیم است",
            ),
            FlowerFreshnessBatch(
                batch_code="BATCH-202610-LISIANTHUS",
                flower_species="لیسیانتوس نباتی و یاسی",
                stems_received=250,
                stems_remaining=60,
                unit_cost_toman=22000,
                received_date=datetime.now(timezone.utc) - timedelta(days=4),
                max_freshness_days=5,
                status=FreshnessStatus.NEEDS_ROTATION,
                notes="روز چهارم ماندگاری، اولویت استفاده در دستهگلهای امروز",
            ),
        ]
        db.add_all(batches)
        await db.flush()

        print("🕒 Initializing delivery slots for the week...")
        date_list = get_available_delivery_dates(days_ahead=7)
        windows = [
            ("09:00-13:00", "بازه صبح (۰۹:۰۰ الی ۱۳:۰۰)"),
            ("13:00-17:00", "بازه عصر (۱۳:۰۰ الی ۱۷:۰۰)"),
            ("17:00-21:00", "بازه شب (۱۷:۰۰ الی ۲۱:۰۰)"),
        ]
        slots = []
        for d in date_list:
            for w, lbl in windows:
                slots.append(
                    DeliverySlot(
                        date_jalali=d["date_jalali"],
                        time_window=w,
                        label_fa=lbl,
                        max_capacity=8,
                        reserved_count=1 if d["is_today"] else 0,
                        is_active=True,
                    )
                )
        db.add_all(slots)
        await db.flush()

        print("📦 Creating realistic orders in various lifecycle stages...")
        today_j = get_today_jalali()

        # Order 1: ARRANGING (Florist actively assembling blooms)
        order_arranging = Order(
            tracking_code="FN-829104",
            status=OrderStatus.ARRANGING,
            customer_id=customer.id,
            buyer_name="پرهام صادقی",
            buyer_phone="09124445566",
            buyer_email="parham@example.com",
            recipient_name="نیلوفر کاظمی",
            recipient_phone="09127778899",
            recipient_address="نیاوران، خیابان یاسر، کوچه تبریزی، پلاک ۱۴، واحد ۸",
            recipient_city="تهران",
            district_zone="منطقه ۱",
            is_surprise=True,
            greeting_card_message="برای زیباترین روزهای پیش رو، با آرزوی سالی پر از لبخند و شکوفایی.",
            greeting_card_sender="پرهام",
            ribbon_text="تولدت مبارک نیلوفر عزیزم",
            delivery_date_jalali=today_j,
            delivery_time_window="13:00-17:00",
            delivery_notes="زنگ واحد ۸ زده شود و تحویل شخص خانم کاظمی گردد.",
            items_total=2950000,
            addons_total=65000,
            delivery_fee=0,
            discount_amount=0,
            final_total=3015000,
            status_history=[
                {
                    "from_status": None,
                    "to_status": "CONFIRMED",
                    "to_status_fa": "تایید سفارش و رزرو گل",
                    "timestamp_jalali": today_j + " 09:30",
                    "timestamp_iso": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
                    "changed_by": "سیستم سفارش آنلاین",
                    "note": "سفارش ثبت و ظرفیت آتلیه رزرو شد.",
                },
                {
                    "from_status": "CONFIRMED",
                    "to_status": "ARRANGING",
                    "to_status_fa": "در حال گلآرایی در آتلیه",
                    "timestamp_jalali": today_j + " 10:15",
                    "timestamp_iso": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                    "changed_by": "سارا احمدی (سرپرست گلآرایی)",
                    "note": "شاخههای رز قرمز ممتاز از سردخانه برداشت شد و چیدمان آغاز گردید.",
                },
            ],
            items=[
                OrderItem(
                    product_id=products[0].id,
                    product_title=products[0].title_fa,
                    unit_price=2950000,
                    quantity=1,
                    subtotal=2950000,
                )
            ],
            addons=[
                OrderAddon(
                    addon_id=addons[0].id,
                    addon_title=addons[0].title_fa,
                    unit_price=65000,
                    quantity=1,
                    subtotal=65000,
                )
            ],
        )

        # Order 2: QUALITY_APPROVED (Ready for courier pickup with QC photo)
        order_qc = Order(
            tracking_code="FN-941820",
            status=OrderStatus.QUALITY_APPROVED,
            customer_id=customer.id,
            buyer_name="دکتر مریم جهانگیری",
            buyer_phone="09128889900",
            recipient_name="دکتر آریا فرهمند",
            recipient_phone="09121113344",
            recipient_address="سعادتآباد، بلوار پاکنژاد، بالاتر از میدان بهرود، بیمارستان آتیه",
            recipient_city="تهران",
            district_zone="منطقه ۲",
            is_surprise=False,
            greeting_card_message="تبریک صمیمانه جهت ارتقای رتبه علمی و آرزوی درخشش روزافزون.",
            greeting_card_sender="مریم جهانگیری",
            ribbon_text="با احترام و افتخار",
            delivery_date_jalali=today_j,
            delivery_time_window="13:00-17:00",
            delivery_notes="تحویل دفتر ریاست بخش جراحی",
            items_total=3850000,
            addons_total=380000,
            delivery_fee=0,
            discount_amount=0,
            final_total=4230000,
            arrangement_photo_url="https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11?auto=format&fit=crop&w=800&q=80",
            status_history=[
                {
                    "from_status": "ARRANGING",
                    "to_status": "QUALITY_APPROVED",
                    "to_status_fa": "تایید کنترل کیفی گلها",
                    "timestamp_jalali": today_j + " 11:45",
                    "timestamp_iso": (datetime.now(timezone.utc) - timedelta(minutes=45)).isoformat(),
                    "changed_by": "سارا احمدی (سرپرست گلآرایی)",
                    "note": "تصویر چیدمان باکس زمردین تایید شد و همراه شکلات دستساز آماده ارسال است.",
                }
            ],
            items=[
                OrderItem(
                    product_id=products[2].id,
                    product_title=products[2].title_fa,
                    unit_price=3850000,
                    quantity=1,
                    subtotal=3850000,
                )
            ],
            addons=[
                OrderAddon(
                    addon_id=addons[1].id,
                    addon_title=addons[1].title_fa,
                    unit_price=380000,
                    quantity=1,
                    subtotal=380000,
                )
            ],
        )

        # Order 3: DELIVERED (Successfully completed)
        order_delivered = Order(
            tracking_code="FN-105829",
            status=OrderStatus.DELIVERED,
            customer_id=customer.id,
            buyer_name="فرزاد نادری",
            buyer_phone="09125556677",
            recipient_name="مهتاب نادری",
            recipient_phone="09126667788",
            recipient_address="شهرک غرب، خیابان ایرانزمین، کوچه دوم، پلاک ۵",
            recipient_city="تهران",
            district_zone="منطقه ۲",
            is_surprise=True,
            greeting_card_message="سالگرد پیوندمان مبارک عزیزترینم. بیست سال عشق بیپایان.",
            greeting_card_sender="فرزاد",
            ribbon_text="همیشه دوستت دارم",
            delivery_date_jalali=today_j,
            delivery_time_window="09:00-13:00",
            delivery_notes="تحویل شد",
            items_total=2750000,
            addons_total=0,
            delivery_fee=0,
            discount_amount=0,
            final_total=2750000,
            status_history=[
                {
                    "from_status": "OUT_FOR_DELIVERY",
                    "to_status": "DELIVERED",
                    "to_status_fa": "تحویل نهایی به گیرنده",
                    "timestamp_jalali": today_j + " 12:10",
                    "timestamp_iso": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                    "changed_by": "سفیر تشریفاتی (علی مرادی)",
                    "note": "تحویل با لبخند و رضایت کامل گیرنده انجام گردید.",
                }
            ],
            items=[
                OrderItem(
                    product_id=products[4].id,
                    product_title=products[4].title_fa,
                    unit_price=2750000,
                    quantity=1,
                    subtotal=2750000,
                )
            ],
        )

        db.add_all([order_arranging, order_qc, order_delivered])
        await db.commit()

        print("✨ Database successfully seeded with production floristry catalog & sample operations!")


if __name__ == "__main__":
    asyncio.run(seed())
