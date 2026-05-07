from fastapi import APIRouter, HTTPException, status

from app.schemas.api import DataProviderResponse, MarketDataIngestionResponse, MarketObservation
from app.services.data_pipeline import (
    DataPipelineError,
    get_latest_market_observations,
    get_latest_treasury_observations,
    list_data_providers,
    run_sample_market_ingestion,
    run_treasury_yield_curve_ingestion,
)

router = APIRouter(prefix="/data-pipeline", tags=["data-pipeline"])


@router.get("/providers", response_model=list[DataProviderResponse])
def read_data_providers() -> list[DataProviderResponse]:
    return list_data_providers()


@router.post("/market-data/sample-ingest", response_model=MarketDataIngestionResponse)
def ingest_sample_market_data() -> MarketDataIngestionResponse:
    try:
        return run_sample_market_ingestion()
    except DataPipelineError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get("/market-data/latest", response_model=list[MarketObservation])
def read_latest_market_data() -> list[MarketObservation]:
    try:
        return get_latest_market_observations()
    except DataPipelineError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.post("/market-data/treasury-ingest", response_model=MarketDataIngestionResponse)
def ingest_treasury_market_data() -> MarketDataIngestionResponse:
    try:
        return run_treasury_yield_curve_ingestion()
    except DataPipelineError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get("/market-data/treasury-latest", response_model=list[MarketObservation])
def read_latest_treasury_market_data() -> list[MarketObservation]:
    try:
        return get_latest_treasury_observations()
    except DataPipelineError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
