# Shopee API Docs Scraping Guide

## Purpose
Guide for scraping Shopee Open Platform API documentation.

## Prerequisites
- Firecrawl CLI installed
- API documentation URL pattern: `https://open.shopee.com/documents/v2/v2.{module}.{api_name}?module={module_id}&type=1`

## Full Command

```bash
firecrawl scrape "https://open.shopee.com/documents/v2/v2.{module}.{api_name}?module={module_id}&type=1" --only-main-content --wait-for 8000 -o platform_helpers/shopee/api_docs/v2/{module}/{api_name}.md
```

### Parameters
| Parameter | Description |
| --- | --- |
| URL | Full API doc URL fromShopee Open Platform |
| --only-main-content | Extract main content only (works after JS renders) |
| --wait-for 8000 | Wait 8 seconds for JS to render |
| -o | Output file path |

## Batching Strategy

### Parallel Batch Size
- **5 APIs per parallel call** (recommended)
- Execute in batches of 5 to avoid rate limiting

### Command Example (batch of 5)
```bash
firecrawl scrape "URL1" --only-main-content --wait-for 8000 -o out1.md &
firecrawl scrape "URL2" --only-main-content --wait-for 8000 -o out2.md &
firecrawl scrape "URL3" --only-main-content --wait-for 8000 -o out3.md &
firecrawl scrape "URL4" --only-main-content --wait-for 8000 -o out4.md &
firecrawl scrape "URL5" --only-main-content --wait-for 8000 -o out5.md &
wait
```

### Retry Strategy
If a file is too small (<1KB), retry individually:
```bash
firecrawl scrape "FAILED_URL" --only-main-content --wait-for 10000 -o output.md
```

## Module IDs Reference

| Module | module ID |
| --- | --- |
| Order | 94 |
| Product | 89 |
| Returns | 102 |
| Account Health | 103 |
| Ads | 117 |
| Payment | 97 |
| Discount | 96 |
| Shop Flash Sale | 98 |

## File Structure

```
platform_helpers/shopee/api_docs/v2/
├── PLAN.md                    # This file
├── order/
│   ├── get_order_list.md
│   ├── get_order_detail.md
│   ├── best_practice_guide.md
│   └── shopee_xpress_best_practice.md
├── product/
│   ├── get_category.md
│   ├── get_item_list.md
│   ├── variant_management_best_practice.md
│   ├── product_base_info_management_best_practice.md
│   └── stock_and_price_management_best_practice.md
├── payment/
│   ├── get_escrow_detail.md
│   └── get_income_statement.md
├── returns/
│   ├── get_return_list.md
│   └── confirm.md
├── account_health/
│   └── get_shop_performance.md
└── ads/
    ├── get_total_balance.md
    ├── get_product_campaign_daily_performance.md
    └── ads_best_practice.md
```

## Notes

- `--only-main-content` flag doesn't fully filter JS-rendered Shopee docs
- Files include navigation prefix (~1500 lines) but actual docs start around line 1502
- Use `grep` to find "## Request Parameters" to verify content exists
- All files are complete and usable - just verbose

## Quick Start

1. Create module directory:
```bash
mkdir -p platform_helpers/shopee/api_docs/v2/{module}
```

2. Scrape single API:
```bash
firecrawl scrape "https://open.shopee.com/documents/v2/v2.order.get_order_list?module=94&type=1" --only-main-content --wait-for 8000 -o platform_helpers/shopee/api_docs/v2/order/get_order_list.md
```

3. Verify:
```bash
wc -l platform_helpers/shopee/api_docs/v2/order/get_order_list.md
grep "## Request Parameters" platform_helpers/shopee/api_docs/v2/order/get_order_list.md
```