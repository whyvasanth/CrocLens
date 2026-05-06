from app.services.data_pipeline import normalize_coingecko_bitcoin_response, run_sample_market_ingestion


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


def test_coingecko_normalizer_returns_market_observation() -> None:
    observation = normalize_coingecko_bitcoin_response(
        {
            "bitcoin": {
                "usd": 66123.45,
                "usd_24h_change": -1.25,
                "last_updated_at": 1714939200,
            }
        }
    )

    assert observation.symbol == "BTC"
    assert observation.asset_class == "crypto"
    assert observation.metric_type == "price"
    assert observation.value == 66123.45
    assert observation.trend == "down"
    assert observation.source.name == "CoinGecko"
    assert observation.data_limitations
