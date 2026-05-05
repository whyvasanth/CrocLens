from app.schemas.api import (
    ActionPlanItem,
    ActionPlanResponse,
    AssetDetailCard,
    AssetDetailMetric,
    AssetDetailResponse,
    AssetResponse,
    PortfolioSummaryResponse,
    SourceMetadata,
)
from app.services.portfolio_calculations import (
    AssetPosition,
    LiabilityPosition,
    calculate_portfolio_summary,
)

MOCK_SOURCE = SourceMetadata(
    name="CrocLens sample data",
    freshness="Calculated from Phase 6 sample positions",
    as_of="2026-05-05",
)

EDUCATIONAL_DISCLAIMER = "This is educational information, not financial advice."


def get_portfolio_summary() -> PortfolioSummaryResponse:
    calculation = calculate_portfolio_summary(
        assets=get_sample_asset_positions(),
        liabilities=get_sample_liability_positions(),
    )

    return PortfolioSummaryResponse(
        user_name="Maya",
        total_assets=calculation.total_assets,
        total_liabilities=calculation.total_liabilities,
        net_worth=calculation.net_worth,
        allocation=calculation.allocation,
        debt_impact=calculation.debt_impact,
        scores=calculation.scores,
        sources=[MOCK_SOURCE],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def get_sample_asset_positions() -> list[AssetPosition]:
    return [
        AssetPosition(asset_class="Stocks", market_value=95_526),
        AssetPosition(asset_class="ETFs", market_value=79_056),
        AssetPosition(asset_class="Real Estate", market_value=72_468),
        AssetPosition(asset_class="Retirement", market_value=42_822),
        AssetPosition(asset_class="Cash", market_value=23_058),
        AssetPosition(asset_class="Crypto", market_value=16_470),
    ]


def get_sample_liability_positions() -> list[LiabilityPosition]:
    return [
        LiabilityPosition(liability_type="Mortgage", balance=106_000, interest_rate=0.061),
        LiabilityPosition(liability_type="Student loan", balance=6_100, interest_rate=0.045),
        LiabilityPosition(liability_type="Credit card", balance=2_500, interest_rate=0.199),
    ]


def list_assets() -> list[AssetResponse]:
    return [
        AssetResponse(
            id="asset_stock_bucket",
            symbol="STOCKS",
            name="Stock holdings",
            asset_type="Stocks",
            current_price=None,
            market_value=95_526,
            allocation_percent=29,
            risk_level="medium",
            beginner_explanation="Stocks represent ownership in companies and can move up and down with markets.",
            source=MOCK_SOURCE,
        ),
        AssetResponse(
            id="asset_etf_bucket",
            symbol="ETFS",
            name="ETF holdings",
            asset_type="ETFs",
            current_price=None,
            market_value=79_056,
            allocation_percent=24,
            risk_level="medium",
            beginner_explanation="ETFs are baskets of investments that can make diversification easier.",
            source=MOCK_SOURCE,
        ),
        AssetResponse(
            id="asset_real_estate",
            symbol="HOME",
            name="Real estate equity",
            asset_type="Real Estate",
            current_price=None,
            market_value=72_468,
            allocation_percent=22,
            risk_level="medium",
            beginner_explanation="Real estate can build equity but is usually less liquid than public investments.",
            source=MOCK_SOURCE,
        ),
        AssetResponse(
            id="asset_retirement",
            symbol="401K",
            name="Retirement accounts",
            asset_type="Retirement",
            current_price=None,
            market_value=42_822,
            allocation_percent=13,
            risk_level="medium",
            beginner_explanation="Retirement accounts are long-term accounts with tax rules and contribution limits.",
            source=MOCK_SOURCE,
        ),
        AssetResponse(
            id="asset_btc",
            symbol="BTC",
            name="Bitcoin",
            asset_type="Crypto",
            current_price=66_421.35,
            market_value=16_470,
            allocation_percent=5.0,
            risk_level="high",
            beginner_explanation="Crypto can move sharply in price, so CrocLens treats it as higher risk.",
            source=MOCK_SOURCE,
        ),
        AssetResponse(
            id="asset_cash",
            symbol="USD",
            name="Cash reserve",
            asset_type="Cash",
            current_price=None,
            market_value=23_058,
            allocation_percent=7.0,
            risk_level="low",
            beginner_explanation="Cash is usually stable and liquid, but inflation can reduce buying power.",
            source=MOCK_SOURCE,
        ),
    ]


def get_asset_by_id(asset_id: str) -> AssetResponse | None:
    return next((asset for asset in list_assets() if asset.id == asset_id), None)


def list_asset_detail_cards() -> list[AssetDetailCard]:
    return [
        AssetDetailCard(
            id=detail.id,
            symbol=detail.symbol,
            name=detail.name,
            category=detail.category,
            asset_type=detail.asset_type,
            current_value=detail.current_value,
            risk_level=detail.risk_level,
            summary=detail.headline,
        )
        for detail in list_asset_details()
    ]


def get_asset_detail_by_id(asset_id: str) -> AssetDetailResponse | None:
    return next((detail for detail in list_asset_details() if detail.id == asset_id), None)


def list_asset_details() -> list[AssetDetailResponse]:
    return [
        AssetDetailResponse(
            id="asset_stock_bucket",
            symbol="STOCKS",
            name="Stock holdings",
            category="stock_etf",
            asset_type="Stocks",
            current_value=95_526,
            allocation_percent=29,
            risk_level="medium",
            portfolio_role="Growth engine for long-term wealth, with prices that can move day to day.",
            headline="Your stock exposure is meaningful, so CrocLens explains both growth potential and volatility.",
            what_this_is="Stocks represent small ownership pieces in public companies. Their prices can rise or fall based on company results, interest rates, investor expectations, and the wider economy.",
            why_it_matters="Stocks can help a portfolio grow over long periods, but they also create short-term ups and downs. Beginners should understand concentration before adding more.",
            risk_explanation="Medium risk in this sample because the stock bucket is diversified, but still exposed to market swings.",
            liquidity_explanation="Public stocks are usually liquid because they can often be sold during market hours, though sale prices are not guaranteed.",
            tax_complexity_explanation="Tax complexity is moderate because selling may create capital gains or losses, and holding period matters.",
            income_potential_explanation="Some stocks pay dividends, but this sample bucket is treated mainly as a growth asset.",
            what_to_watch=[
                "Whether one sector or company becomes too large compared with the rest of your wealth.",
                "How stock exposure compares with your time horizon and comfort with volatility.",
                "Short-term versus long-term holding periods before taxable sales.",
            ],
            beginner_takeaway="Stocks can support growth, but CrocLens wants you to compare them with cash, debt, real estate, and retirement goals before making changes.",
            safe_next_steps=[
                "Consider reviewing whether this bucket is diversified across sectors.",
                "You may want to research how stock volatility has affected your past decisions.",
                "This may be worth discussing with a professional if taxes or concentrated positions are involved.",
            ],
            key_metrics=[
                AssetDetailMetric(
                    label="Current value",
                    value="$95,526",
                    explanation="Sample market value used by the Phase 7 detail page.",
                    tone="green",
                ),
                AssetDetailMetric(
                    label="Portfolio share",
                    value="29%",
                    explanation="A large enough share to influence your overall risk score.",
                    tone="gold",
                ),
                AssetDetailMetric(
                    label="Liquidity",
                    value="High",
                    explanation="Public market assets are usually easier to convert to cash than real estate.",
                    tone="green",
                ),
            ],
            confidence="medium",
            data_limitations=["Uses static sample holdings.", "No live brokerage positions are connected yet."],
            source=MOCK_SOURCE,
            educational_disclaimer=EDUCATIONAL_DISCLAIMER,
        ),
        AssetDetailResponse(
            id="asset_etf_bucket",
            symbol="ETFS",
            name="ETF holdings",
            category="stock_etf",
            asset_type="ETFs",
            current_value=79_056,
            allocation_percent=24,
            risk_level="medium",
            portfolio_role="Diversified market exposure that can reduce single-company risk.",
            headline="Your ETF holdings can make diversification easier, but the underlying mix still matters.",
            what_this_is="An ETF is a basket of investments traded like a stock. One ETF can hold hundreds or thousands of securities.",
            why_it_matters="ETFs can help beginners avoid putting too much weight on one company, but two ETFs can still overlap heavily.",
            risk_explanation="Medium risk because many ETFs hold stocks or bonds whose prices still move with markets.",
            liquidity_explanation="Most large ETFs are liquid during market hours, though smaller funds can have wider trading spreads.",
            tax_complexity_explanation="Tax complexity is usually moderate. Selling ETF shares can create taxable gains or losses.",
            income_potential_explanation="Some ETFs pay dividends or bond interest, depending on what the fund owns.",
            what_to_watch=[
                "Expense ratios, because fees reduce returns over time.",
                "Overlap between ETFs that may make the portfolio less diversified than it appears.",
                "Whether stock, bond, and international exposure match your goals.",
            ],
            beginner_takeaway="ETFs are often beginner-friendly building blocks, but CrocLens still checks cost, overlap, risk, and taxes.",
            safe_next_steps=[
                "Consider reviewing ETF overlap before adding another similar fund.",
                "You may want to research each fund's expense ratio and holdings.",
                "Based on the data provided, review whether ETFs match your time horizon.",
            ],
            key_metrics=[
                AssetDetailMetric(
                    label="Current value",
                    value="$79,056",
                    explanation="Sample ETF market value in this portfolio.",
                    tone="green",
                ),
                AssetDetailMetric(
                    label="Portfolio share",
                    value="24%",
                    explanation="A meaningful part of the total asset base.",
                    tone="gold",
                ),
                AssetDetailMetric(
                    label="Diversification help",
                    value="Strong",
                    explanation="ETFs can spread risk across many holdings when chosen carefully.",
                    tone="green",
                ),
            ],
            confidence="medium",
            data_limitations=["Uses static sample ETFs.", "No fund holdings or expense ratio feed is connected yet."],
            source=MOCK_SOURCE,
            educational_disclaimer=EDUCATIONAL_DISCLAIMER,
        ),
        AssetDetailResponse(
            id="asset_btc",
            symbol="BTC",
            name="Bitcoin",
            category="crypto",
            asset_type="Crypto",
            current_value=16_470,
            allocation_percent=5,
            risk_level="high",
            portfolio_role="Small but volatile satellite position that can move sharply.",
            headline="Bitcoin is a smaller allocation here, but its price swings can still affect how the portfolio feels.",
            what_this_is="Bitcoin is a digital asset that trades globally. It is not a stock, bond, or cash account.",
            why_it_matters="Crypto can move much more sharply than traditional assets, so position size matters for beginners.",
            risk_explanation="High risk because crypto prices can change quickly and may be affected by regulation, liquidity, and sentiment.",
            liquidity_explanation="Bitcoin is usually tradeable, but exchange access, fees, spreads, and custody risks matter.",
            tax_complexity_explanation="Tax complexity can be high because crypto sales, swaps, or payments may create taxable events.",
            income_potential_explanation="Bitcoin itself does not pay dividends or interest in this sample.",
            what_to_watch=[
                "Whether crypto remains a small part of total net worth.",
                "Custody, account security, and exchange reliability.",
                "Tax records for purchases, transfers, and sales.",
            ],
            beginner_takeaway="CrocLens treats crypto as high risk and focuses on size, safety, and tax records rather than hype.",
            safe_next_steps=[
                "Consider reviewing whether the crypto allocation still matches your risk comfort.",
                "You may want to research custody and account security basics.",
                "This could be a risk if tax records are incomplete.",
            ],
            key_metrics=[
                AssetDetailMetric(
                    label="Current value",
                    value="$16,470",
                    explanation="Sample Bitcoin market value in the current portfolio.",
                    tone="green",
                ),
                AssetDetailMetric(
                    label="Portfolio share",
                    value="5%",
                    explanation="Small by allocation, but still high volatility.",
                    tone="gold",
                ),
                AssetDetailMetric(
                    label="Tax complexity",
                    value="High",
                    explanation="Crypto transactions can create extra recordkeeping work.",
                    tone="coral",
                ),
            ],
            confidence="medium",
            data_limitations=["Uses a static sample crypto value.", "No live CoinGecko or exchange data is connected yet."],
            source=MOCK_SOURCE,
            educational_disclaimer=EDUCATIONAL_DISCLAIMER,
        ),
        AssetDetailResponse(
            id="asset_real_estate",
            symbol="HOME",
            name="Real estate equity",
            category="real_estate",
            asset_type="Real Estate",
            current_value=72_468,
            allocation_percent=22,
            risk_level="medium",
            portfolio_role="Home equity can build wealth, but it is less liquid than public investments.",
            headline="Real estate adds inflation sensitivity and stability, but it cannot be accessed as easily as cash.",
            what_this_is="Real estate equity is the estimated property value minus the mortgage balance tied to the property.",
            why_it_matters="For many beginners, real estate is one of the largest parts of net worth and debt exposure at the same time.",
            risk_explanation="Medium risk because property values can change and maintenance costs can surprise owners.",
            liquidity_explanation="Liquidity is low because selling or borrowing against property takes time, paperwork, and fees.",
            tax_complexity_explanation="Tax complexity can be moderate because property taxes, interest, sale rules, and local rules matter.",
            income_potential_explanation="Primary homes usually do not create income unless rented or partially rented.",
            what_to_watch=[
                "Mortgage rate, remaining balance, and monthly payment pressure.",
                "Emergency cash for repairs and insurance changes.",
                "Local housing market trends if a sale or refinance is being considered.",
            ],
            beginner_takeaway="Real estate can help net worth, but CrocLens separates the asset value from the mortgage so debt impact stays visible.",
            safe_next_steps=[
                "Consider reviewing how the mortgage balance affects net worth.",
                "You may want to research local housing trends before making large property decisions.",
                "This may be worth discussing with a professional if refinancing or selling has tax implications.",
            ],
            key_metrics=[
                AssetDetailMetric(
                    label="Estimated equity",
                    value="$72,468",
                    explanation="Sample equity value after considering property and mortgage assumptions.",
                    tone="green",
                ),
                AssetDetailMetric(
                    label="Portfolio share",
                    value="22%",
                    explanation="A large part of net worth that is not quickly spendable.",
                    tone="gold",
                ),
                AssetDetailMetric(
                    label="Liquidity",
                    value="Low",
                    explanation="Property usually takes longer to convert into cash.",
                    tone="coral",
                ),
            ],
            confidence="medium",
            data_limitations=[
                "Uses sample real estate equity.",
                "No live appraisal, mortgage, FHFA, or local listing data is connected yet.",
            ],
            source=MOCK_SOURCE,
            educational_disclaimer=EDUCATIONAL_DISCLAIMER,
        ),
        AssetDetailResponse(
            id="liability_mortgage",
            symbol="MTG",
            name="Mortgage balance",
            category="debt",
            asset_type="Debt",
            current_value=106_000,
            allocation_percent=32,
            risk_level="medium",
            portfolio_role="Major liability that reduces net worth and affects monthly flexibility.",
            headline="The mortgage is the largest sample liability, so CrocLens explains rate, balance, and cash-flow pressure.",
            what_this_is="A mortgage is debt secured by real estate. The balance is money still owed to the lender.",
            why_it_matters="Debt reduces net worth and can limit flexibility, even when it is tied to a valuable home.",
            risk_explanation="Medium risk because the rate and payment are material, but mortgages are usually more structured than credit cards.",
            liquidity_explanation="Debt is not liquid. Paying it down may improve net worth, but it can also reduce available cash.",
            tax_complexity_explanation="Tax complexity depends on local rules and whether mortgage interest is deductible for the household.",
            income_potential_explanation="Debt does not create income, but lowering high-cost debt can improve monthly cash flow over time.",
            what_to_watch=[
                "Interest rate compared with other debts and safe cash needs.",
                "Monthly payment as a share of income.",
                "Whether extra payments would reduce flexibility too much.",
            ],
            beginner_takeaway="CrocLens treats debt as part of the full wealth picture because assets and liabilities must be viewed together.",
            safe_next_steps=[
                "Consider comparing this rate with other debts before prioritizing payoff.",
                "You may want to research whether your emergency fund is strong before extra payments.",
                "This may be worth discussing with a professional before refinancing or changing payment strategy.",
            ],
            key_metrics=[
                AssetDetailMetric(
                    label="Balance",
                    value="$106,000",
                    explanation="Sample amount still owed on the mortgage.",
                    tone="coral",
                ),
                AssetDetailMetric(
                    label="Interest rate",
                    value="6.1%",
                    explanation="The sample annual rate used in Phase 6 debt impact logic.",
                    tone="gold",
                ),
                AssetDetailMetric(
                    label="Debt impact",
                    value="34.8%",
                    explanation="Total liabilities divided by total assets in the sample portfolio.",
                    tone="gold",
                ),
            ],
            confidence="medium",
            data_limitations=["Uses sample liability data.", "No live lender, amortization schedule, or income data is connected yet."],
            source=MOCK_SOURCE,
            educational_disclaimer=EDUCATIONAL_DISCLAIMER,
        ),
        AssetDetailResponse(
            id="asset_retirement",
            symbol="401K",
            name="Retirement accounts",
            category="retirement",
            asset_type="Retirement",
            current_value=42_822,
            allocation_percent=13,
            risk_level="medium",
            portfolio_role="Long-term wealth bucket with special tax rules and contribution planning.",
            headline="Retirement accounts are long-term accounts, so CrocLens explains progress, limits, and employer match basics.",
            what_this_is="Retirement accounts such as a 401(k) or IRA are designed for long-term saving and often have tax advantages.",
            why_it_matters="These accounts can be central to future security, especially when employer matching or tax benefits apply.",
            risk_explanation="Risk depends on the investments inside the account, not only the account label.",
            liquidity_explanation="Liquidity is lower because early withdrawals can involve taxes, penalties, or plan restrictions.",
            tax_complexity_explanation="Tax complexity is moderate to high because contribution type, withdrawal timing, and account rules matter.",
            income_potential_explanation="Retirement accounts may hold assets that produce dividends or interest, but the main purpose is long-term growth.",
            what_to_watch=[
                "Contribution rate compared with employer match rules.",
                "Investment mix inside the account.",
                "Account fees and whether old retirement accounts should be reviewed.",
            ],
            beginner_takeaway="CrocLens separates retirement accounts because they can be powerful, but their rules are different from regular brokerage accounts.",
            safe_next_steps=[
                "Consider reviewing whether you understand the employer match formula.",
                "You may want to research the investment mix inside the retirement account.",
                "This may be worth discussing with a professional before rollovers or early withdrawals.",
            ],
            key_metrics=[
                AssetDetailMetric(
                    label="Current value",
                    value="$42,822",
                    explanation="Sample retirement account value in the portfolio.",
                    tone="green",
                ),
                AssetDetailMetric(
                    label="Portfolio share",
                    value="13%",
                    explanation="A long-term bucket with different access rules.",
                    tone="gold",
                ),
                AssetDetailMetric(
                    label="Access",
                    value="Restricted",
                    explanation="Early withdrawals may have tax or penalty consequences.",
                    tone="coral",
                ),
            ],
            confidence="medium",
            data_limitations=["Uses sample retirement account data.", "No plan rules, employer match, or contribution feed is connected yet."],
            source=MOCK_SOURCE,
            educational_disclaimer=EDUCATIONAL_DISCLAIMER,
        ),
    ]


def get_action_plan() -> ActionPlanResponse:
    return ActionPlanResponse(
        plan_id="plan_mock_phase_3",
        items=[
            ActionPlanItem(
                id="action_cash_buffer",
                title="Review emergency cash target",
                description="Consider comparing your cash reserve with three months of core expenses.",
                priority="high",
                status="suggested",
                safe_wording_note="Uses review language, not a direct instruction.",
            ),
            ActionPlanItem(
                id="action_debt_rates",
                title="Compare debt interest rates",
                description="You may want to research whether high-interest debt is affecting net worth growth.",
                priority="medium",
                status="suggested",
                safe_wording_note="Frames the item as research, not advice.",
            ),
        ],
        confidence="medium",
        data_limitations=["Uses static sample data only.", "No live account or market data is connected."],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def generate_action_plan() -> ActionPlanResponse:
    return get_action_plan()
