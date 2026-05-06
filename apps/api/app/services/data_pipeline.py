from datetime import UTC, datetime
from pathlib import Path

import httpx
from pydantic import ValidationError

from app.schemas.api import (
    DataFreshnessReport,
    DataProviderResponse,
    DataQualityIssue,
    MarketDataIngestionResponse,
    MarketObservation,
    SampleMarketDataFile,
    SourceMetadata,
)
from app.services.mock_data import EDUCATIONAL_DISCLAIMER

SAMPLE_MARKET_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_market_data.json"
COINGECKO_SIMPLE_PRICE_URL = "https://api.coingecko.com/api/v3/simple/price"


class DataPipelineError(RuntimeError):
    pass


class DataPipelineProviderError(DataPipelineError):
    pass


def list_data_providers() -> list[DataProviderResponse]:
    return [
        DataProviderResponse(
            id="croclens_sample_market_file",
            name="CrocLens sample market file",
            provider_type="sample_file",
            asset_classes=["stock", "crypto", "treasury", "macro", "real_estate"],
            authentication="None",
            cost_model="Free local development fixture",
            current_use="Used in Phase 11 for repeatable ETL tests.",
            notes=[
                "Best for deterministic local development.",
                "Does not represent live market data.",
            ],
        ),
        DataProviderResponse(
            id="coingecko_simple_price",
            name="CoinGecko Simple Price API",
            provider_type="free_api",
            asset_classes=["crypto"],
            authentication="No API key required for the basic public endpoint.",
            cost_model="Free public API with rate limits.",
            current_use="Optional live Bitcoin preview endpoint; not required for tests.",
            notes=[
                "Good first free API because it avoids secrets in the MVP.",
                "Production use should cache responses and handle rate limits.",
            ],
        ),
        DataProviderResponse(
            id="fred_macro",
            name="FRED",
            provider_type="free_api",
            asset_classes=["macro", "treasury"],
            authentication="Free API key required.",
            cost_model="Free with usage rules.",
            current_use="Planned future macro and rates ingestion.",
            notes=[
                "Strong source for inflation, rates, employment, and economic time series.",
                "Requires key management before production use.",
            ],
        ),
        DataProviderResponse(
            id="alpha_vantage_equities",
            name="Alpha Vantage or similar market data API",
            provider_type="free_api",
            asset_classes=["stock", "etf"],
            authentication="Free API key usually required.",
            cost_model="Free tier with strict limits; paid tiers optional later.",
            current_use="Planned future stocks and ETFs ingestion.",
            notes=[
                "Useful for MVP stock price prototypes.",
                "Rate limits mean caching is required.",
            ],
        ),
    ]


