# Resume links

Lead with this lab. Do not lead with the Qatar RASK cockpit.

Paste-ready SUMMARY block: `interview/resume_top.md`

**Ancillary Pricing Production Lab** — Independent prototype | extra baggage and extra-legroom seats

- Live lab: https://dureduran.github.io/EtihadPricingDemo/ — land on Price Explanation
- Executive walkthrough: https://dureduran.github.io/EtihadPricingDemo/walkthrough.html (`docs/walkthrough.html`)
- One-page brief: https://dureduran.github.io/EtihadPricingDemo/one_page_brief.pdf (`interview/one_page_brief.pdf`)
- Databricks train: https://github.com/Dureduran/EtihadPricingDemo/blob/main/databricks/02_train_new_model.py
- Databricks notebook (same train, renders on GitHub): https://github.com/Dureduran/EtihadPricingDemo/blob/main/databricks/train_new_model.ipynb
- BigQuery ingest + train (Vertex/Colab notebook): https://github.com/Dureduran/EtihadPricingDemo/blob/main/gcp/run_ingest_and_train.ipynb
- Repo: https://github.com/Dureduran/EtihadPricingDemo

Do not hyperlink a Databricks workspace or a GCP console. Put the words Databricks and BigQuery in the bullet.

Supporting RM literacy only: fare/inventory cockpit https://qa-dashboard-lac.vercel.app/

## Screenshot-style four lines (use these at the top)

The Ancillary Pricing Production Lab PoC (Python, Streamlit, monotonic XGBoost, Databricks, BigQuery) addresses 4 critical management challenges:

1. Inherit Current Pricing (Problem: A model that only prints a price cannot replace today’s quote) → Monotonic XGBoost P(buy | price, booking context), then Price × P(buy) on an AED grid vs Current Pricing → holdout AUC 0.87; local +8.9% expected revenue on AUH–LHR extra-legroom — still not a go-live
2. Business Rules Control (Problem: Models bypass fare inclusion, Guest comps, inventory, and RM caps) → Rules always finish the quote → AED 175 recommended, AED 150 cap, guest sees AED 150; 0 rule violations
3. Safe Production Rollout (Problem: A pricing cutover becomes a network-wide ancillary event) → Shadow → 5% → 20% traffic ladder plus a 4-layer checkout fallback (New Model → Current Pricing → simple rules → safe fixed price) → only AUH–LHR extra-legroom live at 20%; guest still gets a valid price if the model fails
4. Production Monitor (Problem: Unhealthy models stay live) → HOLD / Return to Current Pricing if RevPP ≤ −2% or conversion ≤ −3 pp → simulated −44.3% RevPP / −19.8 pp conversion triggered Return — the kill switch worked

Target bullets (experience-section style):

- Built a production lab that tests a New Model against Current Pricing for extra baggage and extra-legroom seats, then applies Business Rules so Revenue Management keeps final control.
- Trained P(buy | price, booking context) on Databricks, selected price by expected revenue, and compared Current vs New on simulated offer logs (synthetic + public data).
- Added a BigQuery ingest and Vertex/Colab notebook for the same offer log, with the training-column contract enforced in code (synthetic + public data).
- Added rollout (shadow → 5% → 20%), checkout fallback, and a monitor with a HOLD / Return to Current Pricing decision so a model is not left live when behaviour drifts.
