Created with Sketch.Open Platform

[Documentation\\
\\
- \\
Developer Guide\\
\\
- \\
API Reference\\
\\
- \\
Push Mechanism\\
\\
\\
- \\
Terms of Use](https://open.shopee.com/developer-guide)

Support Center

-
Raise Ticket

-
FAQ


[Announcement](https://open.shopee.com/announcements) [Console](https://open.shopee.com/console?from=header)

English

-
English

-
简体中文

-
繁體中文

-
Português (Brasil)

-
Korean

-
Bahasa Indonesia

-
ไทย


Log In


Tables of Contents


API Best Practices


API Best Practices

>


Shopee On-Platform Ads API Guide


Shopee On-Platform Ads API Guide

What is Shopee Ads


What is Shopee Ads

Ads Open API Usage Rules


Ads Open API Usage Rules

Ads Open API Instruction


Ads Open API Instruction

1\. Retrieve Ad Balance and Shop Settings


1\. Retrieve Ad Balance and Shop Settings

2.Obtain real-time performance overview data of product ads (shop dimension)


2.Obtain real-time performance overview data of product ads (shop dimension)

3\. Retrieve Recommended Keywords and Product Data


3\. Retrieve Recommended Keywords and Product Data

4\. Retrieve Campaign-Level Data


4\. Retrieve Campaign-Level Data

5\. GMV Max Ads Overview


5\. GMV Max Ads Overview

6\. Item GMV Max Ads (Item-level Full-site Promotion)


6\. Item GMV Max Ads (Item-level Full-site Promotion)

7\. Shop GMV Max Ads


7\. Shop GMV Max Ads

8\. Manual Product Ads


8\. Manual Product Ads

9\. (coming offline soon) Auto Product Ads


9\. (coming offline soon) Auto Product Ads

Getting Started


Getting Started

Introduction


Introduction

Developer account registration


Developer account registration

App management


App management

API calls


API calls

Push Mechanism notifications


Push Mechanism notifications

Authorization and Authentication


Authorization and Authentication

Sandbox Testing V2


Sandbox Testing V2

Service Partner Program


Service Partner Program

V2.0 API Call Flow


V2.0 API Call Flow

CNSC API Integration Guide


CNSC API Integration Guide

KRSC API Integration Guide


KRSC API Integration Guide

V2.0 Data Definition


V2.0 Data Definition

Requesting Access to Sensitive Data


Requesting Access to Sensitive Data

API Best Practices


API Best Practices

Guidelines for Creating Product


Guidelines for Creating Product

Product creation preparation


Product creation preparation

Creating product


Creating product

Creating global product


Creating global product

Publishing global product


Publishing global product

Variant management


Variant management

Product base info management


Product base info management

Stock & Price Management


Stock & Price Management

Order Management


Order Management

First Mile Binding


First Mile Binding

Return Refund Management


Return Refund Management

SIP best practices


SIP best practices

Shopee On-Platform Ads API Guide


Shopee On-Platform Ads API Guide

Shopee Xpress - Package-free Integration Guide


Shopee Xpress - Package-free Integration Guide

API de Cotação (Logística do Vendedor)


API de Cotação (Logística do Vendedor)

Shopee Entrega Direta


Shopee Entrega Direta

AUTO PARTS: COMPATIBILIDADE DE AUTOPEÇAS


AUTO PARTS: COMPATIBILIDADE DE AUTOPEÇAS

Brazil Open API Best Practice


Brazil Open API Best Practice

Passo a Passo Logistica API


Passo a Passo Logistica API

Ferramenta de Log da Open Platform


Ferramenta de Log da Open Platform

Passo a passo para subir a NF-e através da OpenAPI


Passo a passo para subir a NF-e através da OpenAPI

APIs de orders


APIs de orders

Shopee Open API Platform \| Passo a Passo de Solicitação


Shopee Open API Platform \| Passo a Passo de Solicitação

Open API auth call \| Fluxo autorização


Open API auth call \| Fluxo autorização

Fulfilled by Shopee (BR)


Fulfilled by Shopee (BR)

Quotation API (Entrega Expressa) Developer Guide


Quotation API (Entrega Expressa) Developer Guide

Instant Mart Integration Guide


Instant Mart Integration Guide

Livestream API Integration Guide


Livestream API Integration Guide

Shopee AMS API Integration Guide


Shopee AMS API Integration Guide

Shopee Video API Integration Guide


Shopee Video API Integration Guide

Terms of Use


Terms of Use

Terms of Service


Terms of Service

Data Protection Policy


Data Protection Policy

Platform Partner Rules


Platform Partner Rules

TW Developer Screening


TW Developer Screening

Chatbot Terms of Service


Chatbot Terms of Service

# Shopee On-Platform Ads API Guide

Last Updated: 2026-01-28


Language Supported:
English /

简体中文 /

ไทย


# What is Shopee Ads

Shopee Ads allow you to create ads within Shopee’s platform to increase exposure for your products and shop.

Learn Shopee Ads： [https://ads.shopee.sg/learn/faq/96/195](https://ads.shopee.sg/learn/faq/96/195)

# Ads Open API Usage Rules

When using the advertising  API, you need to abide by the following rules we have listed so that Shopee can create a fair and safe market for all sellers:

1. When processing advertising data, you need to comply with the platform's [data protection policy](https://open.shopee.com/developer-guide/32).
2. The advertising API is limited to Shopee's official cooperative ISVs and is used with platform sellers. It can be used for shop advertising operations and official cooperation agency operation projects. The advertising API cannot be used for other purposes.
3. shop data may not be used for any purpose other than shop operations and official Shopee cooperation projects.
4. To retrieve seller shop data through the ISV API, you need to obtain the consent of the platform seller through the authorization process.

Tips: If you fail to comply with our norms and rules, you will receive a warning email from Shopee; if you fail to modify it in time, you may face our penalties.

# Ads Open API Instruction

## 1\. Retrieve Ad Balance and Shop Settings

- [v2.ads.get\_total\_balance](https://open.shopee.com/documents/v2/v2.ads.get_total_balance?module=117&type=1): Use this API to retrieve the seller's real-time total ad credit balance, including both paid and free credits. Sellers can monitor their balance status through this API to ensure that the balance is sufficient for normal ad operations.
- [v2.ads.get\_shop\_toggle\_info](https://open.shopee.com/documents/v2/v2.ads.get_shop_toggle_info?module=117&type=1): Use this API to retrieve the shop’s ad settings, such as whether auto top-up and ad price optimization features are enabled.


Top\_Up Toggle: Enable/disable auto top-up

![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=9OMZeNtLbZcBM31kOeptGJGOL9b%2FLOdIc%2BgqF5qOaCsWxSijHmVQULhecM61qncKgbVL%2BnJHmRBIfdTDtzNegg%3D%3D&image_type=png)

Campaign\_Surge: Turn on/off ads price optimization in the campaign period

- Campaign\_Surge: Enable/disable ad price optimization


![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=EmzpqKbRbsT5BPTregyG0gWD1ZHePMd4P4K8v17vMp85gdaV17e7Dlh3r4MPJ61f%2FDanJ970UPyrTtDb1paPdA%3D%3D&image_type=png)

## 2.Obtain real-time performance overview data of product ads (shop dimension)

- [v2.ads.get\_all\_cpc\_ads\_hourly\_performance](https://open.shopee.cn/documents/v2/v2.ads.get_all_cpc_ads_hourly_performance?module=167&type=1): Use this API to obtain the hourly performance data of store-level CPC advertisements for a single day. Sellers can access information such as daily Conversions, Conversion Rate, items sold, GMV, Ad GMV/Ad Expenditure, etc.
- [v2.ads.](https://open.uat.shopee.cn/documents/v2/v2.ads.get_all_cpc_ads_hourly_performance?module=167&type=1) [get\_all\_cpc\_ads\_daily\_performance](https://open.shopee.cn/documents/v2/v2.ads.get_all_cpc_ads_daily_performance?module=167&type=1): Using this API, you can obtain the multi-day performance of store-level CPC ads (with the time dimension unit being days). Sellers can get information such as daily conversions, conversion rate, items sold, GMV, Ad GMV/Ad Expenditure, etc., over multiple days.

![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=nbmTdBH0PkDRx7%2FQ%2FcZOo%2Bvb7DSa2QKGSY1hiaVwl1QkMZQAE%2FFsuL2o%2BObLzmV8F1hWxK8ZQfsRmwJM%2B23%2Fjg%3D%3D&image_type=png)

## 3\. Retrieve Recommended Keywords and Product Data

- [v2.ads.get\_recommended\_keyword\_list](https://open.shopee.com/documents/v2/v2.ads.get_recommended_keyword_list?module=117&type=1): Use this API to retrieve a list of recommended keywords per item, along with optional search keywords. Sellers can also view keyword quality scores, search volume, and suggested bids.
- [v2.ads.get\_recommended\_item\_list](https://open.shopee.com/documents/v2/v2.ads.get_recommended_item_list?module=117&type=1): Use this API to retrieve a list of recommended SKUs (shop-level) with specific tags such as Hot Search, Best Seller, or Best ROI.


![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=EbgTp9dVAnH68GfpojbO8W6vLlGyoWxR5F200%2Bhl%2Fivn%2B2WxNm2SYU8BhDr6ux9%2FVnReUVSBOmvNeZFphZtX8Q%3D%3D&image_type=png)

![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=ix5VrxQckCczwqVU%2Brwl2ZBwIZ7icdmdS5bBpXileSC8Xw8JTp6eGkL1YLsl6Fq2kxs0Iap%2BKJL5QaykSzVjqQ%3D%3D&image_type=png)

## 4\. Retrieve Campaign-Level Data

- [v2.ads.get\_product\_level\_campaign\_id\_list](https://open.shopee.com/documents/v2/v2.ads.get_product_level_campaign_id_list?module=117&type=1): Use this API to get the list of ad campaigns associated with a specific product.
- [v2.ads.get\_product\_level\_campaign\_setting\_info](https://open.shopee.com/documents/v2/v2.ads.get_product_level_campaign_setting_info?module=117&type=1): Use this API to retrieve detailed settings for a specific ad campaign.
- v2.ads.get\_product\_campaign\_daily\_performance and v2.ads.get\_product\_campaign\_hourly\_performance: Use these APIs to obtain daily/hourly performance data for product-level ad campaigns.


![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=Z%2BrMDlvue5btmgKoCnuBY9HmvZe9y6RIKUy0QPaoFaniZpxImMcdctZhtBNVtCqNK6291zdpKJdFT4MquG7gzw%3D%3D&image_type=png)

## 5\. GMV Max Ads Overview

GMV Max Ads are Shopee’s full-funnel advertising solutions that leverage automated bidding and intelligent traffic allocation to maximize sellers’ GMV performance.

Currently, Shopee supports two types of GMV Max Ads:

- Item GMV Max Ads (Item-level)
- Shop GMV Max Ads (Shop-level / Auto-selected Products)

Both ad types are powered by system automation and optimized around ROAS (Return on Ad Spend) targets.

Comparison:

|     |     |     |
| --- | --- | --- |
| Dimension | Item GMV Max | Shop GMV Max |
| Ad Level | Item | Shop |
| Product Selection | Developer-specified | System auto-selected |
| Creation API | create\_manual\_product\_ads | create\_gms\_product\_campaign |
| ROAS Control | Supported | Supported / Auto |
| Campaign Limit | Multiple | One per shop |
| Product Exclusivity Rule | A product cannot participate in both Item GMV Max Ads and Shop GMV Max Ads | A product cannot participate in both Item GMV Max Ads and Shop GMV Max Ads |

## 6\. Item GMV Max Ads (Item-level Full-site Promotion)

Item GMV Max Ads are item-level full-site promotion ads designed to promote specified products across Shopee’s entire traffic inventory.

Key Characteristics:

- Created at the item level
- Uses Auto Bidding
- Optimized around ROAS targets
- Suitable for sellers aiming to scale GMV for individual products

To create Item GMV Max Ads via Open API, use:

- v2.ads.create\_manual\_product\_ads
- Key Parameter:

  - bidding\_method = auto → Item GMV Max Ads

![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=6ndPDeh76t4V7oQyCwXKiJWLfmQRbu5uEgfqrvP1wzIT0Wz5FdO8%2B0lBR1Q7er%2FhHT5Hw2Y3I28RgCpmQ2MtTQ%3D%3D&image_type=png)

Before creating Item GMV Max Ads, developers may retrieve recommended ROAS using:

v2.ads.get\_product\_recommended\_roi\_target

![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=OGq9NqGIXTY47D%2BDFfdtgC2k%2BEpgRNjCvjEGD1RumN%2B8%2BPor5f045DTWRbuzw89g9ziq4r27818uH5cNz4LwHQ%3D%3D&image_type=png)

Developers may also retrieve recommended budget ranges via:

v2.ads.get\_create\_product\_ad\_budget\_suggestion

![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=H%2B0UMdIyPMMqGRzwnBotqObwvQPZ1gAT4udE2%2B9gLiT%2FsgtPhO8o%2F8wQdRKdm%2Bm7bK2g5Qna8VZ7icD2l1GGJQ%3D%3D&image_type=png)

Typical Flow:

1\. Call v2.ads.get\_product\_recommended\_roi\_target to retrieve recommended ROAS

2\. Call v2.ads.get\_create\_product\_ad\_budget\_suggestion to retrieve budget suggestions

3\. Call v2.ads.create\_manual\_product\_ads (bidding\_method = auto)

Note:

ROAS and budget recommendations are system-generated references. Final performance depends on actual delivery and system learning.

## 7\. Shop GMV Max Ads

Shop GMV Max Ads are shop-level full-site promotion ads. The system automatically selects products within the shop and optimizes delivery based on budget and ROAS settings to maximize overall shop GMV.

Key Characteristics:

- Created at the shop level
- System automatically selects products and dynamically allocates budget
- Supports Auto Bidding and Custom ROAS
- Suitable for sellers seeking lower management overhead and scalable shop GMV growth

Bidding Modes:

1. Auto Bidding: The system explores traffic opportunities automatically within acceptable ROAS ranges to scale exposure and GMV.
2. Custom ROAS: The system optimizes delivery based on advertiser-defined ROAS targets to balance GMV and efficiency.

To create Shop GMV Max Ads via Open API, use:

- v2.ads.create\_gms\_product\_campaign
- Key Field: roas\_target

  - Not provided or = 0 → Auto Bidding (Shop GMV Max)
  - \> 0 → Custom ROAS (Shop GMV Max)

![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=w5KtlLTaUS4X0eHvUDUQeIYQmjRpT0e4BUad8v2JznMPF3cWiujlEJvrZYKtUgeXdEtI69QVxwLh%2BF0C1xbvnw%3D%3D&image_type=png)

Before creation, developers may validate eligibility using:

- v2.ads.check\_create\_gms\_product\_campaign\_eligibility

Management & Performance APIs:

- Campaign Configuration & Management

  - v2.ads.edit\_gms\_product\_campaign: Update Shop GMV Max campaign configuration (e.g. bidding mode, ROAS settings).

- Product Management

  - v2.ads.edit\_gms\_item\_product\_campaign: Manage product-level configurations within a Shop GMV Max campaign.
  - v2.ads.list\_gms\_user\_deleted\_item: Retrieve information on products removed by the seller.

- Performance & Reporting

  - v2.ads.get\_gms\_campaign\_performance: Retrieve overall performance metrics of a Shop GMV Max campaign.
  - v2.ads.get\_gms\_item\_performance: Retrieve item-level performance metrics within a Shop GMV Max campaign.

Typical Integration Flow

1. Call v2.ads.check\_create\_gms\_product\_campaign\_eligibility

   - Validate whether the shop is eligible to create a Shop GMV Max campaign.

3. Call v2.ads.create\_gms\_product\_campaign

   - Create a Shop GMV Max campaign.

5. (Optional) Call v2.ads.edit\_gms\_product\_campaign

   - Update or adjust campaign configuration after creation.

7. Call v2.ads.get\_gms\_campaign\_performance and v2.ads.get\_gms\_item\_performance

   - Monitor campaign-level and item-level performance on an ongoing basis.

Note:

- Products are auto-selected by default and updated daily. If sellers manually adjust the product list, the seller-configured list takes precedence.
- Performance improves during the learning phase. Avoid frequent configuration changes during this period.

## 8\. Manual Product Ads

Manual Product Ads are item-level ads that require developers to explicitly configure products, keywords, and bidding strategies. Currently, this feature is available only to selected whitelist sellers.

Key Characteristics:

- Created at the item level
- Uses Manual Bidding
- Supports keyword and item targeting
- Suitable for sellers requiring granular control

To create Manual Product Ads, use:

- v2.ads.create\_manual\_product\_ads
- Key Parameter:

  - bidding\_method = manual → Manual Product Ads

![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=d294xey%2FYasFp0vjhNXYQVJsHmPfJv%2BneVEmMvCUbbyCTOYGwGG2e8l7YKab1JvElmLMw1W1qzdrl1JQgBx%2FpA%3D%3D&image_type=png)

For Manual Product Ads (bidding\_method = manual), developers may use

[v2.ads.get\_recommended\_item\_list](https://open.shopee.cn/documents/v2/v2.ads.get_recommended_item_list?module=167&type=1) and [v2.ads.get\_recommended\_keyword\_list](https://open.shopee.cn/documents/v2/v2.ads.get_recommended_keyword_list?module=167&type=1)

to obtain recommended items and keywords, and then configure budget, placements,

and other campaign settings to start ad delivery.

## 9\. (coming offline soon) Auto Product Ads

v2.ads.create\_auto\_product\_ads (whitelist shops only)

![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=iJ7Oi%2BKA9iHF9Rk7mxAcwykvPGS4Uth6w0rbCjJeHCZAwaZjfK7%2BFDfg91cuxQC%2F9QNRDp%2BpYEyrwT0pSIxAsA%3D%3D&image_type=png)

If you encounter problems, it is recommended to check the [Developer Guide](https://open.shopee.com/developer-guide/8) and search for [FAQ](https://open.shopee.com/faq?categoryId=2011).

If you encounter problems, please log in to the Open Platform Console to [Raise a ticket](https://open.shopee.com/myconsole/ticket-system/raise-ticket).

### User Guide

#### [Developer Guide](https://open.shopee.com/developer-guide/0)

#### [API reference](https://open.shopee.com/documents/v2/v2.ams.get_open_campaign_added_product?module=127&type=1)

#### [Push Mechanism](https://open.shopee.com/push-mechanism/5)

#### [Shopee Open Platform Data Protection Policy](https://open.shopee.com/policy?policy_id=1)

### Shopee Markets

#### [Service Market](https://service.shopee.cn/)

#### [Seller Education Hub (Singapore)](https://seller.shopee.sg/edu)

#### [Seller Education Hub (Malaysia)](https://seller.shopee.com.my/edu)

#### [Seller Education Hub (Thailand)](https://seller.shopee.co.th/edu)

#### [Seller Education Hub (Vietnam)](https://banhang.shopee.vn/edu)

#### [Seller Education Hub (Indonesia)](https://seller.shopee.co.id/edu)

#### [Seller Education Hub (Philippines)](https://seller.shopee.ph/edu)

#### [Seller Education Hub (Brazil)](https://seller.shopee.com.br/edu)

#### [Seller Education Hub (Japan)](https://shopee.jp/edu)

#### [Seller Education Hub (Korea)](https://shopee.kr/edu)

#### [Seller Education Hub (Hongkong)](https://shopee.com.hk/edu)

#### [虾皮卖家学习中心](https://shopee.cn/edu)

### Support

#### [Announcement](https://open.shopee.com/announcements)

#### [FAQ](https://open.shopee.com/faq)

#### [Raise Ticket](https://open.shopee.com/console/raise-ticket)

Copyright @ Shopee 2025