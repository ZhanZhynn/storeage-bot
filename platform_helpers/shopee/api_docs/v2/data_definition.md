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


Getting Started


Getting Started

>


V2.0 Data Definition


V2.0 Data Definition

Basic Data Type


Basic Data Type

OrderStatus


OrderStatus

ReturnStatus


ReturnStatus

ReturnSolution


ReturnSolution

ReturnReason


ReturnReason

LogisticsStatus


LogisticsStatus

PackageFulfillmentStatus


PackageFulfillmentStatus

ReturnDisputeReasonId


ReturnDisputeReasonId

AttributeType


AttributeType

AttributeInputTypeEdit


AttributeInputTypeEdit

CancelReason（Seller）


CancelReason（Seller）

FeeType


FeeType

PaymentMethod


PaymentMethod

CancelReason


CancelReason

ShippingDocumentType


ShippingDocumentType

ItemStatus


ItemStatus

StockType


StockType

Language


Language

PromotionType


PromotionType

BuyerCancelReason


BuyerCancelReason

TrackingLogisticsStatus


TrackingLogisticsStatus

SellerProofStatus


SellerProofStatus

TransactionType


TransactionType

SellerCompensationStatus


SellerCompensationStatus

NegotiationStatus


NegotiationStatus

Return Refund Request Type


Return Refund Request Type

Validation Type


Validation Type

Reverse Logistics Status


Reverse Logistics Status

\[Normal Return\]


\[Normal Return\]

\[In-transit RR\]


\[In-transit RR\]

\[Return-on-the-Spot\]


\[Return-on-the-Spot\]

Post Return Logistics Status


Post Return Logistics Status

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

# V2.0 Data Definition

Last Updated: 2026-03-17


Language Supported:
English /

繁體中文 /

Português (Brasil) /

ไทย


# Basic Data Type

- uint8: 8 bit unsigned integer
- uint16: 16 bit unsigned integer
- int32: 32 bit signed integer
- uint32: 32 bit unsigned integer
- uint64: 64 bit unsigned integer
- timestamp: uint32
- country: ISO ALPHA-2 Code, string of 2 characters

# OrderStatus

- UNPAID:Order is created, buyer has not paid yet.
- PENDING: Order is pending and cannot proceed to shipment arrangement yet.
- READY\_TO\_SHIP:Seller can arrange shipment.
- PROCESSED:Seller has arranged shipment online and got tracking number from 3PL.
- RETRY\_SHIP:3PL pickup parcel fail. Need to re arrange shipment.
- SHIPPED:The parcel has been drop to 3PL or picked up by 3PL.
- TO\_CONFIRM\_RECEIVE:The order has been received by buyer.
- IN\_CANCEL:The order's cancelation is under processing.
- CANCELLED:The order has been canceled.
- TO\_RETURN:The buyer requested to return the order and order's return is processing.
- COMPLETED:The order has been completed.

# ReturnStatus

- REQUESTED
- ACCEPTED
- CANCELLED
- JUDGING
- CLOSED
- PROCESSING
- SELLER\_DISPUTE

# ReturnSolution

- RETURN\_REFUND
- REFUND

# ReturnReason

- NONRECEIPT
- WRONG\_ITEM
- ITEM\_DAMAGED
- DIFF\_DESC
- MUITAL\_AGREE
- OTHER
- USED
- NO\_REASON
- ITEM\_WRONGDAMAGED
- CHANGE\_MIND
- ITEM\_MISSING
- EXPECTATION\_FAILED
- ITEM\_FAKE
- PHYSICAL\_DMG
- FUNCTIONAL\_DMG
- ITEM\_NOT\_FIT
- SUSPICIOUS\_PARCEL
- EXPIRED\_PRODUCT
- WRONG\_ORDER\_INFO
- WRONG\_ADDRESS
- CHANGE\_OF\_MIND
- SELLER\_SENT\_WRONG\_ITEM
- SPILLED\_CONTENTS
- BROKEN\_PRODUCTS
- DAMAGED\_PACKAGE
- SCRATCHED
- DAMAGED\_OTHERS
- SIZE\_DEVIATION
- LOOK\_DEVIATION
- DATE\_DEVIATION
- DIFFERENT\_DESCRIPTION

# LogisticsStatus

