"""
Deterministic demo seed for a waffle business.
All IDs are derived via uuid5 so the seed is idempotent — running it twice
produces no duplicates.
"""

import uuid
from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.catalog import Category, Product
from app.models.modifier import ModifierGroup, ModifierOption, ProductModifierGroup
from app.models.order import Order, OrderItem, OrderItemModifier
from app.models.settings import BusinessSettings
from app.models.tenant import Branch, Tenant
from app.models.user import User

_NS = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _id(name: str) -> str:
    return str(uuid.uuid5(_NS, name))


def _dt(days_ago: int, hour: int = 12, minute: int = 0) -> datetime:
    base = datetime.now(timezone.utc).replace(hour=hour, minute=minute, second=0, microsecond=0)
    return base - timedelta(days=days_ago)


def run(db: Session) -> None:
    """Insert demo data. Safe to call multiple times — skips if already present."""

    tenant_id = _id("tenant:waffle-kosesi")

    if db.query(Tenant).filter(Tenant.id == tenant_id).first():
        print("Demo data already present — skipping.")
        return

    print("Seeding demo data...")

    # ── Tenant ────────────────────────────────────────────────────────────────
    tenant = Tenant(
        id=tenant_id,
        business_name="Waffle Köşesi",
        slug="waffle-kosesi",
        business_type="waffle",
        currency="TRY",
        is_active=True,
        onboarding_completed=True,
    )
    db.add(tenant)
    db.flush()

    # ── Branch ────────────────────────────────────────────────────────────────
    branch_id = _id("branch:ana-sube")
    branch = Branch(
        id=branch_id,
        tenant_id=tenant_id,
        name="Ana Şube",
        city="İstanbul",
        district="Kadıköy",
        address="Moda Cad. No:12, Kadıköy / İstanbul",
        is_active=True,
    )
    db.add(branch)
    db.flush()

    # ── Business settings ─────────────────────────────────────────────────────
    db.add(
        BusinessSettings(
            id=_id("settings:ana-sube"),
            tenant_id=tenant_id,
            branch_id=branch_id,
            service_mode="both",
            accepts_orders=True,
        )
    )

    # ── Users ─────────────────────────────────────────────────────────────────
    db.add(
        User(
            id=_id("user:demo-admin"),
            tenant_id=tenant_id,
            name="Demo Admin",
            email="demo@orderiq.app",
            password_hash=_pwd.hash("demo1234"),
            role="admin",
            is_active=True,
        )
    )
    db.add(
        User(
            id=_id("user:kitchen"),
            tenant_id=tenant_id,
            name="Mutfak Ekranı",
            email="kitchen@orderiq.app",
            password_hash=_pwd.hash("demo1234"),
            role="kitchen",
            is_active=True,
        )
    )
    db.flush()

    # ── Categories ────────────────────────────────────────────────────────────
    cat_names = ["Wafflelar", "Soslar", "Meyveler", "Süslemeler", "İçecekler"]
    cats: dict[str, str] = {}  # name → id
    for i, name in enumerate(cat_names):
        cid = _id(f"cat:{name}")
        cats[name] = cid
        db.add(
            Category(
                id=cid,
                tenant_id=tenant_id,
                branch_id=branch_id,
                name=name,
                sort_order=i,
                is_active=True,
            )
        )
    db.flush()

    # ── Products ──────────────────────────────────────────────────────────────
    products_data = [
        # (key, category, name, desc, price, prep_min)
        (
            "klasik-waffle",
            "Wafflelar",
            "Klasik Waffle",
            "Altın sarısı waffle, seçtiğiniz sosla servis edilir.",
            75.00,
            8,
        ),
        (
            "nutella-waffle",
            "Wafflelar",
            "Nutella Waffle",
            "Çıtır waffle üzerine bol Nutella ve pudra şekeri.",
            95.00,
            10,
        ),
        (
            "meyveli-waffle",
            "Wafflelar",
            "Meyveli Waffle",
            "Taze mevsim meyveleriyle hazırlanan özel waffle.",
            105.00,
            12,
        ),
        (
            "double-waffle",
            "Wafflelar",
            "Double Waffle",
            "İki kat waffle, iki kat lezzet. Doyurucu porsiyon.",
            120.00,
            15,
        ),
        (
            "cikolata-sosu",
            "Soslar",
            "Çikolata Sosu (Ekstra)",
            "El yapımı sıcak çikolata sosu.",
            15.00,
            None,
        ),
        (
            "cilek-sosu",
            "Soslar",
            "Çilek Sosu (Ekstra)",
            "Taze çilek püresiyle hazırlanan sos.",
            15.00,
            None,
        ),
        (
            "karamel-sos",
            "Soslar",
            "Karamel Sos (Ekstra)",
            "Tereyağlı karamel sos.",
            15.00,
            None,
        ),
        ("cilek-meyve", "Meyveler", "Çilek", "Taze çilek dilim.", 20.00, None),
        ("muz-meyve", "Meyveler", "Muz", "Taze muz dilim.", 15.00, None),
        ("kivi-meyve", "Meyveler", "Kivi", "Taze kivi dilim.", 20.00, None),
        (
            "findik-ezmesi",
            "Süslemeler",
            "Fındık Ezmesi",
            "Çıtır çıtır fındık ezmesi.",
            25.00,
            None,
        ),
        (
            "hindistan-cevizi",
            "Süslemeler",
            "Hindistan Cevizi",
            "Rendelenmiş hindistan cevizi.",
            20.00,
            None,
        ),
        ("renkli-seker", "Süslemeler", "Renkli Şeker", "Renkli küçük şekerler.", 10.00, None),
        ("cay", "İçecekler", "Çay", "Demlik çay.", 20.00, None),
        ("turk-kahvesi", "İçecekler", "Türk Kahvesi", "Geleneksel Türk kahvesi.", 35.00, None),
        ("limonata", "İçecekler", "Limonata", "El yapımı taze limonata.", 45.00, None),
        ("su", "İçecekler", "Su (500ml)", None, 10.00, None),
    ]

    prods: dict[str, tuple[str, float]] = {}  # key → (id, price)
    for key, cat_name, name, desc, price, prep in products_data:
        pid = _id(f"prod:{key}")
        prods[key] = (pid, price)
        db.add(
            Product(
                id=pid,
                tenant_id=tenant_id,
                branch_id=branch_id,
                category_id=cats[cat_name],
                name=name,
                description=desc,
                base_price=price,
                prep_time_minutes=prep,
                is_active=True,
                is_in_stock=True,
            )
        )
    db.flush()

    # ── Modifier groups ───────────────────────────────────────────────────────
    mg_sos_id = _id("mg:sos-secimi")
    db.add(
        ModifierGroup(
            id=mg_sos_id,
            tenant_id=tenant_id,
            branch_id=branch_id,
            name="Sos Seçimi",
            selection_type="single",
            is_required=True,
            min_select=1,
            max_select=1,
            is_active=True,
        )
    )

    mg_meyve_id = _id("mg:meyve-ekle")
    db.add(
        ModifierGroup(
            id=mg_meyve_id,
            tenant_id=tenant_id,
            branch_id=branch_id,
            name="Meyve Ekle",
            selection_type="multiple",
            is_required=False,
            min_select=0,
            max_select=3,
            is_active=True,
        )
    )
    db.flush()

    # Sos options
    sos_options = [
        ("Çikolata Sosu", 0.00),
        ("Çilek Sosu", 0.00),
        ("Karamel Sos", 0.00),
        ("Sade", 0.00),
    ]
    sos_option_ids: dict[str, str] = {}
    for i, (name, extra) in enumerate(sos_options):
        oid = _id(f"mo:sos:{name}")
        sos_option_ids[name] = oid
        db.add(
            ModifierOption(
                id=oid,
                modifier_group_id=mg_sos_id,
                name=name,
                extra_price=extra,
                sort_order=i,
                is_active=True,
            )
        )

    # Meyve options
    meyve_options = [
        ("Çilek", 20.00),
        ("Muz", 15.00),
        ("Kivi", 20.00),
        ("Şeftali", 20.00),
    ]
    meyve_option_ids: dict[str, str] = {}
    for i, (name, extra) in enumerate(meyve_options):
        oid = _id(f"mo:meyve:{name}")
        meyve_option_ids[name] = oid
        db.add(
            ModifierOption(
                id=oid,
                modifier_group_id=mg_meyve_id,
                name=name,
                extra_price=extra,
                sort_order=i,
                is_active=True,
            )
        )
    db.flush()

    # Link modifier groups to waffle products
    waffle_keys = ["klasik-waffle", "nutella-waffle", "meyveli-waffle", "double-waffle"]
    for wk in waffle_keys:
        pid = prods[wk][0]
        db.add(
            ProductModifierGroup(
                id=_id(f"pmg:{wk}:sos"),
                product_id=pid,
                modifier_group_id=mg_sos_id,
            )
        )
        db.add(
            ProductModifierGroup(
                id=_id(f"pmg:{wk}:meyve"),
                product_id=pid,
                modifier_group_id=mg_meyve_id,
            )
        )
    db.flush()

    # ── Orders ────────────────────────────────────────────────────────────────
    # (order_num, days_ago, hour, table, order_type, status, items)
    # items: list of (prod_key, qty, modifier_name_or_None)
    orders_plan = [
        (
            1, 7, 11, "3", "dine_in", "delivered",
            [("klasik-waffle", 2, "Çikolata Sosu"), ("cay", 2, None)],
        ),
        (
            2, 6, 14, "5", "dine_in", "delivered",
            [("nutella-waffle", 1, "Sade"), ("limonata", 1, None)],
        ),
        (
            3, 5, 13, "1", "dine_in", "delivered",
            [
                ("double-waffle", 2, "Karamel Sos"),
                ("meyveli-waffle", 1, "Çilek Sosu"),
                ("turk-kahvesi", 3, None),
            ],
        ),
        (
            4, 4, 16, "7", "dine_in", "delivered",
            [("klasik-waffle", 1, "Çilek Sosu"), ("su", 2, None)],
        ),
        (
            5, 3, 12, "2", "dine_in", "delivered",
            [
                ("nutella-waffle", 2, "Sade"),
                ("double-waffle", 1, "Çikolata Sosu"),
                ("limonata", 2, None),
            ],
        ),
        (
            6, 2, 15, "4", "dine_in", "delivered",
            [("meyveli-waffle", 2, "Karamel Sos"), ("cay", 4, None)],
        ),
        (
            7, 2, 18, "6", "dine_in", "cancelled",
            [("klasik-waffle", 1, "Sade")],
        ),
        (
            8, 1, 13, "3", "dine_in", "delivered",
            [("double-waffle", 1, "Çikolata Sosu"), ("turk-kahvesi", 1, None)],
        ),
        (
            9, 0, 10, "2", "dine_in", "preparing",
            [("nutella-waffle", 2, "Sade"), ("limonata", 1, None)],
        ),
        (
            10, 0, 11, "8", "dine_in", "pending",
            [("klasik-waffle", 1, "Çilek Sosu"), ("cay", 2, None)],
        ),
    ]

    for order_num, days_ago, hour, table, otype, status, items in orders_plan:
        placed = _dt(days_ago, hour)

        subtotal = 0.0
        item_rows = []
        for prod_key, qty, mod_name in items:
            pid, unit_price = prods[prod_key]
            line = unit_price * qty
            subtotal += line
            item_rows.append((prod_key, pid, unit_price, qty, line, mod_name))

        order_id = _id(f"order:{order_num}")
        order = Order(
            id=order_id,
            tenant_id=tenant_id,
            branch_id=branch_id,
            order_number=order_num,
            order_type=otype,
            status=status,
            table_number=table,
            subtotal=subtotal,
            total_amount=subtotal,
            currency="TRY",
            placed_at=placed,
            completed_at=placed + timedelta(minutes=20) if status == "delivered" else None,
            cancelled_at=placed + timedelta(minutes=5) if status == "cancelled" else None,
        )
        db.add(order)
        db.flush()

        for prod_key, pid, unit_price, qty, line, mod_name in item_rows:
            item_id = _id(f"oi:{order_num}:{prod_key}")
            # Snapshot the product name from products_data
            prod_name = next(p[2] for p in products_data if p[0] == prod_key)
            db.add(
                OrderItem(
                    id=item_id,
                    order_id=order_id,
                    product_id=pid,
                    product_name_snapshot=prod_name,
                    unit_price=unit_price,
                    quantity=qty,
                    line_total=line,
                )
            )
            db.flush()

            if mod_name and prod_key in waffle_keys:
                mo_id = sos_option_ids.get(mod_name)
                if mo_id:
                    db.add(
                        OrderItemModifier(
                            id=_id(f"oim:{order_num}:{prod_key}:{mod_name}"),
                            order_item_id=item_id,
                            modifier_option_id=mo_id,
                            modifier_name_snapshot=mod_name,
                            extra_price=0.00,
                        )
                    )
                    db.flush()

    db.commit()
    print("Demo seed complete.")
    print()
    print("  Tenant slug : waffle-kosesi")
    print("  Admin login : demo@orderiq.app / demo1234")
    print("  Kitchen     : kitchen@orderiq.app / demo1234")
    print("  Menu URL    : http://localhost:3000/m/waffle-kosesi  (once web is ready)")
    print("  Public API  : http://localhost:8000/public/menu/waffle-kosesi")
