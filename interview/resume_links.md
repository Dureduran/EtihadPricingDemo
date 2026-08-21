# Resume links

Lead with this lab. Do not lead with the Qatar RASK cockpit.

**Ancillary Pricing Production Lab** — Independent prototype | extra baggage and extra-legroom seats

- Live lab: https://dureduran.github.io/EtihadPricingDemo/ — land on Price Explanation
- One-page brief: https://dureduran.github.io/EtihadPricingDemo/one_page_brief.pdf (`interview/one_page_brief.pdf`)
- Databricks notebook: `databricks/02_train_new_model.py` and this public repo https://github.com/Dureduran/EtihadPricingDemo

Do not hyperlink a Databricks workspace. Put the word Databricks in the bullet.

Supporting RM literacy only: fare/inventory cockpit https://qa-dashboard-lac.vercel.app/

Target bullets:

- Built a production lab that tests a New Model against Current Pricing for extra baggage and extra-legroom seats, then applies Business Rules so Revenue Management keeps final control.
- Trained P(buy | price, booking context) on Databricks, selected price by expected revenue, and compared Current vs New on simulated offer logs (synthetic + public data).
- Added rollout (shadow → 5% → 20%), checkout fallback, and a monitor with a HOLD / Return to Current Pricing decision so a model is not left live when behaviour drifts.
