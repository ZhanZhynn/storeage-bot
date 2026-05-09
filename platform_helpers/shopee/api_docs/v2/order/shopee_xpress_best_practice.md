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


Shopee Xpress - Package-free Integration Guide


Shopee Xpress - Package-free Integration Guide

1.Terminology


1.Terminology

2.Business Operation Logic


2.Business Operation Logic

3.Query item’s Unpackaged SKU ID


3.Query item’s Unpackaged SKU ID

4.Obtain order information and detail


4.Obtain order information and detail

5.Basic Shipping Logic


5.Basic Shipping Logic

6.Other Process


6.Other Process

7.Recommended API Call Flow


7.Recommended API Call Flow

8.FAQ


8.FAQ

9.Data Definition


9.Data Definition

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

# Shopee Xpress - Package-free Integration Guide

Last Updated: 2026-02-10


Language Supported:
English /

简体中文 /

繁體中文


## 1.Terminology

- Shopee Xpress - Package-free: logistics channel ID 30029
- Unpackage sku id: Unique item identifier used for this logistics channel.
- Unpackage shipment label: The label that is used for attached on the item when shipping with this logistics channel.
- TO label: The label that is used for attached on the shipping carton when shipping with this logistics channel.
- Sorting group: The value that is used for sellers to pack the item together when shipping with this logistics channel.

## 2.Business Operation Logic

2.1 Automatic Order Splitting

For orders with logistics channel 30029, when the order status becomes "READY\_TO\_SHIP", the system will automatically split the order into multiple packages based on the quantity of each item (Quantity Level).

For example, if an order contains 3 bottles of milk tea and 2 bottles of black tea, the system will automatically split it into 5 packages, each containing 1 quantity.

2.2 Arrange Shipment Process

When using logistics channel 30029 to ship items, sellers no longer need to pack by order level. The steps are:

1) Attach the Unpackage shipment label to each item

2) Pack items together in a shipping carton by sorting\_group and attach the TO Label on the shipping carton

