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
    stage: "Guided workspace",
    focusAreas: [
      "Holdings table",
      "Account grouping",
      "Allocation by asset class",
      "Beginner explanations"
    ],
    nextMilestone: "This area becomes more useful as you add holdings, debts, and goals.",
    beginnerNote: "A portfolio is the full collection of investments and cash you own."
  },
  compareAssets: {
    title: "Compare Assets",
    description:
      "Compare risk, liquidity, tax complexity, income potential, and inflation sensitivity across asset types.",
    stage: "Guided workspace",
    focusAreas: [
      "Stocks vs ETFs",
      "Crypto vs cash",
      "Real estate vs bonds",
      "Cross-asset scorecards"
    ],
    nextMilestone: "CrocLens will keep adding clearer comparisons as your records grow.",
    beginnerNote:
      "Cross-asset comparison helps you understand tradeoffs, not chase a single best asset."
  },
  watchlist: {
    title: "Watchlist",
    description: "Save assets and markets you want to research before making a decision.",
    stage: "Guided workspace",
    focusAreas: [
      "Stocks and ETFs",
      "Crypto",
      "Real estate markets",
      "Why I am watching notes"
    ],
    nextMilestone: "Use this area to organize assets you want to research more carefully.",
    beginnerNote: "A watchlist is a research list. It is not a recommendation to buy."
  },
  actionPlans: {
    title: "Action Plans",
    description: "Turn CrocLens insights into safe, educational review checklists.",
    stage: "Guided workspace",
    focusAreas: [
      "Review steps",
      "Priority labels",
      "Confidence levels",
      "Data limitations"
    ],
    nextMilestone: "CrocLens turns insights into review steps, not trading instructions.",
    beginnerNote:
      "Action plans should say what to review or research, not tell you what to buy or sell."
  },
  journal: {
    title: "Decision Journal",
    description: "Record financial decisions so you can learn from your reasoning over time.",
    stage: "Guided workspace",
    focusAreas: ["Decision type", "Reason", "Expected outcome", "Review date"],
    nextMilestone: "Use this area to practice better financial reasoning over time.",
    beginnerNote:
      "A journal helps you improve your process instead of judging decisions only by short-term results."
  },
  retirement: {
    title: "Retirement",
    description:
      "Understand 401(k), IRA, contribution rate, employer match, and progress toward long-term goals.",
    stage: "Guided workspace",
    focusAreas: ["401(k) match", "IRA tracking", "Contribution scenarios", "Goal progress"],
    nextMilestone: "Use this area to review contribution habits and retirement assumptions.",
    beginnerNote:
      "Retirement planning depends heavily on assumptions, time horizon, and contribution consistency."
  },
  taxPlanner: {
    title: "Tax Planner",
    description:
      "Learn tax-aware investing concepts like holding periods, tax lots, and unrealized gains.",
    stage: "Guided workspace",
    focusAreas: ["Tax lots", "Holding periods", "Unrealized gains", "Wash-sale warnings"],
    nextMilestone: "Use this area to learn tax concepts before making taxable decisions.",
    beginnerNote:
      "Tax insights are educational and should be reviewed with a qualified tax professional."
  },
  settings: {
    title: "Settings",
    description: "Manage profile preferences, privacy controls, exports, and future account settings.",
    stage: "Guided workspace",
    focusAreas: ["Beginner mode", "Privacy controls", "Export data", "Delete account/data"],
    nextMilestone: "Use this area to manage privacy, preferences, exports, and account controls.",
    beginnerNote: "Settings are where users should control data visibility, exports, and deletion."
  }
} satisfies Record<string, ProductPageConfig>;
