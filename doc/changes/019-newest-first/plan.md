# 019 Newest card first: plan

- **Core.** The card listing takes an option to return the newest card first;
  its default stays oldest first, so export (id order, EX-6) is unchanged.
- **Web.** The card list asks for newest first. No other change.
- **Tests.** The core CL-1 test and the e2e list-order test now expect newest
  first; export tests keep id order.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served. |
| II. Core and frontend | Served: the order is decided in the core. |
| III. Tested offline | Served. |
| IV. No new technology | Served. |
