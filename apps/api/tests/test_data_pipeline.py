from datetime import UTC, datetime

from app.services.data_pipeline import (
    list_data_providers,
    run_sample_market_ingestion,
    run_treasury_yield_curve_ingestion,
)


TREASURY_YIELD_CURVE_XML = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
      xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
  <entry>
    <content type="application/xml">
      <m:properties>
        <d:NEW_DATE>2026-05-05T00:00:00</d:NEW_DATE>
        <d:BC_3MONTH>4.20</d:BC_3MONTH>
        <d:BC_2YEAR>3.85</d:BC_2YEAR>
        <d:BC_10YEAR>4.15</d:BC_10YEAR>
        <d:BC_30YEAR>4.70</d:BC_30YEAR>
      </m:properties>
    </content>
  </entry>
  <entry>
    <content type="application/xml">
      <m:properties>
        <d:NEW_DATE>2026-05-06T00:00:00</d:NEW_DATE>
        <d:BC_3MONTH>4.22</d:BC_3MONTH>
        <d:BC_2YEAR>3.82</d:BC_2YEAR>
        <d:BC_10YEAR>4.18</d:BC_10YEAR>
        <d:BC_30YEAR>4.70</d:BC_30YEAR>
      </m:properties>
    </content>
  </entry>
</feed>
"""


def test_sample_market_ingestion_returns_quality_report() -> None:
    result = run_sample_market_ingestion()

    assert result.status == "completed"
    assert result.dataset_id == "phase11_sample_market_snapshot_2026_05_05"
    assert result.extracted_count == 6
    assert result.accepted_count == 6
    assert result.rejected_count == 0
    assert result.freshness_report.status == "sample"
    assert result.quality_issues[0].code == "quality_checks_passed"
    assert any(record.symbol == "BTC" for record in result.records)
    assert "not financial advice" in result.educational_disclaimer


def test_provider_registry_uses_only_free_first_sources() -> None:
    providers = list_data_providers()
    provider_ids = {provider.id for provider in providers}

    assert provider_ids == {"croclens_sample_market_file", "fred_macro", "treasury_fiscal_data", "fhfa_housing"}
    assert {provider.provider_type for provider in providers}.issubset({"sample_file", "free_api"})
    assert any(provider.id == "treasury_fiscal_data" for provider in providers)


def test_treasury_yield_curve_ingestion_normalizes_official_xml() -> None:
    result = run_treasury_yield_curve_ingestion(
        fetch_xml=lambda year: TREASURY_YIELD_CURVE_XML,
        now=datetime(2026, 5, 7, 12, 0, tzinfo=UTC),
    )

    assert result.pipeline_name == "treasury_yield_curve_live_ingestion"
    assert result.dataset_id == "treasury_yield_curve_2026-05-06"
    assert result.provider.id == "treasury_fiscal_data"
    assert result.status == "completed"
    assert result.extracted_count == 2
    assert result.accepted_count == 4
    assert result.rejected_count == 0
    assert result.freshness_report.status == "fresh"
    assert result.confidence == "high"
    assert "not financial advice" in result.educational_disclaimer
    assert any("Only Treasury yield curve rates are live" in limitation for limitation in result.data_limitations)
    assert any("Stock, ETF, mutual fund, and crypto prices remain sample data" in limitation for limitation in result.data_limitations)

    records_by_symbol = {record.symbol: record for record in result.records}
    assert set(records_by_symbol) == {"US3M", "US2Y", "US10Y", "US30Y"}

    ten_year = records_by_symbol["US10Y"]
    assert ten_year.name == "10-Year Treasury Yield"
    assert ten_year.asset_class == "treasury"
    assert ten_year.metric_type == "yield"
    assert ten_year.value == 4.18
    assert ten_year.unit == "percent"
    assert ten_year.change_percent == 0.03
    assert ten_year.trend == "up"
    assert ten_year.source.name == "U.S. Treasury Daily Treasury Par Yield Curve Rates"
    assert ten_year.source_url is not None
    assert "home.treasury.gov" in ten_year.source_url

    two_year = records_by_symbol["US2Y"]
    assert two_year.change_percent == -0.03
    assert two_year.trend == "down"

    thirty_year = records_by_symbol["US30Y"]
    assert thirty_year.change_percent == 0
    assert thirty_year.trend == "flat"
