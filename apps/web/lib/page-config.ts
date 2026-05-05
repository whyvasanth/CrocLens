export interface ProductPageConfig {
  beginnerNote: string;
  description: string;
  focusAreas: string[];
  nextMilestone: string;
  stage: string;
  title: string;
}

export const productPages = {
  portfolio: {
    title: "Portfolio",
    description:
      "Track your stocks, ETFs, mutual funds, crypto, cash, and bonds in one beginner-friendly view.",
    stage: "Phase 2 placeholder",
    focusAreas: [
      "Holdings table",
      "Account grouping",
      "Allocation by asset class",
      "Beginner explanations"
    ],
    nextMilestone: "Phase 5 will connect this page to portfolio API data.",
    beginnerNote: "A portfolio is the full collection of investments and cash you own."
  },
  compareAssets: {
    title: "Compare Assets",
    description:
      "Compare risk, liquidity, tax complexity, income potential, and inflation sensitivity across asset types.",
    stage: "Phase 2 placeholder",
    focusAreas: [
      "Stocks vs ETFs",
      "Crypto vs cash",
      "Real estate vs bonds",
      "Cross-asset scorecards"
    ],
    nextMilestone: "Phase 6 will add transparent scoring formulas.",
    beginnerNote:
      "Cross-asset comparison helps you understand tradeoffs, not chase a single best asset."
  },
  watchlist: {
    title: "Watchlist",
    description: "Save assets and markets you want to research before making a decision.",
    stage: "Phase 2 placeholder",
    focusAreas: [
      "Stocks and ETFs",
      "Crypto",
      "Real estate markets",
      "Why I am watching notes"
    ],
    nextMilestone: "Phase 16 will add watchlist intelligence and AI summaries.",
    beginnerNote: "A watchlist is a research list. It is not a recommendation to buy."
  },
  actionPlans: {
    title: "Action Plans",
    description: "Turn CrocLens insights into safe, educational review checklists.",
    stage: "Phase 2 placeholder",
    focusAreas: [
      "Review steps",
      "Priority labels",
      "Confidence levels",
      "Data limitations"
    ],
    nextMilestone: "Phase 9 will add the first safe AI assistant responses.",
    beginnerNote:
      "Action plans should say what to review or research, not tell you what to buy or sell."
  },
  journal: {
    title: "Decision Journal",
    description: "Record financial decisions so you can learn from your reasoning over time.",
    stage: "Phase 2 placeholder",
    focusAreas: ["Decision type", "Reason", "Expected outcome", "Review date"],
    nextMilestone: "Phase 15 will add the decision journal workflow.",
    beginnerNote:
      "A journal helps you improve your process instead of judging decisions only by short-term results."
  },
  retirement: {
    title: "Retirement",
    description:
      "Understand 401(k), IRA, contribution rate, employer match, and progress toward long-term goals.",
    stage: "Phase 2 placeholder",
    focusAreas: ["401(k) match", "IRA tracking", "Contribution scenarios", "Goal progress"],
    nextMilestone: "Phase 14 will add retirement planning calculations.",
    beginnerNote:
      "Retirement planning depends heavily on assumptions, time horizon, and contribution consistency."
  },
  taxPlanner: {
    title: "Tax Planner",
    description:
      "Learn tax-aware investing concepts like holding periods, tax lots, and unrealized gains.",
    stage: "Phase 2 placeholder",
    focusAreas: ["Tax lots", "Holding periods", "Unrealized gains", "Wash-sale warnings"],
    nextMilestone: "Phase 13 will add educational tax-aware modules.",
    beginnerNote:
      "Tax insights are educational and should be reviewed with a qualified tax professional."
  },
  settings: {
    title: "Settings",
    description: "Manage profile preferences, privacy controls, exports, and future account settings.",
    stage: "Phase 2 placeholder",
    focusAreas: ["Beginner mode", "Privacy controls", "Export data", "Delete account/data"],
    nextMilestone: "Phase 17 will add security, privacy, and reliability controls.",
    beginnerNote: "Settings are where users should control data visibility, exports, and deletion."
  }
} satisfies Record<string, ProductPageConfig>;