def run_sample_market_ingestion() -> MarketDataIngestionResponse:
    dataset = _load_sample_market_data()
    issues = _quality_check_records(dataset.records)
    status = "completed_with_warnings" if any(issue.severity != "info" for issue in issues) else "completed"
    source = SourceMetadata(
        name=dataset.source_name,
        freshness="Sample data loaded from local JSON fixture",
        as_of=dataset.as_of.isoformat(),
    )

    return MarketDataIngestionResponse(
        pipeline_name="sample_market_data_ingestion",
        dataset_id=dataset.dataset_id,
        provider=list_data_providers()[0],
        status=status,
        extracted_count=len(dataset.records),
        accepted_count=len(dataset.records),
        rejected_count=0,
        freshness_report=DataFreshnessReport(
            status="sample",
            as_of=dataset.as_of,
            retrieved_at=dataset.retrieved_at,
            explanation="This Phase 11 pipeline uses deterministic sample data so tests and UI work are repeatable.",
        ),
        quality_issues=issues,
        records=dataset.records,
        confidence="medium",
        data_limitations=[
            "The sample file is synthetic and should not be used for investment decisions.",
            "Records are not persisted to PostgreSQL yet.",
            "Scheduling, retries, and cache storage are documented but not automated yet.",
        ],
        sources=[source],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def get_latest_market_observations() -> list[MarketObservation]:
    return run_sample_market_ingestion().records


def fetch_coingecko_bitcoin_observation() -> MarketObservation:
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_last_updated_at": "true",
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(COINGECKO_SIMPLE_PRICE_URL, params=params)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise DataPipelineProviderError(f"CoinGecko request failed: {exc}") from exc

    return normalize_coingecko_bitcoin_response(response.json())


def normalize_coingecko_bitcoin_response(payload: dict) -> MarketObservation:
    bitcoin = payload.get("bitcoin")
    if not isinstance(bitcoin, dict):
        raise DataPipelineProviderError("CoinGecko response did not include a bitcoin object.")

    usd_price = bitcoin.get("usd")
    if usd_price is None:
        raise DataPipelineProviderError("CoinGecko response did not include a USD price.")

    change_percent = bitcoin.get("usd_24h_change")
    last_updated_at = bitcoin.get("last_updated_at")
    as_of = (
        datetime.fromtimestamp(last_updated_at, tz=UTC)
        if isinstance(last_updated_at, int | float)
        else datetime.now(tz=UTC)
    )
    retrieved_at = datetime.now(tz=UTC)

    return MarketObservation(
        symbol="BTC",
        name="Bitcoin",
        asset_class="crypto",
        metric_type="price",
        value=float(usd_price),
        unit="USD",
        currency="USD",
        change_percent=float(change_percent) if change_percent is not None else None,
        trend=_trend_from_change(change_percent),
        as_of=as_of,
        retrieved_at=retrieved_at,
        source=SourceMetadata(
            name="CoinGecko",
            freshness="Live free API preview when this endpoint was called",
            as_of=as_of.isoformat(),
        ),
        source_url=COINGECKO_SIMPLE_PRICE_URL,
        data_limitations=[
            "Free public API responses can be rate limited or temporarily unavailable.",
            "This preview is not cached or persisted yet.",
            "Crypto prices can move quickly; review source freshness before relying on a value.",
        ],
    )


def _load_sample_market_data(path: Path = SAMPLE_MARKET_DATA_PATH) -> SampleMarketDataFile:
    try:
        return SampleMarketDataFile.model_validate_json(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DataPipelineError(f"Sample market data file was not found: {path}") from exc
    except ValidationError as exc:
        raise DataPipelineError(f"Sample market data failed validation: {exc}") from exc


def _quality_check_records(records: list[MarketObservation]) -> list[DataQualityIssue]:
    issues: list[DataQualityIssue] = []
    seen_keys: set[tuple[str, str, str]] = set()

    for record in records:
        key = (record.symbol.upper(), record.metric_type, record.as_of.date().isoformat())
        if key in seen_keys:
            issues.append(
                DataQualityIssue(
                    severity="warning",
                    code="duplicate_observation",
                    record_symbol=record.symbol,
                    message="Duplicate symbol, metric, and date combination found in the sample dataset.",
                )
            )
        seen_keys.add(key)

        if record.value == 0:
            issues.append(
                DataQualityIssue(
                    severity="warning",
                    code="zero_value",
                    record_symbol=record.symbol,
                    message="A zero value may be valid for some metrics, but it should be reviewed.",
                )
            )

        if not record.data_limitations:
            issues.append(
                DataQualityIssue(
                    severity="warning",
                    code="missing_limitations",
                    record_symbol=record.symbol,
                    message="Each market observation should explain its limitations.",
                )
            )

    if not issues:
        issues.append(
            DataQualityIssue(
                severity="info",
                code="quality_checks_passed",
                message="All sample records passed required validation and basic quality checks.",
            )
        )

    return issues


def _trend_from_change(change_percent: float | int | None) -> str:
    if change_percent is None:
        return "flat"
    if change_percent > 0:
        return "up"
    if change_percent < 0:
        return "down"
    return "flat"