- LOGISTICS\_NOT\_START:Initial status, order not ready for fulfillment
- LOGISTICS\_PENDING\_ARRANGE:order logistics pending arrangement
- LOGISTICS\_COD\_REJECTED:Integrated logistics COD: Order rejected for COD
- LOGISTICS\_READY:order ready for fulfillment from payment perspective:non-COD: order paidCOD: order passed COD screening
- LOGISTICS\_REQUEST\_CREATED:order arranged shipment
- LOGISTICS\_PICKUP\_DONE:order handed over to 3PL
- LOGISTICS\_DELIVERY\_DONE:order successfully delivered
- LOGISTICS\_INVALID:order cancelled when order at LOGISTICS\_READY
- LOGISTICS\_REQUEST\_CANCELED:order cancelled when order at LOGISTICS\_REQUEST\_CREATED
- LOGISTICS\_PICKUP\_FAILED:order cancelled by 3PL due to failed pickup or picked up but not able to proceed with delivery
- LOGISTICS\_PICKUP\_RETRY:order pending 3PL retry pickup
- LOGISTICS\_DELIVERY\_FAILED:order cancelled due to 3PL delivery failed
- LOGISTICS\_LOST:order cancelled due to 3PL lost the order

# PackageFulfillmentStatus

- LOGISTICS\_NOT\_START: Initial status, package not ready for fulfillment
- LOGISTICS\_READY: Package ready for fulfillment from payment perspective. For non-COD: paid; forCOD: passed COD screening
- LOGISTICS\_REQUEST\_CREATED: Package arranged shipment
- LOGISTICS\_PICKUP\_DONE: Package handed over to 3PL
- LOGISTICS\_DELIVERY\_DONE: Package successfully delivered
- LOGISTICS\_INVALID: Order cancelled when package at LOGISTICS\_READY
- LOGISTICS\_REQUEST\_CANCELED: Order cancelled when package at LOGISTICS\_REQUEST\_CREATED
- LOGISTICS\_PICKUP\_FAILED: Order cancelled by 3PL due to failed pickup or picked up but not able to proceed with delivery
- LOGISTICS\_PICKUP\_RETRY: Package pending 3PL retry pickup
- LOGISTICS\_DELIVERY\_FAILED: Order cancelled due to 3PL delivery failed
- LOGISTICS\_LOST: Order cancelled due to 3PL lost the Package

# ReturnDisputeReasonId

- "1": "I would like to reject the non-receipt claim"
- "2": "I would like to reject the return request"
- "3": "I agree with the return request, but I did not receive the product(s) which was/were supposed to be"
- "4": "未收到退貨"
- "5": "商品毀損/瑕疵"
- "6": "商品缺件/不符"
- "7": "非鑑賞期商品"
- "8": "其他"
- "9": "I have shipped the item(s) and have proof of shipment"
- "10": "I shipped the correct item(s) as buyer ordered"
- "11": "I shipped the item(s) in good working condition"
- "12": "I agreed with the return request, but I have not received the item(s) that was/were supposed to be returned"
- "13": "I agreed with the return request, but I received wrong/damaged item(s) from buyer"
- "41": "I have shipped the item(s) and have proof of shipment"
- "42": "I shipped the correct item(s) as buyer ordered"
- "43": "I shipped the item(s) in good working condition"
- "44": "Unable to come to an agreement with buyer"
- "45": "Products are not in the appreciation period"
- "46": "Did not receive the return product"
- "47": "Received return products with physical damage"
- "48": "Received incomplete return products (missing quantity/accessories)"
- "49": "Received wrong return product"
- "50": "Received return item(s), buyer's claim incorrect"
- "51": "Unable to come to an agreement with seller"
- "53": "Buyer’s claim is incorrect"
- "54": "Buyer has been refunded wrong amount"
- "55": "Buyer claim is correct, but I have other concerns"
- "56": "Received return item(s), but item is used"
- "81": "Did not receive the return product"
- "82": "Received return products with physical damage"
- "83": "Received incomplete return products (missing quantity/accessories)"
- "84": "Received wrong return product"
- "85": "Products are not in the appreciation period"
- "86": "Received return item(s), buyer's claim incorrect"
- "87": "The product(s) returned is excluded from buyer's statutory right of withdrawal"
- "88": "Buyer was unresponsive in Seller Arrange Return"
- "89": "Received return item(s), but item is used"

