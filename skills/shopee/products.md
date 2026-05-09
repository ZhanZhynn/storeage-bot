# Shopee Products Summary

keywords: shopee, products, product, sku, model, item, inventory, stock, price, comments, reply, listing

## Quick Answer (Use This)

```bash
# Fetch products (default behavior)
python3 -m platform_helpers.shopee.cli products get --page-size 50

# Fetch one product (base info + models if present)
python3 -m platform_helpers.shopee.cli products get-one --item-id <ITEM_ID>
```

Returns: product list or product detail with base info and models when `has_model=true`.

<!-- END_QUICK_ANSWER -->

---

# Full Documentation

## Goal
Retrieve Shopee catalog data, SKU (model) stock/price, and buyer comments via deterministic helpers.

## Common Endpoint Family
- `/api/v2/product/get_item_list`
- `/api/v2/product/get_item_base_info`
- `/api/v2/product/get_model_list`
- `/api/v2/product/update_price`
- `/api/v2/product/update_stock`
- `/api/v2/product/get_comment`
- `/api/v2/product/reply_comment`

## Deterministic Helper Commands (Preferred)
- Fetch product list:
  - `python3 -m platform_helpers.shopee.cli products get --page-size 50`
  - `python3 -m platform_helpers.shopee.cli products get --page-size 50 --item-status NORMAL,UNLIST`
  - `python3 -m platform_helpers.shopee.cli products get --page-size 50 --max-pages 5`
- Search products (requires item_name or attribute_status):
  - `python3 -m platform_helpers.shopee.cli products search --item-name "shirt"`
  - `python3 -m platform_helpers.shopee.cli products search --attribute-status 2`
  - `python3 -m platform_helpers.shopee.cli products search --item-sku "SKU-123" --item-name "shirt"`
  - `python3 -m platform_helpers.shopee.cli products search --item-name "shirt" --item-status NORMAL,UNLIST --deboost-only true`
- Product detail:
  - `python3 -m platform_helpers.shopee.cli products get-one --item-id <ITEM_ID>`
- Models (variants):
  - `python3 -m platform_helpers.shopee.cli products models --item-id <ITEM_ID>`
- Extra info (views/likes/sales/ratings):
  - `python3 -m platform_helpers.shopee.cli products extra --item-id <ITEM_ID>`
- Promotions:
  - `python3 -m platform_helpers.shopee.cli products promotion --item-id <ITEM_ID>`
- Add product:
  - `python3 -m platform_helpers.shopee.cli products add --payload '{"original_price":123.3,"description":"Item description","weight":1.1,"item_name":"Demo Item","dimension":{"package_height":11,"package_length":11,"package_width":11},"logistic_info":[{"enabled":true,"logistic_id":12345}],"category_id":14695,"image":{"image_id_list":["<IMAGE_ID>"]},"item_status":"UNLIST"}'`
  - `python3 -m platform_helpers.shopee.cli products add --payload '{"original_price":123.0,"description":"Test item created by helper","weight":1.0,"item_name":"StoreAge logo clone","item_status":"UNLIST","dimension":{"package_height":1,"package_length":1,"package_width":1},"logistic_info":[{"enabled":true,"logistic_id":21012,"is_free":false}],"attribute_list":[{"attribute_id":201004,"attribute_value_list":[{"value_id":105488,"original_value_name":"[S]No","value_unit":""}]}],"category_id":300361,"image":{"image_id_list":["my-11134207-81z1k-mo0pah5q1xxcf1"]},"condition":"NEW","brand":{"brand_id":0,"original_brand_name":"NoBrand"},"seller_stock":[{"location_id":"MYZ","stock":1}]}'`

## Stock & Price
- Get price:
  - `python3 -m platform_helpers.shopee.cli products price-get --item-id <ITEM_ID> --has-model`
  - `python3 -m platform_helpers.shopee.cli products price-get --item-id <ITEM_ID> --no-model`
- Get stock:
  - `python3 -m platform_helpers.shopee.cli products stock-get --item-id <ITEM_ID> --has-model`
  - `python3 -m platform_helpers.shopee.cli products stock-get --item-id <ITEM_ID> --no-model`
