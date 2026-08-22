# Ancillary Pricing Production Lab

Testing, safely rolling out and monitoring machine-learning pricing for airline seats and baggage

Independent portfolio prototype using synthetic and public data. No Etihad internal data, systems or proprietary pricing logic are used.

## What this is

Etihad already has an in-house ancillary dynamic-pricing capability. This lab is not another dashboard that only predicts a price. It shows how a Solutions Manager would evaluate a **New Model** against **Current Pricing**, apply **Business Rules** as the final control, introduce the model in a traffic ladder (shadow → 5% → 20% → 50% → 100%), measure commercial impact, and **Return to Current Pricing** if it is not healthy.

**v1 products:** extra baggage and preferred / extra-legroom seat only. Fare-brand upgrades (Basic → Value / Comfort) are a future expansion, not built here.

Public GitHub: [Dureduran/EtihadPricingDemo](https://github.com/Dureduran/EtihadPricingDemo)

Live lab: [https://dureduran.github.io/EtihadPricingDemo/](https://dureduran.github.io/EtihadPricingDemo/)

Executive walkthrough: [docs/walkthrough.html](https://dureduran.github.io/EtihadPricingDemo/walkthrough.html)

One-page brief: [interview/one_page_brief.pdf](https://dureduran.github.io/EtihadPricingDemo/one_page_brief.pdf)

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m data.build_offer_log
python -m new_model.train
pytest
streamlit run app/Home.py
```

Open the app and walk **Price Explanation → Pricing Controls → Pricing Test Results → Production Monitor**. Every screen carries: Simulated result using synthetic/public data.

## Architecture

**Online path**

Booking information → possible prices → New Model → P(buy) at each price → choose max expected revenue → Business Rules → final price → customer buys / does not buy → save result → monitor.

**Offline path (Databricks Free)**

Historical results → train New Model → test against Current Pricing → small controlled rollout → measure revenue + conversion → expand / pause / return.

See [databricks/README_DATABRICKS.md](databricks/README_DATABRICKS.md).

## Language

User-facing copy uses Current Pricing, New Model, Business Rules, Rollout Decision, Return to Current Pricing, and Pricing Test Results.

## Checkout fallback

1. New Model  
2. Current Pricing  
3. Simple pricing rules  
4. Safe fixed price  

If the pricing model fails during checkout, the customer still gets a valid price.

## Disclaimer

Fare-brand inclusion, loyalty complimentary seats, and online-versus-airport baggage differences in this repo are **portfolio stand-ins** shaped by public airline merchandising patterns. They are not Etihad production logic.
