# Training features

The New Model may only see these columns:

- `route`
- `fare_type`
- `loyalty`
- `channel`
- `cabin`
- `days_to_departure`
- `remaining_extra_legroom`
- `party_size`
- `product_type`
- `displayed_price`
- `purchased`

`purchased` is the target. All others are features. `displayed_price` is the only price the model sees.

Forbidden in training: `latent_wtp`, `generator_rule_id`, `true_elasticity`, and any column under `generator/`.
