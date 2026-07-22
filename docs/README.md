# Pred-Market Documentation

## Deployment

For the active Railway production-style staging environment, start with:

- `deployment/railway/production_staging_runbook.md`
- `deployment/railway/railway_hosting_master_plan.md`

This folder contains the planning and product documentation for Pred-Market V1.

Pred-Market V1 now has a Next.js frontend with mock-preview and real-backend modes, plus a FastAPI backend foundation under `backend/`. Backend phases 1-8 cover auth/users, market reads, persisted watchlists, market suggestions/admin review, simulated wallets, double-entry ledger entries, orders, matching, positions, trades, admin-led settlement, analytics rollups, realtime event outbox, and WebSocket subscriptions. V1 implementation defaults to simulated funds only.

## Folder Structure

```text
docs/
  README.md
  architecture/
    pred_market_v1_architecture.svg
  analytics/
    analytics_data_model_spec.md
  backend/
    api_contract_spec.md
    auth_and_session_spec.md
    backend_implementation_spec.md
    database_schema_spec.md
    order_matching_engine_spec.md
    settlement_resolution_spec.md
    wallet_double_entry_ledger_spec.md
  categories/
    commodities_rulebook.md
    economics_rulebook.md
    sports_rulebook.md
    weather_climate_rulebook.md
  compliance/
    compliance_and_risk_policy_spec.md
  data/
    market_data_source_catalog_and_ai_strategy.md
  frontend/
    frontend_completion_plan.md
    frontend_design_system_spec.md
    final_real_backend_qa_review.md
  market-types/
    binary_market_end_to_end_workflow.md
    multiple_choice_market_end_to_end_workflow.md
    prediction_market_types_end_to_end_documentation.md
    six_buyable_contract_market_types.md
    user_to_user_binary_market_model.md
  planning/
    market_categories_automation_and_analytics.md
    phase_4_6_backend_implementation_plan.md
    phase_7_8_realtime_analytics_frontend_integration_plan.md
    pred_market_v1_implementation_plan.md
    pred_market_discussion_record.md
    pred_market_v1_tech_stack_and_database_plan.md
  testing/
    persistent_real_database_simulation.md
```

## Recommended Reading Order

1. [Discussion Record](planning/pred_market_discussion_record.md)
2. [Tech Stack And Database Plan](planning/pred_market_v1_tech_stack_and_database_plan.md)
3. [Pred-Market V1 Implementation Plan](planning/pred_market_v1_implementation_plan.md)
4. [Phase 4-6 Backend Implementation Plan](planning/phase_4_6_backend_implementation_plan.md)
5. [Phase 7-8 Realtime, Analytics, And Frontend Integration Plan](planning/phase_7_8_realtime_analytics_frontend_integration_plan.md)
6. [Backend Implementation Spec](backend/backend_implementation_spec.md)
7. [Auth And Session Spec](backend/auth_and_session_spec.md)
8. [Database Schema Spec](backend/database_schema_spec.md)
9. [Wallet And Double-Entry Ledger Spec](backend/wallet_double_entry_ledger_spec.md)
10. [Order Matching Engine Spec](backend/order_matching_engine_spec.md)
11. [Settlement And Resolution Spec](backend/settlement_resolution_spec.md)
12. [API Contract Spec](backend/api_contract_spec.md)
13. [Frontend Design System Spec](frontend/frontend_design_system_spec.md)
14. [Frontend Completion Plan](frontend/frontend_completion_plan.md)
15. [Final Real Backend QA Review](frontend/final_real_backend_qa_review.md)
16. [Analytics Data Model Spec](analytics/analytics_data_model_spec.md)
17. [Compliance And Risk Policy Spec](compliance/compliance_and_risk_policy_spec.md)
18. [Market Categories, Automation, And Analytics Plan](planning/market_categories_automation_and_analytics.md)
19. [Market Data Source Catalog And AI Strategy](data/market_data_source_catalog_and_ai_strategy.md)
20. [Sports Category Rulebook](categories/sports_rulebook.md)
21. [Economics Category Rulebook](categories/economics_rulebook.md)
22. [Weather And Climate Category Rulebook](categories/weather_climate_rulebook.md)
23. [Commodities Category Rulebook](categories/commodities_rulebook.md)
24. [All Market Types End-to-End Documentation](market-types/prediction_market_types_end_to_end_documentation.md)
25. [Six Buyable Contract Market Types](market-types/six_buyable_contract_market_types.md)
26. [Binary YES/NO Market End-to-End Workflow](market-types/binary_market_end_to_end_workflow.md)
27. [User-to-User Binary Market Model](market-types/user_to_user_binary_market_model.md)
28. [Multiple-Choice Market End-to-End Workflow](market-types/multiple_choice_market_end_to_end_workflow.md)
29. [Pred-Market V1 Architecture SVG](architecture/pred_market_v1_architecture.svg)
30. [Persistent Real-Database Trading Simulation](testing/persistent_real_database_simulation.md)

## Sections

### Architecture

The architecture folder contains visual system architecture artifacts for Pred-Market V1.

### Backend

The backend folder contains implementation-facing specs for:

```text
- backend module boundaries and request flows
- authentication, session, and RBAC rules
- PostgreSQL schema and migration order
- wallet and double-entry ledger workflows
- order matching engine rules
- settlement and resolution workflows
- REST and WebSocket API contracts
```

### Frontend

The frontend folder contains the design system spec and completion plan for the calm trading terminal UI.

### Categories

The categories folder contains source, settlement, edge-case, void, and automation rulebooks for launch-priority categories.

### Analytics

The analytics folder contains the read-model, rollup, chart, liquidity, open-interest, and reconciliation spec.

### Compliance

The compliance folder contains risk, restricted category, prohibited market, KYC/AML, jurisdiction, eligibility, and manipulation-monitoring policy assumptions.

### Data

The data folder defines sector coverage, source tiers, approved/discovery source policy, issuing flows, and AI usage boundaries.

### Market Types

The market-types folder contains detailed documentation for:

```text
- binary YES/NO markets
- multiple-choice markets
- range markets
- threshold markets
- conditional markets
- combo/parlay-style markets
- scalar markets
```

For V1 buyable contract implementation, start with the six discrete contract types in
[Six Buyable Contract Market Types](market-types/six_buyable_contract_market_types.md).
Scalar markets are documented as a later specialized payoff model.

### Planning

The planning folder contains the original discussion record, the recommended V1 technology/database direction, and phase-specific implementation plans.
It also includes the category, automation, and analytics plan for making markets easier to operate and easier for users to analyze.

### Testing

The testing folder records persistent local PostgreSQL simulations, exact data counts, verified workflows, and defects found during real-database execution.

## Build Status

The project now includes a Next.js frontend with mock mode and FastAPI integration mode. It also includes the FastAPI backend foundation for phases 1-8: real backend auth/session APIs, seeded market reads, persisted watchlists, market suggestions/admin review, simulated wallets, ledger entries, orders, matching, positions, trades, admin-led settlement, analytics rollups, realtime event outbox, and WebSocket subscriptions. Real-money launch remains blocked until KYC/AML, jurisdiction controls, payment rails, reconciliation, compliance review, and production risk controls are implemented.
