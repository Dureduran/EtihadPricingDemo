# HireVue map

Independent portfolio prototype using synthetic and public data.

| Story they want | Screen / artefact |
|---|---|
| Inherit existing pricing and improve it in-house | Opening line + Price Explanation (Current Pricing vs New Model) |
| Business Rules have final control | Price Explanation cap line; Pricing Controls temporary cap |
| Safe rollout | Pricing Controls: shadow → 5% → 20% → 50% → 100% |
| Commercial impact | Pricing Test Results (RevPP, conversion, ASP) |
| Monitor / HOLD | Production Monitor HOLD decision with a specific market/DTD reason |
| Checkout fallback | New Model → Current Pricing → simple rules → safe fixed price |
| Adoption / change | RM traffic and pause controls, not per-passenger approve |
| POC into production | Databricks notebooks or GCP BigQuery + Colab/Vertex notebooks + exported model + fallback |

Keep simulated-data honesty in every answer. Say: Simulated result using synthetic/public data.
