from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ingestion.raw_inventory import get_project_root, list_supported_data_files


@dataclass(frozen=True)
class SourceTableConfig:
    """Configuration for one source-aligned Silver table."""

    logical_name: str
    source_filename: str
    datetime_columns: tuple[str, ...] = ()
    numeric_columns: tuple[str, ...] = ()
    silver_v1: bool = True
    notes: str = ""


SOURCE_TABLES: tuple[SourceTableConfig, ...] = (
    SourceTableConfig(
        logical_name="orders",
        source_filename="olist_orders_dataset.csv",
        datetime_columns=(
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ),
        notes="Order header grain: one row per order_id in the raw source.",
    ),
    SourceTableConfig(
        logical_name="order_items",
        source_filename="olist_order_items_dataset.csv",
        datetime_columns=("shipping_limit_date",),
        numeric_columns=("order_item_id", "price", "freight_value"),
        notes="Order item grain: one row per order_id and order_item_id.",
    ),
    SourceTableConfig(
        logical_name="order_payments",
        source_filename="olist_order_payments_dataset.csv",
        numeric_columns=("payment_sequential", "payment_installments", "payment_value"),
        notes="Payment event grain: one row per order payment sequence.",
    ),
    SourceTableConfig(
        logical_name="products",
        source_filename="olist_products_dataset.csv",
        numeric_columns=(
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ),
        notes="Product grain: one row per product_id in the raw source.",
    ),
    SourceTableConfig(
        logical_name="product_category_name_translation",
        source_filename="product_category_name_translation.csv",
        notes="Category translation grain: one row per product_category_name.",
    ),
    SourceTableConfig(
        logical_name="customers",
        source_filename="olist_customers_dataset.csv",
        numeric_columns=("customer_zip_code_prefix",),
        notes="Customer order identity grain: one row per customer_id.",
    ),
    SourceTableConfig(
        logical_name="sellers",
        source_filename="olist_sellers_dataset.csv",
        numeric_columns=("seller_zip_code_prefix",),
        notes="Seller grain: one row per seller_id.",
    ),
    SourceTableConfig(
        logical_name="order_reviews",
        source_filename="olist_order_reviews_dataset.csv",
        datetime_columns=("review_creation_date", "review_answer_timestamp"),
        numeric_columns=("review_score",),
        silver_v1=False,
        notes="Deferred from Silver v1 to keep the first business layer focused on sales and revenue.",
    ),
    SourceTableConfig(
        logical_name="geolocation",
        source_filename="olist_geolocation_dataset.csv",
        numeric_columns=("geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng"),
        silver_v1=False,
        notes="Deferred from Silver v1 because it is large and needs geography-specific deduplication decisions.",
    ),
)


def get_silver_tables_dir() -> Path:
    """Return the directory for source-aligned Silver table artifacts."""
    return get_project_root() / "data" / "silver" / "tables"


def get_silver_metadata_dir() -> Path:
    """Return the directory for Silver metadata artifacts."""
    return get_project_root() / "data" / "silver" / "metadata"


def get_silver_v1_configs() -> list[SourceTableConfig]:
    """Return source table configs included in Silver v1."""
    return [config for config in SOURCE_TABLES if config.silver_v1]


def discover_source_registry() -> dict[str, Path]:
    """
    Map logical table names to discovered raw source files.

    The registry is resolved from the landed raw files so the pipeline does not
    depend on unverified paths.
    """
    supported_files = {path.name: path for path in list_supported_data_files()}
    registry: dict[str, Path] = {}

    for config in get_silver_v1_configs():
        source_path = supported_files.get(config.source_filename)
        if source_path is not None:
            registry[config.logical_name] = source_path

    return registry


def get_config_by_logical_name(logical_name: str) -> SourceTableConfig:
    """Return the source table config for a logical table name."""
    for config in SOURCE_TABLES:
        if config.logical_name == logical_name:
            return config

    raise KeyError(f"Unknown source table config: {logical_name}")