Please refer to the Seller Education Hub article for more detail: [【蝦皮店到店-環保無包裝】出貨流程教學](https://seller.shopee.tw/edu/article/24913)

## 3.Query item’s Unpackaged SKU ID

The Unpackaged SKU ID is the unique identifier for the item under this logistics channel. You can obtain the information through the following API when item enabled logistic channel 30029:

- [v2.product.search\_unpackaged\_model\_list](https://open.shopee.com/documents/v2/v2.product.search_unpackaged_model_list?module=89&type=1)

## 4.Obtain order information and detail

Note: The logistics channel 30029 automatically splits orders. Be sure to get package level information while using the following APIs to avoid missing details.

- [v2.order.search\_package\_list](https://open.shopee.com/documents/v2/v2.order.search_package_list?module=94&type=1)：To query the package list.
- [v2.order.get\_package\_detail](https://open.shopee.com/documents/v2/v2.order.get_package_detail?module=94&type=1)：To query the package information.
- [v2.order.get\_order\_detail](https://open.shopee.com/documents/v2/v2.order.get_order_detail?module=94&type=1)：To query the order information, please ensure “package\_list” is included in the request parameter “response\_optional\_fields”.

\*When the PackageFulfillmentStatus of packages with this logistics channel changes to “LOGISTICS\_REQUEST\_CREATED” (after arrange shipment), you can obtain the value in the “sorting\_group” field.

## 5.Basic Shipping Logic

5.1 Shipment API Call Flow

Note: The logistics channel 30029 automatically splits orders, please ensure “package\_number” is included in the request parameter for following APIs.

1. Obtain shipping parameter: Call “ [v2.logistics.get\_shipping\_parameter](https://open.shopee.com/documents/v2/v2.logistics.get_shipping_parameter?module=95&type=1)” or “ [v2.logistics.get\_mass\_shipping\_parameter](https://open.shopee.com/documents/v2/v2.logistics.get_mass_shipping_parameter?module=95&type=1)” API
2. Arrange Shipment: Call “ [v2.logistics.ship\_order](https://open.shopee.com/documents/v2/v2.logistics.ship_order?module=95&type=1)” or “ [v2.logistics.mass\_ship\_order](https://open.shopee.com/documents/v2/v2.logistics.mass_ship_order?module=95&type=1)” API
3. Obtain tracking number: Call “ [v2.logistics.get\_tracking\_number](https://open.shopee.com/documents/v2/v2.logistics.get_tracking_number?module=95&type=1)” API

5.2 Obtain Unpackage shipment label call flow

Call the following APIs in sequence to obtain the Unpackage shipment label corresponding to the package:

1. [v2.logistics.get\_shipping\_document\_parameter](https://open.shopee.com/documents/v2/v2.logistics.get_shipping_document_parameter?module=95&type=1)
2. [v2.logistics.create\_shipping\_document](https://open.shopee.com/documents/v2/v2.logistics.create_shipping_document?module=95&type=1)
3. [v2.logistics.get\_shipping\_document\_result](https://open.shopee.com/documents/v2/v2.logistics.get_shipping_document_result?module=95&type=1)
4. [v2.logistics.download\_shipping\_document](https://open.shopee.com/documents/v2/v2.logistics.download_shipping_document?module=95&type=1)

The order for this logistics channel only supports "THERMAL\_UNPACKAGED\_LABEL" as the "shipping\_document\_type".

5.3 Obtain TO label call flow

After completing the packing according to the sorting group, you can obtain the TO label file through the following API:

- [v2.logistics.download\_to\_label](https://open.shopee.com/documents/v2/v2.logistics.download_to_label?module=95&type=1)

Please note that each TO label is unique. Ensure that each TO label is obtained by independently calling this API, as duplicate packing lists will affect the drop-off process.

## 6.Other Process

6.1 Pre-printing Unpackage shipment label before order creation

We support pre-printing Unpackage shipment label for items even before order creation, for advanced labeling and preparation

You can obtain the file by calling the following APIs in sequence:

1. [v2.logistics.create\_shipping\_document\_job](https://open.shopee.com/documents/v2/v2.logistics.create_shipping_document_job?module=95&type=1): Create a print job
2. [v2.logistics.get\_shipping\_document\_job\_status](https://open.shopee.com/documents/v2/v2.logistics.get_shipping_document_job_status?module=95&type=1): Get the job status
3. [v2.logistics.download\_shipping\_document\_job](https://open.shopee.com/documents/v2/v2.logistics.download_shipping_document_job?module=95&type=1): Download the label files

Please note that the item must have logistics channel 30029 enabled to use this process for calling the API.

(\*Starting from 2026/01/12, shops must use the "Unpackaged sku id" shipment label mode in order to use this process. If the shop is using the "Tracking Number" shipment label mode, this process will not provide a usable label.)

6.2 Self-Design Unpackage hipment label

In this logistics option, we recommend that you design the Unpackage shipment label according to sellers’ preferences. You can refer to the "custom fields" section specifications in the [FAQ](https://open.shopee.com/faq/279) attachment to create labels tailored to each seller's needs.

- [v2.logistics.get\_shipping\_document\_data\_info](https://open.shopee.com/documents/v2/v2.logistics.get_shipping_document_data_info?module=95&type=1): For orders using B2C logistics, you can obtain the "unpackaged\_sku\_id" and "unpackaged\_sku\_id\_qrcode" fields through this API.
- Guidelines (for reference only, the official specifications are in the [FAQ](https://open.shopee.com/faq/279) on the Open Platform website)

  - QR Code Generation Rules:

    - ECI mode is not allowed.
    - Avoid embedding UTF-8 or other encoding declarations in the QR code.

  - Custom Area Display Rules:

    - Font size and line-break restrictions have been removed.
    - Ensure that custom areas do not affect the display or layout of non-custom areas.

## 7.Recommended API Call Flow

7.1 Printing Unpackage shipment label after order creation

![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=gmp8Yaf%2BAd0cUw8hjvSD6ka4IJ7KHtGtlvUbmv5tQ3dAgOYw70brmf13MwIYphkB6D%2BqGP65L9SVOfmCZvFeYw%3D%3D&image_type=jpg)

7.2 Pre-printing Unpackage shipment label before order creation

\*If the shop is using the "Tracking Number" shipment label mode, this process cannot be used.

![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=VFVDZrjdvG26scOfRf9Miw23YTBsjwvb4txaTPFlBuIDcrpYvIpJw2vfSGSNHppPppImWDY9G5GqCbCmQXcfKw%3D%3D&image_type=jpg)

## 8.FAQ

Q: For orders under this logistics channel with multiple packages, when the logistics statuses of the packages differ, how will the order status be displayed?

A: Please to this FAQ for detail: [https://open.shopee.com/faq/510](https://open.shopee.com/faq/510)

—-—-—-—-—-—-

Q: Why is the "shipping\_carrier" field at the outer level empty when I retrieve order details through the "v2.order.get\_order\_detail" API?

A: Orders under this logistics channel will be automatically split, and the "shipping\_carrier" field at the outer level of the "v2.order.get\_order\_detail" API will not display a value. Please retrieve the "shipping\_carrier" field from each package in the "package\_list."

—-—-—-—-—-—-

Q: Why does the system return an error message when I call the Shipment or Unpackage shipment label API?

A: This logistics channel will automatically split orders. Please ensure that the "package\_number" field parameter is included in the request when calling logistics-related APIs.

# 9.Data Definition

Please refer to the [V2.0 Data Definition](https://open.shopee.com/developer-guide/31) page.

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