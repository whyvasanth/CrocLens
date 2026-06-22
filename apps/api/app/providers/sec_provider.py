from __future__ import annotations

from datetime import date
from typing import Any

import httpx

from app.providers.base import BaseProvider, ProviderRuntimeConfig
from app.providers.exceptions import ProviderInvalidSymbolError, ProviderMalformedResponseError, ProviderUnavailableError
from app.providers.models import CompanyProfile, FilingSummary, utc_now

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"


class SecProvider(BaseProvider):
    name = "sec_edgar"
    display_name = "SEC EDGAR"
    capabilities = ("profile", "sec_filings")

    def __init__(
        self,
        *,
        enabled: bool,
        user_agent: str,
        config: ProviderRuntimeConfig,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.user_agent = user_agent.strip()
        super().__init__(
            enabled=enabled,
            configured=bool(self.user_agent),
            config=config,
            data_limitations=[
                "SEC EDGAR is official for filings, not market prices.",
                "SEC requests require a descriptive User-Agent identifying the application/contact.",
                "Company filing data may lag company events and should be used as research context.",
            ],
        )
        self._client = client

    async def get_profile(self, symbol: str) -> CompanyProfile:
        normalized_symbol = _normalize_symbol(symbol)
        cache_key = f"sec_profile:{normalized_symbol}"
        cached = self.cache.get(cache_key)
        if isinstance(cached, CompanyProfile):
            return cached

        self._ensure_available()
        company = await self._resolve_company(normalized_symbol)
        retrieved_at = utc_now()
        profile = CompanyProfile(
            provider_name=self.name,
            provider_status="healthy",
            symbol=normalized_symbol,
            company_name=company["title"],
            exchange=None,
            sector=None,
            industry=None,
            website=None,
            data_as_of=retrieved_at,
            retrieved_at=retrieved_at,
            is_stale=False,
            is_sample_data=False,
            data_quality="delayed",
            confidence="high",
            source_url=SEC_TICKERS_URL,
            data_limitations=self.data_limitations,
            raw_payload={"cik": company["cik"], "ticker": normalized_symbol, "title": company["title"]},
        )
        self.cache.set(cache_key, profile)
        self._record_success()
        return profile

    async def get_filings(self, symbol: str) -> list[FilingSummary]:
        normalized_symbol = _normalize_symbol(symbol)
        cache_key = f"sec_filings:{normalized_symbol}"
        cached = self.cache.get(cache_key)
        if isinstance(cached, list) and all(isinstance(item, FilingSummary) for item in cached):
            return cached

        self._ensure_available()
        company = await self._resolve_company(normalized_symbol)
        cik = str(company["cik"]).zfill(10)
        payload = await self._get_json(SEC_SUBMISSIONS_URL.format(cik=cik))
        recent = payload.get("filings", {}).get("recent", {})
        forms = recent.get("form")
        filing_dates = recent.get("filingDate")
        accession_numbers = recent.get("accessionNumber")
        if not isinstance(forms, list) or not isinstance(filing_dates, list) or not isinstance(accession_numbers, list):
            raise ProviderMalformedResponseError(f"SEC submissions response for {normalized_symbol} was malformed.")

        retrieved_at = utc_now()
        filings = []
        for form, filing_date, accession_number in zip(forms[:10], filing_dates[:10], accession_numbers[:10], strict=False):
            parsed_date = _date_from_any(filing_date)
            accession_compact = str(accession_number).replace("-", "")
            filings.append(
                FilingSummary(
                    provider_name=self.name,
                    provider_status="healthy",
                    symbol=normalized_symbol,
                    cik=cik,
                    filing_type=str(form),
                    filing_date=parsed_date,
                    accession_number=str(accession_number),
                    filing_url=(
                        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_compact}/"
                        f"{str(accession_number)}-index.html"
                    ),
                    data_as_of=retrieved_at,
                    retrieved_at=retrieved_at,
                    is_stale=False,
                    is_sample_data=False,
                    data_quality="delayed",
                    confidence="high",
                    source_url=SEC_SUBMISSIONS_URL.format(cik=cik),
                    data_limitations=self.data_limitations,
                )
            )

        self.cache.set(cache_key, filings)
        self._record_success()
        return filings

    async def _resolve_company(self, symbol: str) -> dict[str, str]:
        cached = self.cache.get("sec_company_tickers")
        if isinstance(cached, dict):
            company = cached.get(symbol)
            if company:
                return company

        payload = await self._get_json(SEC_TICKERS_URL)
        mapping: dict[str, dict[str, str]] = {}
        for company in payload.values():
            if not isinstance(company, dict):
                continue
            ticker = str(company.get("ticker") or "").upper()
            title = str(company.get("title") or "").strip()
            cik = company.get("cik_str")
            if ticker and title and cik is not None:
                mapping[ticker] = {"ticker": ticker, "title": title, "cik": str(cik)}
        self.cache.set("sec_company_tickers", mapping)
        if symbol not in mapping:
            raise ProviderInvalidSymbolError(f"SEC ticker mapping did not include {symbol}.")
        return mapping[symbol]

    async def _get_json(self, url: str) -> dict[str, Any]:
        headers = {"User-Agent": self.user_agent, "Accept-Encoding": "gzip, deflate", "Host": _host_from_url(url)}
        try:
            if self._client is not None:
                response = await self._client.get(url, headers=headers)
            else:
                async with httpx.AsyncClient(timeout=self.config.timeout_seconds, headers=headers) as client:
                    response = await client.get(url)
        except httpx.TimeoutException as exc:
            self._record_error("provider_timeout", "SEC request timed out.")
            raise ProviderUnavailableError("SEC request timed out.") from exc
        except httpx.HTTPError as exc:
            self._record_error("provider_unavailable", str(exc))
            raise ProviderUnavailableError("SEC request failed.") from exc

        if response.status_code >= 400:
            self._record_error("provider_unavailable", f"SEC returned HTTP {response.status_code}.")
            raise ProviderUnavailableError(f"SEC returned HTTP {response.status_code}.")
        return response.json()


def _normalize_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not normalized or len(normalized) > 12 or not normalized.replace("-", "").replace(".", "").isalnum():
        raise ProviderInvalidSymbolError("SEC symbol must be a ticker-like value.")
    return normalized


def _date_from_any(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def _host_from_url(url: str) -> str:
    if "data.sec.gov" in url:
        return "data.sec.gov"
    return "www.sec.gov"
