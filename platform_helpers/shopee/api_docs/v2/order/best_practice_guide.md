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


Order Management


Order Management

1\. Entity


1\. Entity

2\. Order Status Flow


2\. Order Status Flow

3\. Package Fulfillment Status


3\. Package Fulfillment Status

4\. Getting order list and details


4\. Getting order list and details

5\. Canceling Order


5\. Canceling Order

6\. Splitting Order


6\. Splitting Order

6.1 Splitting


6.1 Splitting

6.2 Cancel Splitting


6.2 Cancel Splitting

7\. Getting package list and details for shipment


7\. Getting package list and details for shipment

8\. Shipment API Call Flow


8\. Shipment API Call Flow

8.1 Basic Shipping Logic


8.1 Basic Shipping Logic

8.2 Related APIs for order shipment


8.2 Related APIs for order shipment

8.3 API request example


8.3 API request example

8.3.1 v2.logistics.get\_shipping\_parameter


8.3.1 v2.logistics.get\_shipping\_parameter

8.3.2. v2.logistics.ship\_order


8.3.2. v2.logistics.ship\_order

8.3.3 v2.logistics.update\_shipping\_order


8.3.3 v2.logistics.update\_shipping\_order

9\. FAQ


9\. FAQ

Order related


Order related

Shipping related


Shipping related

Airway Bill related


Airway Bill related

10\. Data Definition


10\. Data Definition

Order Status


Order Status

Package Status


Package Status

Package Fulfillment Status / Logistics Status


Package Fulfillment Status / Logistics Status

Order cancellation reason


Order cancellation reason

Cancel reason


Cancel reason

Buyer cancel reason


Buyer cancel reason

Shipping document type


Shipping document type

Package logistics track status


Package logistics track status

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

# Order Management

Last Updated: 2025-09-24


Language Supported:
English /

简体中文 /

繁體中文 /

Português (Brasil) /

ไทย


# 1\. Entity

Order: Created after checkout. 1 order can contain multiple items.

Package: Created after the order is generated. It represents the unit for shipment. 1 order can be split into multiple packages, and 1 package can contain multiple items.

Item: The individual products within an order, with quantity and other details. Items are included in packages for shipment.

# 2\. Order Status Flow

![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=1vR037Deon1TfHF8LuX3ANMIt4KzgNbuMlngwgb4Hbsd4B3O16%2B4M8jEwiydIxZz%2F%2FUVJEd20uF1NVXqSupddw%3D%3D&image_type=png)

# 3\. Package Fulfillment Status

![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=BCF6GSGHu0RUbI5NmVvWacXLYj5%2F4qcTQYj6Vetj5cCSxI1pptmSl0NqEpjRyfx1ECiNanWrOeuDzHWETnJuGg%3D%3D&image_type=png)

# 4\. Getting order list and details

