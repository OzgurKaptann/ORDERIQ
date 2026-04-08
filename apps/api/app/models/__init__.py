# Import all models so that Alembic autogenerate picks them up
from app.models.tenant import Tenant, Branch  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.catalog import Category, Product, ProductTag  # noqa: F401
from app.models.modifier import ModifierGroup, ModifierOption, ProductModifierGroup  # noqa: F401
from app.models.order import Order, OrderItem, OrderItemModifier  # noqa: F401
from app.models.qr_code import QRCode  # noqa: F401
from app.models.settings import BusinessSettings  # noqa: F401
from app.models.event_log import EventLog  # noqa: F401
