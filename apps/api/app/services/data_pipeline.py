from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

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
TREASURY_YIELD_CURVE_URL_TEMPLATE = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml"
    "?data=daily_treasury_yield_curve&field_tdr_date_value={year}"
)
TREASURY_USER_AGENT = "CrocLens educational local app; no paid data provider; contact local@example.com"
ATOM_NS = "{http://www.w3.org/2005/Atom}"
DATA_NS = "{http://schemas.microsoft.com/ado/2007/08/dataservices}"
METADATA_NS = "{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}"
TREASURY_FIELDS = [
    ("US3M", "3-Month Treasury Yield", "BC_3MONTH"),
    ("US2Y", "2-Year Treasury Yield", "BC_2YEAR"),
    ("US10Y", "10-Year Treasury Yield", "BC_10YEAR"),
    ("US30Y", "30-Year Treasury Yield", "BC_30YEAR"),
]


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
            current_use="Used for real-data v1 Treasury yield curve ingestion.",
            notes=[
                "Official no-key public Treasury source.",
                "Used for Treasury rate context, not stock or crypto prices.",
                "Production use should cache responses and handle provider downtime.",
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


def run_treasury_yield_curve_ingestion(
    fetch_xml: Callable[[int], str] | None = None,
    now: datetime | None = None,
) -> MarketDataIngestionResponse:
    retrieved_at = now or datetime.now(tz=UTC)
    fetcher = fetch_xml or _fetch_treasury_yield_curve_xml
    year = retrieved_at.year
    xml_text = fetcher(year)
    rows = _parse_treasury_yield_curve_xml(xml_text)

    if not rows:
        raise DataPipelineError("Treasury yield curve feed returned no rows.")

    rows = sorted(rows, key=lambda row: row["date"])
    latest = rows[-1]
    previous = rows[-2] if len(rows) >= 2 else None
    source_url = TREASURY_YIELD_CURVE_URL_TEMPLATE.format(year=year)
    source = SourceMetadata(
        name="U.S. Treasury Daily Treasury Par Yield Curve Rates",
        freshness="Live public XML feed from home.treasury.gov",
        as_of=latest["date"].isoformat(),
    )

    records: list[MarketObservation] = []
    for symbol, name, field_name in TREASURY_FIELDS:
        value = latest.get(field_name)
        if value is None:
            continue

        previous_value = previous.get(field_name) if previous else None
        change = round(value - previous_value, 2) if previous_value is not None else None
        trend = "flat"
        if change is not None and change > 0:
            trend = "up"
        elif change is not None and change < 0:
            trend = "down"

        records.append(
            MarketObservation(
                symbol=symbol,
                name=name,
                asset_class="treasury",
                metric_type="yield",
                value=value,
                unit="percent",
                currency=None,
                change_percent=change,
                trend=trend,
                as_of=datetime.combine(latest["date"], datetime.min.time(), tzinfo=UTC),
                retrieved_at=retrieved_at,
                source=source,
                source_url=source_url,
                data_limitations=[
                    "Official Treasury yield data is public macro context, not a personalized recommendation.",
                    "This feed does not provide stock, ETF, mutual fund, or crypto prices.",
                    "Rates can update after market hours and should be cached in production.",
                ],
            )
        )

    if not records:
        raise DataPipelineError("Treasury yield curve feed did not include supported maturity fields.")

    issues = _quality_check_records(records)
    days_old = (retrieved_at.date() - latest["date"]).days
    freshness_status = "fresh" if days_old <= 7 else "stale"
    status = "completed_with_warnings" if any(issue.severity != "info" for issue in issues) else "completed"

    return MarketDataIngestionResponse(
        pipeline_name="treasury_yield_curve_live_ingestion",
        dataset_id=f"treasury_yield_curve_{latest['date'].isoformat()}",
        provider=next(provider for provider in list_data_providers() if provider.id == "treasury_fiscal_data"),
        status=status,
        extracted_count=len(rows),
        accepted_count=len(records),
        rejected_count=0,
        freshness_report=DataFreshnessReport(
            status=freshness_status,
            as_of=datetime.combine(latest["date"], datetime.min.time(), tzinfo=UTC),
            retrieved_at=retrieved_at,
            explanation=(
                "Latest daily Treasury yield curve row was loaded from the official public XML feed. "
                "CrocLens treats this as macro context, not investment advice."
            ),
        ),
        quality_issues=issues,
        records=records,
        confidence="high",
        data_limitations=[
            "Only Treasury yield curve rates are live in real-data v1.",
            "Stock, ETF, mutual fund, and crypto prices remain sample data until a verified no-cost source is selected.",
            "No records are persisted to PostgreSQL yet.",
        ],
        sources=[source],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def get_latest_treasury_observations() -> list[MarketObservation]:
    return run_treasury_yield_curve_ingestion().records


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


def _fetch_treasury_yield_curve_xml(year: int) -> str:
    url = TREASURY_YIELD_CURVE_URL_TEMPLATE.format(year=year)
    request = Request(url, headers={"User-Agent": TREASURY_USER_AGENT})

    try:
        with urlopen(request, timeout=20) as response:
            return response.read().decode("utf-8")
    except URLError as exc:
        raise DataPipelineError(f"Treasury yield curve feed could not be reached: {exc}") from exc
    except TimeoutError as exc:
        raise DataPipelineError("Treasury yield curve feed timed out.") from exc


def _parse_treasury_yield_curve_xml(xml_text: str) -> list[dict]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise DataPipelineError("Treasury yield curve feed returned invalid XML.") from exc

    rows: list[dict] = []

    for entry in root.findall(f"{ATOM_NS}entry"):
        properties = entry.find(f"{ATOM_NS}content/{METADATA_NS}properties")
        if properties is None:
            continue

        date_text = _find_treasury_property_text(properties, "NEW_DATE")
        if not date_text:
            continue

        row = {"date": datetime.fromisoformat(date_text).date()}
        for _, _, field_name in TREASURY_FIELDS:
            value_text = _find_treasury_property_text(properties, field_name)
            if value_text:
                row[field_name] = float(value_text)
        rows.append(row)

    return rows


def _find_treasury_property_text(properties: ET.Element, field_name: str) -> str | None:
    element = properties.find(f"{DATA_NS}{field_name}")
    return element.text if element is not None else None