- Update price:
  - `python3 -m platform_helpers.shopee.cli products price-update --item-id <ITEM_ID> --price-list '[{"model_id":123,"original_price":12.34}]'`
- Update stock:
  - `python3 -m platform_helpers.shopee.cli products stock-update --item-id <ITEM_ID> --stock-list '[{"model_id":123,"seller_stock":[{"stock":10}]}]'`
- Get update limits:
  - `python3 -m platform_helpers.shopee.cli products limit --item-id <ITEM_ID>`

## Variant Management
- Init tier variation (changes tier structure):
  - `python3 -m platform_helpers.shopee.cli products tier-init --item-id <ITEM_ID> --tier-variation '[{"name":"Color","option_list":[{"option":"Red"}]}]' --model-list '[{"tier_index":[0],"original_price":10,"model_sku":"sku-red","normal_stock":100}]'`
- Update tier variation (add/delete/reorder options, preserve model ids):
  - `python3 -m platform_helpers.shopee.cli products tier-update --item-id <ITEM_ID> --tier-variation '[{"name":"Color","option_list":[{"option":"Red"},{"option":"Blue"}]}]' --model-list '[{"tier_index":[0],"model_id":10000},{"tier_index":[1],"model_id":20000}]'`
  - `python3 -m platform_helpers.shopee.cli products tier-update --item-id 844134051 --tier-variation '[{"name":"Color","option_list":[{"option":"Blue Updated"},{"option":"Red Updated"},{"option":"Green Updated"}]}]' --model-list '[{"tier_index":[0],"model_id":11237994},{"tier_index":[1],"model_id":11237993}]'`
- Add models:
  - `python3 -m platform_helpers.shopee.cli products model-add --item-id <ITEM_ID> --model-list '[{"tier_index":[1],"original_price":30,"model_sku":"sku-blue","seller_stock":[{"stock":20}]}]'`
  - `python3 -m platform_helpers.shopee.cli products model-add --item-id 844134051 --model-list '[{"tier_index":[2],"model_name":"Green Updated","model_sku":"green-sku","original_price":126,"seller_stock":[{"location_id":"MYZ","stock":1}]}]'`
- Update models:
  - `python3 -m platform_helpers.shopee.cli products model-update --item-id <ITEM_ID> --model-list '[{"model_id":10000,"model_sku":"sku-red"}]'`
  - `python3 -m platform_helpers.shopee.cli products model-update --item-id 844134051 --model-list '[{"model_id":11237995,"model_sku":"green-sku-2","original_price":127,"seller_stock":[{"location_id":"MYZ","stock":2}]}]'`
- Delete models:
  - `python3 -m platform_helpers.shopee.cli products model-delete --item-id <ITEM_ID> --model-id-list '[10000,20000]'`

## Comments
- Get comments:
  - `python3 -m platform_helpers.shopee.cli products comments --item-id <ITEM_ID> --page-size 50`
- Reply to comments:
  - `python3 -m platform_helpers.shopee.cli products reply --comment-list '[{"comment_id":1540927,"comment":"Thanks for your support!"}]'`

## Pagination
- `products get` uses offset + page_size with `--max-pages`
- `products comments` uses cursor + page_size with `--max-pages`

## Endpoint Mapping
- `products get` -> `/api/v2/product/get_item_list`
- `products search` -> `/api/v2/product/search_item`
- `products get-one` -> `/api/v2/product/get_item_base_info`
- `products models` -> `/api/v2/product/get_model_list`
- `products add` -> `/api/v2/product/add_item`
- `products price-update` -> `/api/v2/product/update_price`
- `products stock-update` -> `/api/v2/product/update_stock`
- `products comments` -> `/api/v2/product/get_comment`
- `products reply` -> `/api/v2/product/reply_comment`

## Execution Notes
- Execute helper command via `python3 -m platform_helpers.shopee.safe_run -- ...` and summarize JSON fields directly.

## Inputs to Clarify
- Scope: single item vs full catalog
- Whether the product has variants (`has_model`)
- Max pages and page size for pagination
- Stock/price update lists for SKU-level changes

## Guardrails
- Only update one `item_id` per price/stock request.
- For tier structure changes, use `tier-init` (existing model ids become invalid).
- For option changes that preserve model ids, use `tier-update` and provide `model_list`.
