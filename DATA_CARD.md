# Data card

Independent portfolio prototype using synthetic and public data. No Etihad internal data, systems or proprietary pricing logic are used.

## A. Public seed

The British Airways customer-booking dataset (Kaggle: `patelparth3399/british-airways-customer-booking`) is the public behavioural seed: party size, sales channel, purchase lead, route, and binary take-up of extra baggage / preferred seat.

This build used a **BA-shaped synthetic seed** (`kaggle_used: false`, 12,000 rows, seed 42) because the Kaggle file was not in `data/raw_kaggle/`. Place `customer_booking.csv` there to mix in the real public file. The seed is **take-up**, not priced willingness-to-pay.

## B. Synthetic fields (added in this lab)

| Field | Why it exists |
|---|---|
| `route` overlay (AUH–LHR, AUH–JFK, AUH–BOM, AUH–CDG, AUH–SYD) | Demo hub markets |
| `fare_type` (Basic, Value, Comfort, Deluxe) | Branded-fare inclusion stand-in |
| `loyalty` | Complimentary-benefit stand-in |
| `channel` (web, app, airport) | Online vs airport bag rules |
| `days_to_departure` | Last-minute vs advance purchase |
| `remaining_extra_legroom` | Inventory constraint |
| `cabin` | Economy / Business context |
| `displayed_price` (AED) | Price the customer was shown |
| `product_type` | `extra_baggage` or `extra_legroom` |
| `purchased` | 1 if bought at the displayed price |

Hidden generator columns (`latent_wtp`, `generator_rule_id`, `true_elasticity`) are written only under `generator/` and are **not** training inputs.

## C. What the New Model may see

Customer context + displayed price + purchased / not purchased.

Allowed training columns are listed in [data/TRAINING_FEATURES.md](data/TRAINING_FEATURES.md). A unit test fails if training code reads generator-only columns.

## D. What I would request in week one on the job

1. Offer logs: displayed ancillary price, product, channel, timestamp  
2. Purchase / refund / void outcomes  
3. Fare brand at ticketing and Guest tier at offer time  
4. Seat-map remaining extra-legroom / preferred inventory  
5. Current Pricing (or rules) output and any existing model score  
6. Digital vs airport fulfilment prices  
7. Guardrail / override history from Revenue Management  

Until those exist, every metric in this lab is a **simulated result using synthetic/public data**.