# AttributeType

- INT\_TYPE
- STRING\_TYPE
- ENUM\_TYPE
- FLOAT\_TYPE
- DATE\_TYPE
- TIMESTAMP\_TYPE

# AttributeInputTypeEdit

- DROP\_DOWN
- TEXT\_FILED
- COMBO\_BOX
- MULTIPLE\_SELECT
- ﻿MULTIPLE\_SELECT\_COMBO\_BOX

For more details, please check: [https://open.shopee.com/faq?top=162&sub=166&page=1&faq=195](https://open.shopee.com/faq?top=162&sub=166&page=1&faq=195)

# CancelReason（Seller）

- OUT\_OF\_STOCK
- UNDELIVERABLE\_AREA (only for TW and MY)

# FeeType

- SIZE\_SELECTION
- SIZE\_INPUT
- FIXED\_DEFAULT\_PRICE
- CUSTOM\_PRICE
- SELLER\_LOGISTICS

# PaymentMethod

- Cybersource \[ID, VN, TW, SG, MY, TH, PH\]
- Nicepay Credit Card \[ID\]
- IPay88 Credit Card \[MY\]
- Airpay Credit Card \[PH\]
- Stripe CC \[PH\]
- Airpay Credit Card \[ID, VN, TW, TH\]
- Bank Transfer \[ID\]
- Bank BCA (Manual Transfer) \[ID\]
- Bank Mandiri (Manual Transfer) \[ID\]
- Bank BNI (Manual Transfer) \[ID\]
- Bank BRI (Manual Transfer) \[ID\]
- Bank CIMB Niaga (Manual Transfer) \[ID\]
- Bank Transfer \[VN\]
- Fubon Bank Transfer \[TW\]
- Esun Bank Transfer \[TW\]
- Bank Transfer \[TW\]
- Esun CB Bank Transfer \[TW\]
- Bank Transfer \[SG\]
- Bank Transfer \[MY\]
- ATM Payment \[TH\]
- ATM Payment (BBL) \[TH\]
- Bank Transfer \[TH\]
- ATM Payment (KBANK) \[TH\]
- ATM Payment (KTB) \[TH\]
- ATM Payment (SCB) \[TH\]
- ATM Payment (BAY) \[TH\]
- Online Payment (KBANK) \[TH\]
- Online Payment (BAY) \[TH\]
- Bank Transfer \[PH\]
- Cash on Delivery \[ID, VN, SG, MY, TH, PH\]
- 現付 \[TW\]
- Shopee Seller Wallet \[ID\]
- Shopee Wallet \[ID, VN, TW, SG, MY, TH, PH\]
- Indomaret \[ID\]
- Bank BRI (Virtual Account) \[ID\]
- Bank BCA (Virtual Account) \[ID\]
- Bank Mandiri (Virtual Account) \[ID\]
- Bank BNI (Virtual Account) \[ID\]
- Virtual Account Parent \[ID\]
- Android Pay \[SG\]
- MOLPay \[MY\]
- iPay 88 \[MY\]
- iBanking Payment \[TH\]
- iBanking Payment (BBL) \[TH\]
- iBanking Payment (KTB) \[TH\]
- iBanking Payment (SCB) \[TH\]
- Dragonpay - Remittance Center \[PH\]
- Dragonpay - OTC \[PH\]
- Dragonpay - Online Payment \[PH\]
- Buyer-Seller Self Arrange \[ID, VN, TW, SG, MY, TH, PH\]
- Kredivo \[ID\]
- Kredivo - BNPL \[ID\]
- Kredivo - 3 Months Installment \[ID\]
- Kredivo - 6 Months Installment \[ID\]
- Kredivo - 12 Months Installment \[ID\]
- Nicepay Credit Card Installment \[ID\]
- BCA One Klik \[ID\]
- Akulaku \[ID\]
- Free \[Vn, TW, SG, MY, TH, PH\]
- iPay88 CC Installment \[MY\]
- Ebanx Credit Card \[BR\]
- Ebanx Credit Card Installment \[BR\]
- Ebanx Credit Card Installment 1x installment plan \[BR\]
- Ebanx Credit Card Installment 2x installment plan \[BR\]
- Ebanx Credit Card Installment 3x installment plan \[BR\]
- Ebanx Credit Card Installment 4x installment plan \[BR\]
- Ebanx Credit Card Installment 5x installment plan \[BR\]
- Ebanx Credit Card Installment 6x installment plan \[BR\]
- Ebanx Boleto \[BR\]

# CancelReason

- Out of Stock
- Buyer Request to Cancel
- Undeliverable Area
- COD Unsupported
- Parcel is Lost
- Game Completed
- Unpaid Order
- Underpaid Order
- Unsuccessful / Rejected Payment
- Logistics Request is Cancelled
- 3PL pickup Fail
- Failed Delivery
- COD Rejected
- Seller did not Ship
- Transit Warehouse Cancelled
- Other
- Inactive Seller
- Auto Cancel
- Logistic Issue
- Your approver did not approve order on time.
- You are unable to place order at the moment.
- TBC

# ShippingDocumentType

- NORMAL\_AIR\_WAYBILL
- THERMAL\_AIR\_WAYBILL
- NORMAL\_JOB\_AIR\_WAYBILL
- THERMAL\_JOB\_AIR\_WAYBILL

# ItemStatus

- NORMAL
- BANNED
- UNLIST
- REVIEWING
- SELLER\_DELETE
- SHOPEE\_DELETE

# StockType

- 1: Shopee Warehouse Stock
- 2: Seller Stock

# Language

- zh-hans
- zh-hant
- ms-my
- en-my
- en
- id
- vi
- th
- pt-br
- es-mx
- pl
- es-CO
- es-CL
- es-ES
- es-ar

# PromotionType

- Campaign
- Discount Promotions
- Flash Sale
- Whole Sale
- Group Buy
- Bundle Deal
- Welcome Package
- Add-on Discount
- Brand Sale
- In ShopFlash Sale
- Gift with purchase
- ﻿Exclusive Price
- Platform Streaming
- Seller Streaming

# BuyerCancelReason

- Seller is not Responsive to buyer's Inquires
- Seller ask Buyer to Cancel
- Modify Existing Order
- Product has Bad Reviews
- Seller Takes too Long to Ship The Order
- Seller is Untrustworthy
- Others
- Forgot to Input Voucher Code
- Need to change delivery address
- Need to Change Delivery Address
- Need to input / Change Voucher Code
- Need to Modify Order
- Payment Procedure too Troublesome
- Found Cheaper Elsewhere
- Don't Want to Buy Anymore
- Your approver rejected the order.
- You are unable to place order at the moment.
- Need to change delivery address
- Too long delivery time
- Modify existing order (color, size, voucher, etc)
- Change of mind / others

# TrackingLogisticsStatus

- INITIAL
- ORDER\_INIT
- ORDER\_SUBMITTED
- ORDER\_FINALIZED
- ORDER\_CREATED
- PICKUP\_REQUESTED
- PICKUP\_PENDING
- PICKED\_UP
- DELIVERY\_PENDING
- DELIVERED
- PICKUP\_RETRY
- TIMEOUT
- LOST
- UPDATE
- UPDATE\_SUBMITTED
- UPDATE\_CREATED
- RETURN\_STARTED
- RETURNED
- RETURN\_PENDING
- RETURN\_INITIATED
- EXPIRED
- CANCEL
- CANCEL\_CREATED
- CANCELED
- FAILED\_ORDER\_INIT
- FAILED\_ORDER\_SUBMITTED
- FAILED\_ORDER\_CREATED
- FAILED\_PICKUP\_REQUESTED
- FAILED\_PICKED\_UP
- FAILED\_DELIVERED
- FAILED\_UPDATE\_SUBMITTED
- FAILED\_UPDATE\_CREATED
- FAILED\_RETURN\_STARTED
- FAILED\_RETURNED
- FAILED\_CANCEL\_CREATED
- FAILED\_CANCELED

# SellerProofStatus

- NOT\_NEEDED
- PENDING
- UPLOADED
- OVERDUE

# TransactionType

- ESCROW\_VERIFIED\_ADD = 101;  // Escrow has been verified and paid to seller.
- ESCROW\_VERIFIED\_MINUS = 102; // Escrow has been verified and charged from seller as escrow amount is negative.
- WITHDRAWAL\_CREATED = 201; // The seller has created a withdrawal, so it’s deducted from balance.
- WITHDRAWAL\_COMPLETED = 202; // The withdrawal has been completed, so the ongoing amount decreases.
- WITHDRAWAL\_CANCELLED = 203; // The withdrawal has been canceled, so the amount is added back to the seller balance. Ongoing amount decreases as well.
- REFUND\_VERIFIED\_ADD = 301; //  Normal Order Refund.
- AUTO\_REFUND\_ADD=302; // Normal Order Auto Refund.
- ADJUSTMENT\_ADD = 401; // One adjustment item has been paid to seller.
- ADJUSTMENT\_MINUS = 402; // One adjustment item has been charged from seller.
- FBS\_ADJUSTMENT\_ADD = 404; //One adjustment item related to Shopee fulfillment order is added to seller.
- FBS\_ADJUSTMENT\_MINUS = 405; // One adjustment item related to Shopee fulfillment order is deducted from seller.
- ADJUSTMENT\_CENTER\_ADD = 406; // One adjustment item has been added to seller wallet.
- ADJUSTMENT\_CENTER\_DEDUCT = 407; // One adjustment item has been deducted from seller wallet.
- ESCROW\_ADJUSTMENT\_FOR\_FD\_DEDUCT = 408; // FSF cost passing for canceled/invalid orders.
- PERCEPTION\_VAT\_TAX\_DEDUCT = 409; // Extra charge for perception regime VAT tax (Argentina).
- ADJUSTMENT\_FOR\_RR\_AFTER\_ESCROW\_VERIFIED = 411;// RR adjustment after escrow verified (seller received the parcels), deduct.
- AFFILIATE\_COMMISSION\_FEE\_ADD = 412; // To credit Seller affiliate commission into seller wallet.
- CROSS\_MERCHANT\_ADJUSTMENT\_ADD = 413;// Automated positive wallet adjustment to FBS/B2C wallets based on the escrow amount owned by the FBS/B2C shop in a specific cross listed order.
- CROSS\_MERCHANT\_ADJUSTMENT\_DEDUCT = 414; // Automated negative wallet adjustment to FBS/B2C wallets based on the escrow amount owned by the FBS/B2C shop in a specific cross listed order.
- SELLER\_COMPENSATE\_ADD = 415; // In the new RR flow, buyers will get the benefit of auto and accelerated refunds, where Shopee can accept the refunds without the seller. Subsequently, sellers can raise a compensation request if needed.This txn type is to compensate such sellers.
- CAMPAIGN\_PACKAGE\_ADD = 416; // To refund sellers who have been overcharged for their campaign fees, only for ID.
- CAMPAIGN\_PACKAGE\_MINUS = 417;// To further deduct from sellers who have been undercharged for their campaign fees, only for ID.
- PAID\_ADS\_CHARGE = 450; // Paid ads are charged from seller.
- PAID\_ADS\_REFUND = 451; // Paid ads are refunded to seller.
- FAST\_ESCROW\_DISBURSE = 452; // ADD. // The first disbursement of fast escrow has been paid to seller.
- AFFILIATE\_ADS\_SELLER\_FEE = 455; // DEDUCT // Affiliate ads seller fee is charged from seller.
- AFFILIATE\_ADS\_SELLER\_FEE\_REFUND = 456; // ADD // Affiliate ads seller fee is refunded to seller.
- FAST\_ESCROW\_DEDUCT = 458; // Fast escrow is deducted from seller balance in the event of return and refund.
- FAST\_ESCROW\_DISBURSE\_REMAIN = 459; // The second disbursement of fast escrow has been paid to seller.
- AFFILIATE\_FEE\_DEDUCT = 460; // Affiliate MKT fee is charged from seller for using affiliate MKT services.
- SHOPEE\_WALLET\_PAY = 501;// Local SIP, deduct from seller wallet.
- SPM\_DEDUCT = 502;// SPM charge seller wallet as payment.
- APM\_DEDUCT = 503;// APM charge seller wallet as payment.
- SPM\_REFUND\_ADD = 504; // Normal Order Refund.
- APM\_REFUND\_ADD = 505; // Normal Order Refund.
- DP\_REFUND\_VERIFIED\_ADD = 701; // Digital product purchase refund verified and paid to seller.
- SPM\_DEDUCT\_DIRECT = 801; // Shopee Credit Sellerloan Repayment, eg: provision channel id. 8008601
- SPM\_DISBURSE\_ADD = 802; // Sellerloan pay out to seller wallet.

# SellerCompensationStatus

- COMPENSATION\_NOT\_APPLICABLE
- COMPENSATION\_INITIAL\_STAGE
- COMPENSATION\_PENDING\_REQUEST
- COMPENSATION\_NOT\_REQUIRED
- COMPENSATION\_REQUESTED
- COMPENSATION\_APPROVED
- COMPENSATION\_REJECTED
- COMPENSATION\_CANCELLED
- COMPENSATION\_NOT\_ELIGIBLE

# NegotiationStatus

- PENDING\_RESPOND
- PENDING\_BUYER\_RESPOND
- TERMINATED

# Return Refund Request Type

- 0:  Normal RR（RR is raised by the buyer after they have received the parcel, based on estimated delivery date /delivery done ）
- 1: In-Transit RR (RR is raised by the buyer while item is still in-transit to buyer)
- 2: Return-on-the-Spot (RR is raised by the driver after buyer rejected parcel at delivery)

# Validation Type

- seller\_validation: For Return & Refund requests with return parcel that will be delivered to the seller for validation and decision whether to refund buyer or to raise dispute
- warehouse\_validation: For Return & Refund requests with return parcel that will be delivered to warehouse for validation and decision whether to refund buyer or to raise dispute

# Reverse Logistics Status

## \[Normal Return\]

- LOGISTICS\_PENDING\_ARRANGE: Return is now pending user to select shipping option. Same for both integrated logistics and non-integrated logistics.
- LOGISTICS\_READY: User has selected shipping option, and pending system to create logistics request. Tracking number is not yet available. Same for both integrated logistics and non-integrated logistics.
- LOGISTICS\_REQUEST\_CREATED: Means that the logistics request has been created successfully. Tracking number should be available
- LOGISTICS\_PICKUP\_RETRY: Third party logistics provider will make another attempt to pick up parcel from buyer. Only available for integrated logistics since this is updated by third party logistics provider back to Shopee.
- LOGISTICS\_PICKUP\_FAILED: Third party logistics provider has failed to pickup parcel from buyer. Only available for integrated logistics since this is updated by third party logistics provider back to Shopee.
- LOGISTICS\_PICKUP\_DONE: For integrated logistics, this means the parcel has been picked up by a third party logistics provider. For non-integrated logistics, this means the user has entered shipping proof.
- LOGISTICS\_DELIVERY\_FAILED: Parcel delivery to seller has failed. Only available for integrated logistics since this is updated by third party logistics provider back to Shopee.
- LOGISTICS\_LOST: Parcel has been marked as lost. Only available for integrated logistics since this is updated by third party logistics provider back to Shopee.
- LOGISTICS\_DELIVERY\_DONE: Parcel has been successfully delivered to seller. Only available for integrated logistics since this is updated by third party logistics provider back to Shopee.

## \[In-transit RR\]

- Preparing
- Delivered
- Delivery Failed
- Lost

## \[Return-on-the-Spot\]

- Preparing
- Delivered
- Delivery Failed
- Lost

# Post Return Logistics Status

Note this is only applicable to return parcels sent from warehouse back to seller

- POST\_RETURN\_LOGISTICS\_REQUEST\_CREATED: Logistics request generated successfully with tracking number.
- POST\_RETURN\_LOGISTICS\_REQUEST\_CANCELED: ​​Logistics request cancelled by warehouse team
- POST\_RETURN\_LOGISTICS\_PICKUP\_FAILED: Failed to pickup parcel
- POST\_RETURN\_LOGISTICS\_PICKUP\_RETRY: Subsequent attempt to pickup parcel.
- POST\_RETURN\_LOGISTICS\_PICKUP\_DONE: Successful pickup; on the way to destination.
- POST\_RETURN\_LOGISTICS\_DELIVERY\_FAILED: Failed delivery of parcel. Driver will return parcel back to warehouse.
- POST\_RETURN\_LOGISTICS\_DELIVERY\_DONE: Successful delivery of parcel
- POST\_RETURN\_LOGISTICS\_LOST: Parcel marked as Lost

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