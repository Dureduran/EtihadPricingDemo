# Ancillary Pricing Production Lab

Testing, safely rolling out and monitoring machine-learning pricing for airline seats and baggage

Independent portfolio prototype using synthetic and public data. No Etihad internal data, systems or proprietary pricing logic are used.

## Problem

Etihad already prices ancillaries in-house. The job is not “build a model that prints a price.” It is to test a New Model against Current Pricing, keep Business Rules in control, roll out in traffic steps, and HOLD or Return to Current Pricing when the model is not healthy.

## Two systems

**Current Pricing** — simulated existing system using route, days to departure, product, channel, and remaining inventory.

**New Model** — P(buy | price, booking context), then Price × P(buy) on an allowed grid. Trained on Databricks Free; BigQuery ingest + Colab/Vertex notebook in-repo. Scored in the lab from an exported artifact.

Business Rules always finish the job (included-in-fare, loyalty, min/max, inventory, airport vs online bags, temporary RM caps). Example: recommend AED 175, cap AED 150, customer sees AED 150.

## Products (v1)

Extra baggage. Preferred / extra-legroom seat. Fare-brand upgrades are future expansion.

## Rollout

Offline → shadow (log New Model, customer still gets Current Pricing) → 5% → 20% → 50% → 100%. Pause or Return to Current Pricing at any time.

## Checkout fallback

New Model → Current Pricing → simple rules → safe fixed price.

## How to read the four screens

1. Price Explanation — why this booking’s extra-legroom price moved.  
2. Pricing Controls — traffic, bands, temporary caps. Not per-passenger approve.  
3. Pricing Test Results — revenue per passenger, conversion, ASP. Simulated.  
4. Production Monitor — commercial, model, system, rules, then a giant Rollout Decision (HOLD / expand / return).

GitHub: https://github.com/Dureduran/EtihadPricingDemo
