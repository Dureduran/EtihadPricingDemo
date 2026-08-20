# 8-minute business case

This 8-minute case uses the Ancillary Pricing Production Lab, not a second product.

1. Commercial objective — raise ancillary revenue per passenger on extra baggage and extra-legroom without breaking conversion, brand inclusion, or Guest comps.
2. Decision — which price the customer sees; Business Rules win over the New Model.
3. Data I would request in week one — see DATA_CARD.md section D. This lab uses synthetic + public data only.
4. Model options — monotonic gradient boosting for P(buy), discrete grid on Price × P(buy). Deepair-style end-to-end net is a later live test, not this POC.
5. Validation — holdout AUC/log-loss, monotonic price, leakage test, simulated Current vs New comparison.
6. Change plan — shadow, 5%, 20%, HOLD if AUH–BOM short-DTD drifts.
7. Risks — Guest perception, airport vs digital bag price, fare/ancillary inconsistency, overfit to synthetic WTP.

Spoken 90-day ideas only (not in v1): fare-brand buy-up, and fare+ancillary coherence (ticket bid price vs bag/seat).
