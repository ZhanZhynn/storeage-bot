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


Stock & Price Management


Stock & Price Management

1\. Getting product price


1\. Getting product price

2\. Updating product price


2\. Updating product price

3\. Updating global product price


3\. Updating global product price

4\. Getting product stock


4\. Getting product stock

5\. Updating product stock


5\. Updating product stock

6\. Updating global product stock


6\. Updating global product stock

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

# Stock & Price Management

Last Updated: 2024-03-17


Language Supported:
English /

简体中文 /

繁體中文 /

Português (Brasil) /

ไทย


# 1\. Getting product price

- If a product has no variants, please use [v2.product.get\_item\_base\_info](https://open.shopee.com/documents/v2/v2.product.get_item_base_info?module=89&type=1) API to get price information.
- If a product has variants, please use [v2.product.get\_model\_list](https://open.shopee.com/documents/v2/v2.product.get_model_list?module=89&type=1) API to get price information.

API response:

"price\_info": \[\
\
                    {\
\
                        "current\_price": 7678,\
\
                        "original\_price": 13960,\
\
                        "inflated\_price\_of\_current\_price": 9137,\
\
                        "inflated\_price\_of\_original\_price": 16612,\
\
                        "currency": "COP"\
\
                    }\
\
Please note that:\
\
1\. If your product has ongoing promotion, current\_price will show the promotion price during the promotion period. If not, current\_price=original\_price. original\_price indicates the original price of the product.\
\
2.If your product has multiple promotions, you can get each promotion price through [v2.product.get\_item\_promotion](https://open.shopee.com/documents/v2/v2.product.get_item_promotion?module=89&type=1) API.\
\
3\. If you are an ID / CO / PL seller, inflated\_price\_of\_current\_price/inflated\_price\_of\_original\_price means the price with tax; if you are a seller from other regions, inflated\_price\_of\_current\_price=current\_price, inflated\_price\_of\_original\_price=original\_price.\
\
# 2\. Updating product price\
\
API: [v2.product.update\_price](https://open.shopee.com/documents/v2/v2.product.update_price?module=89&type=1)\
\
- If a product has variants, you can upload multiple variants of this product to update the price in one call.\
- This API only supports updating one item\_id in one call. if you need to update more than one item\_id, you can request them multiple times.\
- Please check that the range of price can be updated by price\_limit in the [v2.product.get\_item\_limit](https://open.shopee.com/documents/v2/v2.product.get_item_limit?module=89&type=1) API.\
\
2.1 Example of updating the price of a product without variants.\
\
{\
\
"item\_id": 1000,\
\
"price\_list": \[{"original\_price": 11.11}\]\
\
}\
\
2.2 Example of updating the price of a product with variants.\
\
{\
\
"item\_id": 2000,\
\
"price\_list": \[{"model\_id": 3456, "original\_price": 11.11}, {"model\_id": 1234, "original\_price": 22.22}\]\
\
}\
\
Note that if you are an ID / CO / PL seller, the original\_price is updated to be the untaxed price.\
\
# 3\. Updating global product price\
\
\*The following is only applicable to cross-border sellers who have upgraded CNSC/KRSC.\
\
API: [v2.global\_product.update\_price](https://open.shopee.com/documents/v2/v2.global_product.update_price?module=90&type=1)\
\
- If a global product has variants, you can update the price of multiple variants of this global product in one call.\
- This API only supports updating one global\_item\_id in one call, if you need to update more than one global\_item\_id, you can request it multiple times.\
- For the price of the global product, please check the price currency first through the [v2.merchant.get\_merchant\_info](https://open.shopee.com/documents/v2/v2.merchant.get_merchant_info?module=93&type=1) API.\
- If you want the price of global products automatically synchronized to shop products, please set the price synchronization toggle open through the [v2.global\_product.set\_sync\_field](https://open.shopee.com/documents/v2/v2.global_product.set_sync_field?module=90&type=1) API . Shopee will automatically update based on the formula. If not, you can update the price through [v2.product.update\_price](https://open.shopee.com/documents/v2/v2.product.update_price?module=89&type=1) API.\
\
# 4\. Getting product stock\
\
- If a product has no variants, please use [v2.product.get\_item\_base\_info](https://open.shopee.com/documents/v2/v2.product.get_item_base_info?module=89&type=1) API to get the stock information.\
- If a product has variants, please use [v2.product.get\_model\_list](https://open.shopee.com/documents/v2/v2.product.get_model_list?module=89&type=1) API to get the stock information.\
\
API response:\
\
Json\
\
```\
{\
\
                "stock_info_v2": {\
\
                    "summary_info": {\
\
                        "total_reserved_stock": 0,\
\
                        "total_available_stock": 389\
\
                    },\
\
                    "seller_stock": [\
\
                        {\
\
                            "location_id": "IDZ",\
\
                            "stock": 90\
\
                        }\
\
                    ],\
\
                    "shopee_stock": [\
\
                        {\
\
                            "location_id": "IDG",\
\
                            "stock": 99\
\
                        },\
\
                        {\
\
                            "location_id": "IDM",\
\
                            "stock": 200\
\
                        }\
\
                    ]\
\
                }\
\
            }\
```\
\
Please note:\
\
- Product may have both seller\_stock and shopee\_stock, or it may have stock from multiple locations.\
- For more stock calculation logic, please refer to the [FAQ](https://open.shopee.com/faq?top=162&sub=166&page=1&faq=230)\
\
# 5\. Updating product stock\
\
API: [v2.product.update\_stock](https://open.shopee.com/documents/v2/v2.product.update_stock?module=89&type=1)\
\
- If a product has variants, you can upload multiple variants of this product to update the stock in one call.\
- This API only supports updating one item\_id in one call, if you need to update more than one item\_id, you can request it multiple times.\
- Sellers can only update seller\_stock, cannot update shopee\_stock.\
- Please check the stock\_limit in the [v2.product.get\_item\_limit](https://open.shopee.com/documents/v2/v2.product.get_item_limit?module=89&type=1) API for the range of stock that can be updated.\
\
5.1 Example of updating the stock of a product with no variants.\
\
{\
\
"item\_id": 1000,\
\
"stock\_list": \[{"seller\_stock": \[{"stock": 100}\]}\]\
\
}\
\
5.2 Example of updating the stock of a product with variants.\
\
{\
\
"item\_id": 2000,\
\
"stock\_list": \[{"model\_id": 3456, "seller\_stock": \[{"stock": 100}\]}, {"model\_id": 1234, "seller\_stock": \[{"stock": 100}\]}\]\
\
}\
\
Please note：\
\
- If a product has variants, the price difference between the variations cannot exceed a certain multiple. For example, BR product, the price of the most expensive variations divided by the price of the cheapest variations cannot exceed 4.\
\
|     |     |\
| --- | --- |\
| Region | multiple |\
| BR | 4 |\
| SG/VN/TW/TH/PH/MX | 5 |\
| ID/MY | 7 |\
| CL/CO | 9 |\
| CNSC | 7 |\
\
- The product participates in certain promotion, sellers are not allow to modify the original price of the product. More detail please check FAQ: [https://open.shopee.com/faq/140](https://open.shopee.com/faq/140)\
\
# 6\. Updating global product stock\
\
\*The following is only applicable to cross-border sellers who have upgraded CNSC/KRSC.\
\
API: [v2.global\_product.update\_stock](https://open.shopee.com/documents/v2/v2.global_product.update_stock?module=90&type=1)\
\
- If a global product has variants, you can update the stock of multiple variants of the global product in one call.\
- Since cross-border sellers who have upgraded CNSC/KRSC can only manage shop product stock through global product, it means you can only call the [v2.global\_product.update\_stock](https://open.shopee.com/documents/v2/v2.global_product.update_stock?module=90&type=1) API to update stock. After updating global product stock, it will be automatically synchronized to shop products. Using the [v2.product.update\_stock](https://open.shopee.com/documents/v2/v2.product.update_stock?module=89&type=1) API to update the stock will result in an error.\
- This API only supports updating one global\_item\_id at a time, if you need to update more than one global\_item\_id, you can request it multiple times.\
- Please check the stock\_limit in the [v2.global\_product.get\_global\_item\_limit](https://open.shopee.com/documents/v2/v2.global_product.get_global_item_limit?module=90&type=1) API for the range of stock that can be updated.\
\
### User Guide\
\
#### [Developer Guide](https://open.shopee.com/developer-guide/0)\
\
#### [API reference](https://open.shopee.com/documents/v2/v2.ams.get_open_campaign_added_product?module=127&type=1)\
\
#### [Push Mechanism](https://open.shopee.com/push-mechanism/5)\
\
#### [Shopee Open Platform Data Protection Policy](https://open.shopee.com/policy?policy_id=1)\
\
### Shopee Markets\
\
#### [Service Market](https://service.shopee.cn/)\
\
#### [Seller Education Hub (Singapore)](https://seller.shopee.sg/edu)\
\
#### [Seller Education Hub (Malaysia)](https://seller.shopee.com.my/edu)\
\
#### [Seller Education Hub (Thailand)](https://seller.shopee.co.th/edu)\
\
#### [Seller Education Hub (Vietnam)](https://banhang.shopee.vn/edu)\
\
#### [Seller Education Hub (Indonesia)](https://seller.shopee.co.id/edu)\
\
#### [Seller Education Hub (Philippines)](https://seller.shopee.ph/edu)\
\
#### [Seller Education Hub (Brazil)](https://seller.shopee.com.br/edu)\
\
#### [Seller Education Hub (Japan)](https://shopee.jp/edu)\
\
#### [Seller Education Hub (Korea)](https://shopee.kr/edu)\
\
#### [Seller Education Hub (Hongkong)](https://shopee.com.hk/edu)\
\
#### [虾皮卖家学习中心](https://shopee.cn/edu)\
\
### Support\
\
#### [Announcement](https://open.shopee.com/announcements)\
\
#### [FAQ](https://open.shopee.com/faq)\
\
#### [Raise Ticket](https://open.shopee.com/console/raise-ticket)\
\
Copyright @ Shopee 2025