[v2.order.get\_order\_list](https://open.shopee.com/documents/v2/v2.order.get_order_list?module=94&type=1): Get the list of orders with different order status.

[v2.order.get\_order\_detail](https://open.shopee.com/documents/v2/v2.order.get_order_detail?module=94&type=1): View order details.

# 5\. Canceling Order

[v2.order.cancel\_order](https://open.shopee.com/documents/v2/v2.order.cancel_order?module=94&type=1): Used for sellers to cancel orders.

[v2.order.handle\_buyer\_cancellation](https://open.shopee.com/documents/v2/v2.order.handle_buyer_cancellation?module=94&type=1): Used to handle buyer’s cancellation requests.

# 6\. Splitting Order

### 6.1 Splitting

[v2.order.split\_order](https://open.shopee.com/documents/v2/v2.order.split_order?module=94&type=1): When an order contains multiple items, the split order function can help you arrange shipping for each item separately according to its readiness or location. Orders can be split only when the order status is "READY\_TO\_SHIP"

API request example

In this example, the order contains 6 items and is divided into two packages

Json

```

{

    "order_sn": "2204215JYEEFW0",

    "package_list": [\
\
        {\
\
            "item_list": [\
\
                {\
\
                    "item_id": 1220089094,\
\
                    "model_id": 0,\
\
                    "order_item_id": 1220089094,\
\
                    "promotion_group_id": 1051400341536827267\
\
                }\
\
            ]\
\
        },\
\
        {\
\
            "item_list": [\
\
                {\
\
                    "item_id": 2436030646,\
\
                    "model_id": 5074620257,\
\
                    "order_item_id": 2436030646,\
\
                    "promotion_group_id": 0\
\
                },\
\
                {\
\
                    "item_id": 7348262532,\
\
                    "model_id": 0,\
\
                    "order_item_id": 7348262532,\
\
                    "promotion_group_id": 0\
\
                },\
\
                {\
\
                    "item_id": 13772515222,\
\
                    "model_id": 0,\
\
                    "order_item_id": 13772515222,\
\
                    "promotion_group_id": 0\
\
                },\
\
                {\
\
                    "item_id": 1229323224,\
\
                    "model_id": 1434025516,\
\
                    "order_item_id": 1229323224,\
\
                    "promotion_group_id": 0\
\
                },\
\
                {\
\
                    "item_id": 1229323224,\
\
                    "model_id": 1434025517,\
\
                    "order_item_id": 1229323224,\
\
                    "promotion_group_id": 0\
\
                }\
\
            ]\
\
        }\
\
    ]

}
```

Tips

1. Split order permission for the shop level, If you get the error "You don't have the permission to split order." when calling the [v2.order.split\_order](https://open.shopee.com/documents/v2/v2.order.split_order?module=94&type=1) api, please contact Shopee business manager to apply.
2. Items under the same Bundle deal and add on deal promotion cannot be split into different packages. Only for selected sellers can support split bundle deal or add on deal promotions.

1. The order\_item\_id of the items in the [V2.order.get\_order\_detail](https://open.shopee.com/documents/v2/v2.order.get_order_detail?module=94&type=1) API is the same, indicating that they are in the same Bundle deal, and the add\_on\_deal\_id is the same, indicating that they are in the same add on deal.

4. If buyers buy more than one items of the same item\_id and model\_id, the order can not be split. It means we only support item level and model level splitting.Only for selected sellers can support split the same items.

eg: For example, if a buyer buys a cell phone A (blue) and a cell phone A (red), the order can be split into two packages. If you buy two cell phones A (blue), you can not split them.

4.When splitting an order, there should be at least two parcels in an order, it means at least two item\_list request. You can split the order into 30 parcels at most in TW and 5 parcels at most in other regions.

5.When splitting an order, the requested item must contain all the items in the order.

### 6.2 Cancel Splitting

[v2.order.unsplit\_order](https://open.shopee.com/documents/v2/v2.order.unsplit_order?module=94&type=1): The order status is "READY\_TO\_SHIP" before the order can be canceled splitting, if any parcel has been shipped, the order can not be splitting anymore.

# 7\. Getting package list and details for shipment

[v2.order.search\_package\_list](https://open.shopee.com/documents/v2/v2.order.search_package_list?module=94&type=1): Search package list that have not been SHIPPED to arrange shipment, with various filters and sort fields. This api is preferred to fetch packages for shipment.

[v2.order.get\_package\_detail](https://open.shopee.com/documents/v2/v2.order.get_package_detail?module=94&type=1): View package details.

# 8\. Shipment API Call Flow

![](https://open.shopee.com/opservice/api/v1/image/download/?image_id=qEuKrZQkpbJEXzXUJzaJbMxhGxHJ0LkgC4OhH4V3DrtMIbUcKCvqjpcN54zLvrBBwHMZ2jUSL0ZeIigOb2Jd0Q%3D%3D&image_type=png)

## 8.1 Basic Shipping Logic

1\. Get the list of packages to be shipped with package\_status of 2 (ToProcess) through [v2.order.search\_package\_list](https://open.shopee.com/documents/v2/v2.order.search_package_list?module=94&type=1) API.

2.Call [v2.logistics.get\_shipping\_parameter](https://open.shopee.com/documents/v2/v2.logistics.get_shipping_parameter?module=95&type=1) API to get the shipping parameters for single package (or call [v2.logistics.get\_mass\_shipping\_parameter](https://open.shopee.com/documents/v2/v2.logistics.get_mass_shipping_parameter?module=95&type=1) API to batch get the shipping parameters for multiple packages under same logistics channel and warehouse), seller choose any one of pickup/dropoff/non\_integrated shipping method to ship. Call [v2.logistics.ship\_order](https://open.shopee.com/documents/v2/v2.logistics.ship_order?module=95&type=1) to ship single package (or call [v2.logistics.mass\_ship\_order](https://open.shopee.com/documents/v2/v2.logistics.mass_ship_order?module=95&type=1) to batch ship multiple packages under same logistics channel and warehouse), for non\_integrated channel orders, the developer should prepare the tracking number and upload it in the request body. After the API call is successful, the package fulfillment status of pickup / dropoff mode will automatically update from LOGISTICS\_READY to LOGISTICS\_REQUEST\_CREATED, and for the non\_integrated mode, package fulfillment status will be immediately updated to LOGISTICS\_PICKUP\_DONE.

3.After successful shipment using the Shopee integration channel, you can call [v2.logistics.get\_tracking\_number](https://open.shopee.com/documents/v2/v2.logistics.get_tracking_number?module=95&type=1) API to get the tracking number for single package (or call [v2.logistics.get\_mass\_tracking\_number](https://open.shopee.com/documents/v2/v2.logistics.get_mass_tracking_number?module=95&type=1) API to batch get the tracking number for multiple packages.

4.After getting the tracking number, you can print the airway bill. You can choose two ways: self-print or Shopee generated. The airway bill can only be printed after the package is arranged shipment successfully and before the package fulfillment status is LOGISTICS\_PICKUP\_DONE.

5.To get the Shopee generated airway bill, you need to call these four APIs one by one. [v2.logistics.get\_shipping\_document\_parameter](https://open.shopee.com/documents/v2/v2.logistics.get_shipping_document_parameter?module=95&type=1)， [v2.logistics.create\_shipping\_document](https://open.shopee.com/documents/v2/v2.logistics.create_shipping_document?module=95&type=1)， [v2.logistics.get\_shippping\_document\_result](https://open.shopee.com/documents/v2/v2.logistics.get_shipping_document_result?module=95&type=1)， [v2.logistics.download\_shipping\_document](https://open.shopee.com/documents/v2/v2.logistics.download_shipping_document?module=95&type=1).

6.TW shipping special logic:

a.When calling the [v2.logistics.get\_shipping\_parameter](https://open.shopee.com/documents/v2/v2.logistics.get_shipping_parameter?module=95&type=1) API to get the shipping parameters, the slug parameter is returned, and the slug parameter must be uploaded when calling the [v2.logistics.ship\_order](https://open.shopee.com/documents/v2/v2.logistics.ship_order?module=95&type=1) API, otherwise the shipment will fail.

b.For the channel 黑猫宅急便(30001), there is no need to print airway bill. 3PL will provide the airway bill and complete the pickup. Calling v2.logistics.create\_shipping\_document will report an error: "The package can not print now."

## 8.2 Related APIs for order shipment

| API | Description |
| --- | --- |
| [v2.order.search\_package\_list](https://open.shopee.com/documents/v2/v2.order.search_package_list?module=94&type=1) | Get a list of packages which not shipped yet |
| [v2.order.get\_package\_detail](https://open.shopee.com/documents/v2/v2.order.get_package_detail?module=94&type=1) | Get package details |
| [v2.logistics.get\_shipping\_parameter](https://open.shopee.com/documents/v2/v2.logistics.get_shipping_parameter?module=95&type=1)[v2.logistics.get\_mass\_shipping\_parameter](https://open.shopee.com/documents/v2/v2.logistics.get_mass_shipping_parameter?module=95&type=1) | Get shipping parameters |
| [v2.logistics.ship\_order](https://open.shopee.com/documents/v2/v2.logistics.ship_order?module=95&type=1)[v2.logistics.mass\_ship\_order](https://open.shopee.com/documents/v2/v2.logistics.mass_ship_order?module=95&type=1) | Arrange shipment |
| [v2.logistics.get\_tracking\_number](https://open.shopee.com/documents/v2/v2.logistics.get_tracking_number?module=95&type=1)[v2.logistics.get\_mass\_tracking\_number](https://open.shopee.com/documents/v2/v2.logistics.get_mass_tracking_number?module=95&type=1) | Get tracking number |
| [v2.logistics.get\_shipping\_document\_data\_info](https://open.shopee.com/documents/v2/v2.logistics.get_shipping_document_data_info?module=95&type=1) | Get the information you need to self print airway bill |
| [v2.logistics.get\_shipping\_document\_parameter](https://open.shopee.com/documents/v2/v2.logistics.get_shipping_document_parameter?module=95&type=1) | Access to selectable and recommended airway bill types |
| [v2.logistics.create\_shipping\_document](https://open.shopee.com/documents/v2/v2.logistics.create_shipping_document?module=95&type=1) | Create airway bill task |
| [v2.logistics.get\_shippping\_document\_result](https://open.shopee.com/documents/v2/v2.logistics.get_shipping_document_result?module=95&type=1) | Get airway bill task result |
| [v2.logistics.download\_shipping\_document](https://open.shopee.com/documents/v2/v2.logistics.download_shipping_document?module=95&type=1) | Download Shopee generated airway bill |

## 8.3 API request example

### 8.3.1 [v2.logistics.get\_shipping\_parameter](https://open.shopee.com/documents/v2/v2.logistics.get_shipping_parameter?module=95&type=1)

Response example:

Json

```
{

    "error": "",

    "message": "",

    "response": {

        "info_needed": {

            "dropoff": [],

            "pickup": [\
\
                "address_id",\
\
                "pickup_time_id"\
\
            ]

        },

        "dropoff": {

            "branch_list": null

        },

        "pickup": {

            "address_list": [\
\
                {\
\
                    "address_id": 2826,\
\
                    "region": "TH",\
\
                    "state": "จังหวัดบึงกาฬ",\
\
                    "city": "อำเภอเมืองบึงกาฬ",\
\
                    "district": "",\
\
                    "town": "",\
\
                    "address": "222/58",\
\
                    "zipcode": "38000",\
\
                    "address_flag": [\
\
                        "default_address",\
\
                        "pickup_address",\
\
                        "return_address"\
\
                    ],\
\
                    "time_slot_list": [\
\
                        {\
\
                            "date": 1639472400,\
\
                            "pickup_time_id": "1639472400"\
\
                        },\
\
                        {\
\
                            "date": 1639558800,\
\
                            "pickup_time_id": "1639558800"\
\
                        }\
\
                    ]\
\
                },\
\
                {\
\
                    "address_id": 3019,\
\
                    "region": "TH",\
\
                    "state": "จังหวัดกระบี่",\
\
                    "city": "อำเภอคลองท่อม",\
\
                    "district": "",\
\
                    "town": "",\
\
                    "address": "home 1234",\
\
                    "zipcode": "81120",\
\
                    "address_flag": [],\
\
                    "time_slot_list": [\
\
                        {\
\
                            "date": 1639472400,\
\
                            "pickup_time_id": "1639472400"\
\
                        },\
\
                        {\
\
                            "date": 1639558800,\
\
                            "pickup_time_id": "1639558800"\
\
                        }\
\
                    ]\
\
                }\
\
            ]

        }

    },

    "request_id": "33d8460efcd7313ac5b8337b54ff4b07"

}
```

Note: The info\_needed field indicates the shipping method supported by the order and the parameters that need to be uploaded when you ship order. This example order supports dropoff or pickup method. If dropoff method is selected, there is no need to upload relevant parameters. If pickup is selected, you need to upload address\_id and pickup\_time\_id parameters. If info\_needed only returns dropoff, it means that the order only supports dropoff.

### 8.3.2. [v2.logistics.ship\_order](https://open.shopee.com/documents/v2/v2.logistics.ship_order?module=95&type=1)

1) Selecting the pickup method:

When the pickup parameter returned by info\_needed in v2.logistics.get\_shipping\_parameter contains address\_id and pickup\_time\_id.

Json

```
{

    "order_sn": "2112132KQ1MK9N",

    "pickup": {

        "address_id": 2826,

        "pickup_time_id": "1639472400"

    }

}
```

2) Selecting the dropoff method

When the dropoff parameter returned by info\_needed in v2.logistics.get\_shipping\_parameter is empty

Json

```
{

    "order_sn": "220301QQY0WASP",

    "dropoff": {}

}
```

Note: some channels for drop

off methods have a direct return of empty fields, you need to pass in the empty field, such as the example. If other parameters are returned, upload other parameters, for example:

Json

```
{
    "order_sn": "220301QQY0WASP",
    "dropoff": {
          "sender_real_name": "ABC"
  }
}
```

3) Selecting the non\_integrated method

When the non\_integrated parameter returned by info\_needed in v2.logistics.get\_shipping\_parameter is tracking\_number

Json

```
{
    "order_sn": "220301QQY0WASP",
    "non_integrated": {
        "tracking_number": "AK224200239740W"
    }
}
```

### 8.3.3 [v2.logistics.update\_shipping\_order](https://open.shopee.com/documents/v2/v2.logistics.update_shipping_order?module=95&type=1)

Json

```
{
    "order_sn": "2112132KQ1MK9N",
    "pickup": {
        "address_id": 11178,
        "pickup_time_id": "1658563200"
    }
}
```

Used for pickup order to update address\_id and pickup\_time\_id. Applicable to orders in RETRY\_SHIP status.

# 9\. FAQ

## Order related

Q: Call [v2.order.get\_order\_detail](https://open.shopee.com/documents/v2/v2.order.get_order_list?module=94&type=1) API and report error "Wrong parameters, detail: the order is not found.

A: Can check this [FAQ](https://open.shopee.com/faq/192).

Q:Call [v2.order.get\_order\_detail](https://open.shopee.com/documents/v2/v2.order.get_order_list?module=94&type=1) API, many response fields are missing, what should I do?

A Please check whether the response\_optional\_fields field is selected to upload the corresponding field, please refer to the [API documentatio](https://open.shopee.com/documents/v2/v2.order.get_order_detail?module=94&type=1) [n](https://open.shopee.com/documents/v2/v2.order.get_order_detail?module=94&type=1) for details.

## Shipping related

Q: Why I can't get the time slot?

A: If you can't get it, the order may have been shipped or ship\_by\_day has passed.

Q: I got the error "logistic status not ready to ship". How to check?

A:Please call [v2.order.get\_order\_detail](https://open.shopee.com/documents/v2/v2.order.get_order_detail?module=94&type=1) API to get the order status. Only orders with READY\_TO\_SHIP status can be shipped.

Q: Call [v2.logistics.get\_tracking\_number](https://open.shopee.com/documents/v2/v2.logistics.get_tracking_number?module=95&type=1) API but no first\_mile\_tracking\_number is returned, what do I need to do?

A: Please check whether the response\_optional\_fields field is selected to upload the corresponding field, please refer to the [API documentation](https://open.shopee.com/documents/v2/v2.logistics.get_tracking_number?module=95&type=1) for details.

## Airway Bill related

Q: Call [v2.logistics.create\_shipping\_document](https://open.shopee.com/documents/v2/v2.logistics.create_shipping_document?module=95&type=1) API, prompt error "Order status does not support awb printing".

A: Please call [v2.order.get\_order\_detail](https://open.shopee.com/documents/v2/v2.order.get_order_detail?module=94&type=1) API to get order\_status, only supports to get under order\_status is PROCESSED.

Q: Call [v2.logistics.get\_shipping\_document\_result](https://open.shopee.com/documents/v2/v2.logistics.get_shipping_document_result?module=95&type=1) API and get the status of "PROCESSING" how to deal with it?

A: It is recommended to call the API cyclically until you get to the "READY" status.

Q: How many types of Airway bill files are there?

A: There are three formats：

- Most orders' airway bill are PDF file.
- TW C2C channels all return airway bills is html format, B2C channels except 7-ELEVEN (channel\_id: 30005), Family Family (channel\_id: 30006), Lai Erfu (channel\_id: 30007), Family Family Frozen Super Pickup (not sent to outlying islands) ( channel\_id: 30011), OK Mart (channel\_id: 30014) are printed in pdf format, and others are returned html.
- If the printing method set in the seller center is thermal printing, the zip format folder is returned.

# 10\. Data Definition

## Order Status

- UNPAID:Order is created, buyer has not paid yet.
- READY\_TO\_SHIP:Seller can arrange shipment.
- PROCESSED:Seller has arranged shipment online and got tracking number from 3PL.
- SHIPPED:The parcel has been drop to 3PL or picked up by 3PL.
- TO\_CONFIRM\_RECEIVE:The order has been received by buyer.
- COMPLETED:The order has been completed.
- RETRY\_SHIP:3PL pickup parcel fail. Need to re arrange shipment.
- IN\_CANCEL:The order's cancelation is under processing.
- CANCELLED:The order has been canceled.
- TO\_RETURN:The buyer requested to return the order and order's return is processing.

## Package Status

- All: Fetch all packages that are Pending, ToProcess, or Processed, value 0.
- Pending: Fetch packages that are not ready for shipment, value 1.
- ToProcess: Fetch packages that need to arrange shipment, value 2.
- Processed: Fetch packages that have been arranged shipment, value 3.

Note:

Package Status takes the same effect as Order Status filter under To Ship tab in Seller Center, the mapping between Package Status, Package Fulfillment Status and Seller Center Order Status filter is as follows:

| Package Status | Package Fulfillment Status | Order Status filter under To Ship tab in Seller Center |
| --- | --- | --- |
| All (0) | LOGISTICS\_NOT\_START, LOGISTICS\_READY, LOGISTICS\_PICKUP\_RETRY, or LOGISTICS\_REQUEST\_CREATED | All |
| Pending (1) | LOGISTICS\_NOT\_START | Pending |
| ToProcess (2) | LOGISTICS\_READY or LOGISTICS\_PICKUP\_RETRY | To Process |
| Processed (3) | LOGISTICS\_REQUEST\_CREATED | Processed |

## Package Fulfillment Status / Logistics Status

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

Note: Due to legacy logic, the package logistics status in get\_order\_detail will return 2 additional values:

- LOGISTICS\_PENDING\_ARRANGE:order logistics pending arrangement
- LOGISTICS\_COD\_REJECTED:Integrated logistics COD: Order rejected for COD

## Order cancellation reason

- OUT\_OF\_STOCK
- UNDELIVERABLE\_AREA

## Cancel reason

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
- Seller did not Ship
- Auto Cancel
- Logistic Issue
- Your approver did not approve order on time.
- You are unable to place order at the moment.
- TBC

## Buyer cancel reason

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

## Shipping document type

- NORMAL\_AIR\_WAYBILL
- THERMAL\_AIR\_WAYBILL
- NORMAL\_JOB\_AIR\_WAYBILL
- THERMAL\_JOB\_AIR\_WAYBILL

## Package logistics track status

（for [get\_tracking\_info](https://open.shopee.com/documents/v2/v2.logistics.get_tracking_info?module=95&type=1) api）

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