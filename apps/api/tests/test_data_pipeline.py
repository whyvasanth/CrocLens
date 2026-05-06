from app.services.data_pipeline import list_data_providers, run_sample_market_ingestion


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
