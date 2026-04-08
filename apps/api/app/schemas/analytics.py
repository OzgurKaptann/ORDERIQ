from pydantic import BaseModel


class AnalyticsSummaryResponse(BaseModel):
    today_order_count: int
    today_revenue: float
    average_basket_value: float


class TopProductEntry(BaseModel):
    product_name: str
    total_quantity: int


class TopProductsResponse(BaseModel):
    products: list[TopProductEntry]


class HourlyOrderEntry(BaseModel):
    hour: int        # 0–23
    order_count: int


class HourlyOrdersResponse(BaseModel):
    distribution: list[HourlyOrderEntry]
