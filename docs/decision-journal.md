# Phase 15: Decision Journal And Feedback Loop

## What We Built

Phase 15 adds a decision journal workflow.

Users can record:

- Decision type.
- Title and symbol/topic.
- Reason.
- Expected outcome.
- Risk considered.
- Review date.

The backend returns rule-based feedback that focuses on decision quality, not market predictions.

## Why This Matters

A journal helps users learn from their process. It encourages users to write down assumptions before acting, then review whether the decision process was sound.

## Endpoints

```http
GET /api/v1/journal/entries
POST /api/v1/journal/entries
```

## Mini Assignment

Add a reviewed entry that compares the expected outcome with what actually happened.
