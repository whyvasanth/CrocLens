from pathlib import Path

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


class DataPipelineError(RuntimeError):
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
            id="treasury_fiscal_data",
            name="Treasury/Fiscal Data",
            provider_type="free_api",
            asset_classes=["treasury"],
            authentication="None for many public endpoints.",
            cost_model="Free official US government data source.",
            current_use="Planned future Treasury rates and bond context ingestion.",
            notes=[
                "Good fit for rates and Treasury context.",
                "Production use should still cache responses and handle provider downtime.",
            ],
        ),
        DataProviderResponse(
            id="fhfa_housing",
            name="FHFA public housing data",
            provider_type="free_api",
            asset_classes=["real_estate"],
            authentication="None for public datasets.",
            cost_model="Free official US government housing data source.",
            current_use="Planned future real estate context ingestion.",
            notes=[
                "Useful for broad housing market context.",
                "Not a replacement for a property appraisal or local real estate valuation.",
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
