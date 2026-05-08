# Shopee Platform Helper

keywords: shopee, shopee api, shopee auth, shopee authorization, shopee integration

## Documentation Sources

- API calls overview: https://open.shopee.com/developer-guide/16
- Authorization and authentication: https://open.shopee.com/developer-guide/20
- Orders list API: https://open.shopee.com/documents/v2/v2.order.get_order_list?module=94&type=1

## Notes

- Signatures use HMAC-SHA256 and lowercase hex output.
- Public APIs sign base string: partner_id + api_path + timestamp.
- Shop APIs sign base string: partner_id + api_path + timestamp + access_token + shop_id.
- Merchant APIs sign base string: partner_id + api_path + timestamp + access_token + merchant_id.
