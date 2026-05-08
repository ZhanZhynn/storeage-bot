# Shopee Open Platform Reference

Sources:
- API calls overview: https://open.shopee.com/developer-guide/16
- Authorization and authentication: https://open.shopee.com/developer-guide/20
- Orders list API: https://open.shopee.com/documents/v2/v2.order.get_order_list?module=94&type=1

## API Calls Overview

### Base Domains

Production:
- Global: https://partner.shopeemobile.com
- China: https://openplatform.shopee.cn
- Brazil: https://openplatform.shopee.com.br

Sandbox:
- Global: https://openplatform.sandbox.test-stable.shopee.sg
- China: https://openplatform.sandbox.test-stable.shopee.cn

### Common Parameters

All API calls require:
- partner_id (int)
- timestamp (int, Unix seconds, valid for 5 minutes)
- sign (HMAC-SHA256, lowercase hex)

Shop or merchant APIs also require:
- access_token
- shop_id (shop APIs) or merchant_id (merchant APIs)

### Signature Rules

Hash function: HMAC-SHA256
Output: lowercase hex

Sign base string formats:
- Public APIs: partner_id + api_path + timestamp
- Shop APIs: partner_id + api_path + timestamp + access_token + shop_id
- Merchant APIs: partner_id + api_path + timestamp + access_token + merchant_id

## Authorization and Authentication

### Authorization Flow

1. Generate authorization link.
2. Seller grants authorization.
3. Exchange code for access and refresh tokens.
4. Refresh access token before expiry.

Authorization validity: up to 365 days.
Code validity: 10 minutes, single use.
Access token: 4 hours.
Refresh token: 30 days.

### Authorization URLs

Auth link endpoint: /api/v2/shop/auth_partner

Production:
- Global: https://partner.shopeemobile.com/api/v2/shop/auth_partner
- China: https://openplatform.shopee.cn/api/v2/shop/auth_partner

Sandbox:
- Global: https://openplatform.sandbox.test-stable.shopee.sg/api/v2/shop/auth_partner
- China: https://openplatform.sandbox.test-stable.shopee.cn/api/v2/shop/auth_partner

### Get Access Token

Endpoint: /api/v2/auth/token/get (POST)

Request body:
- code (required)
- partner_id (required)
- shop_id or main_account_id (one required)

Response fields (common):
- access_token
- refresh_token
- expire_in
- shop_id_list (main account only)
- merchant_id_list (main account only)

### Refresh Access Token

Endpoint: /api/v2/auth/access_token/get (POST)

Request body:
- refresh_token (required)
- partner_id (required)
- shop_id or merchant_id (one required)

Notes:
- Each refresh returns new access_token and refresh_token.
- Old access_token remains valid for 5 minutes after refresh.

## Orders List API (v2.order.get_order_list)

Endpoint: /api/v2/order/get_order_list (GET)

Required parameters:
- time_range_field (create_time or update_time)
- time_from (Unix seconds)
- time_to (Unix seconds)
- page_size (1-100)

Optional parameters:
- cursor
- order_status
- response_optional_fields

Response highlights:
- order_list
- next_page (cursor)
