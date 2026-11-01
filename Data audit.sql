------------------------------------------------------------Data inconsistencies-----------------------------------------------------------
--=================--
--"Customer" table

select *
from Customer

--Total number of Customers.
select count(distinct customer_unique_id) as total_customers
from Customer

--Missing records per column
select
sum(case when customer_id is null then 1 else 0 end) as null_customer_id,
sum(case when customer_unique_id is null then 1 else 0 end) as null_customer_unique_id,
sum(case when customer_zip_code_prefix is null then 1 else 0 end) as null_customer_zipcode_prefix,
sum(case when customer_city is null then 1 else 0 end) as null_customer_city,
sum(case when customer_state is null then 1 else 0 end) as null_customer_state
from customer

--Customer Table has no data inconsistencies.

--=======================--
--"order_payments" table

select *
from order_payments

--Missing value per columns

select
sum(case when order_id is null then 1 else 0 end) as null_order_id,
sum(case when payment_sequential is null then 1 else 0 end) as null_payment_sequential,
sum(case when payment_type is null then 1 else 0 end) as null_payment_type,
sum(case when payment_installments is null then 1 else 0 end) as null_payment_installments,
sum(case when payment_value is null then 1 else 0 end) as null_payment_value
from order_payments

--Find duplicate "order_id" to check for inconsistencies/

SELECT *
FROM order_payments
WHERE order_id IN (SELECT order_id
                   FROM order_payments
                   GROUP BY order_id
                   HAVING COUNT(order_id)>1)
ORDER BY order_id,payment_sequential

--There are order_id that are having payment in parts via different payment types.

/*Cleaning strategy -> Group by order_id and summing for the payment value while converting "payment_type"
to wide format to remove duplicate "order_id" without losing any information.*/

SELECT order_id,count(payment_sequential) as tot_orders,
sum(payment_installments) as Total_installments,
         round(sum(case when payment_type='credit_card'
             then payment_value else 0 end),2) as credit_card,
         round(sum(case when payment_type='boleto'
             then payment_value else 0 end),2) as boleto,
         round(sum(case when payment_type='voucher'
             then payment_value else 0 end),2) as voucher,
         round(sum(case when payment_type='debit_card'
             then payment_value else 0 end),2) as debit_card,
         round(sum(case when payment_type='others'
             then payment_value else 0 end),2) as others,
round(sum(payment_value),2) as total_amount --into order_payments_clean
FROM order_payments
group by order_id


--"order_payments" is clean

--=======================--
--"orders table"

select *
from orders

--Missing values per column

select
sum(case when order_id is null then 1 else 0 end) as null_order_id,
sum(case when customer_id is null then 1 else 0 end) as null_customer_id,
sum(case when order_status is null then 1 else 0 end) as null_order_status,
sum(case when order_purchase_timestamp is null then 1 else 0 end) as null_order_purchase_timestamp,
sum(case when order_approved_at is null then 1 else 0 end) as null_order_approved_at,
sum(case when order_delivered_carrier_date is null then 1 else 0 end) as null_order_delivered_carrier_date,
sum(case when order_delivered_customer_date is null then 1 else 0 end) as null_order_delivered_customer_date,
sum(case when order_estimated_delivery_date is null then 1 else 0 end) as null_order_estimated_delivery_date
from orders

--Missing date time values

select *
from orders
where order_approved_at is null or order_delivered_carrier_date is null
or order_delivered_customer_date is null

/*
1. It is normal to have null values for "order_delivered_carrier_date","order_delivered_customer_date"
and "order_approved_at" for cancelled orders and no imputation is needed.

2. For "shipped" order_status, it is expected to have null "order_delivered_customer_date".
We can segregate them into a different table for analysis purpose. It is advised to keep the null values 
as it shows valuable insights.

3. Orders that are "unavailable","processing" and "invoiced" will have null value for "order_delivered_carrier_date"
and "order_delivered_customer_date". We should keep them as null for analysis of KPIs and trends related to 
incomplete or cancelled orders.
*/

--Orders having delivered date before approved date.

select order_id,customer_id,order_purchase_timestamp,order_delivered_carrier_date,order_delivered_customer_date
from orders
where order_delivered_carrier_date>order_delivered_customer_date

--Missing "order_approved_at" values for orders that are delivered.

select *
from orders
where order_status = 'delivered' and
order_approved_at is null

--14 records have missing "order_approved_at" values despite being delivered.

--Records in total having date time inconsistency.

select *
from orders
where order_purchase_timestamp>order_delivered_carrier_date
or order_purchase_timestamp>order_delivered_customer_date
or order_approved_at>order_delivered_carrier_date
or order_approved_at>order_delivered_customer_date
or order_delivered_carrier_date>order_delivered_customer_date

--There are total 1,381 records which have date time inconsistency ( roughly 1.38% of the total records )

/* Cleaning strategy for orders table -> 
1. Calculate average time in hours it takes for an order to get 
approved, then add that to the "order_purchase_timestamp" to impute missing values.

2. for orders which have delivery date before approved date, we need to confirm with the client for correct
data or assuming these values got exchanged, we can interchange these values to get them in the correct order.

3. For 1,381 records which have a date time inconsistency should be confirmed with the client if they can provide
a clear solution or we can delete them since they will reduce the accuracy of our analysis.
*/

--Find average order_approved time

select avg(DATEDIFF(hour,order_purchase_timestamp,order_approved_at)) as avg_approval_time
from orders

--update order approved at by adding the avg time to order_timestamp

select order_id,
customer_id,order_status,order_purchase_timestamp,
ISNULL(order_approved_at,DATEADD(hour,(select avg(DATEDIFF(hour,order_purchase_timestamp,order_approved_at))
from orders),order_purchase_timestamp))
as filled_approved_at,
order_delivered_carrier_date,order_delivered_customer_date,order_estimated_delivery_date
from orders
where order_approved_at is null and
order_status = 'delivered'

--"orders" table is clean

--=======================--
--"geolocation" table

SELECT *
FROM geolocation

--Missing values per column

select
sum(case when geolocation_zip_code_prefix is null then 1 else 0 end) as null_geolocation_zip_code,
sum(case when geolocation_lat is null then 1 else 0 end) as null_geolocation_lat,
sum(case when geolocation_lng is null then 1 else 0 end) as null_geolocation_lng,
sum(case when geolocation_city is null then 1 else 0 end) as null_geolocation_city,
sum(case when geolocation_state is null then 1 else 0 end) as null_geolocation_state
from geolocation

--Duplicate values

select geolocation_zip_code_prefix, geolocation_lat,geolocation_lng,geolocation_city,geolocation_state,
count(*) as duplicate_count
from geolocation
group by geolocation_zip_code_prefix, geolocation_lat,geolocation_lng,geolocation_city,geolocation_state
having count(*) > 1

--128270 exact duplicates exist in geolocation table

--Remove exact duplicates

select distinct *  --into geolocation_d
from geolocation

--Data inconsistency in geolocation

select *
from geolocation
where geolocation_zip_code_prefix in (select geolocation_zip_code_prefix
                                      from geolocation
                                      group by geolocation_zip_code_prefix
                                      having count(geolocation_zip_code_prefix) > 1)
order by geolocation_zip_code_prefix

/* 
1. Every "geolocation_zip_code_prefix" is repeated multiple times with minor changes in latitudes and
longitudes which is unnecessary for our analysis.

2. There are spelling variations in "geolocation_city" which is also multiplying the rows.

Cleaning stratergy ->  Group all the "geolocation_zip_code_prefix" through average of latitudes and
longitudes and for "geological_city" cleaning, use max to group so as to keep one consistent spelling.
It is better that we can remove latitudes and longitudes just for analysis purposes as cities and states are enough.
*/

select geolocation_zip_code_prefix,
avg(geolocation_lat) as geolocation_lat,
avg(geolocation_lng) as geolocation_lng,
max(geolocation_city) as geolocation_city,
max(geolocation_state) as geolocation_state
from GEOLOCATION
group by geolocation_zip_code_prefix
order by geolocation_zip_code_prefix

--Duplicates are removed and all 19,015 locations are cleanly mentioned with uniform spelling of cities.

--Clean "geolocation" table

--=======================--
--"order_items" table

SELECT *
FROM order_items

--Missing values

select
sum(case when order_id is null then 1 else 0 end) as null_order_id,
sum(case when order_item_id is null then 1 else 0 end) as null_order_item_id,
sum(case when product_id is null then 1 else 0 end) as null_product_id,
sum(case when seller_id is null then 1 else 0 end) as null_seller_id,
sum(case when shipping_limit_date is null then 1 else 0 end) as null_shipping_limit_date,
sum(case when price is null then 1 else 0 end) as null_price,
sum(case when freight_value is null then 1 else 0 end) as null_freight_value
from order_items

--No missing values

--Check if "price" & "freight_value" has negative values

select * 
from order_items
where price < 0 or
freight_value < 0

--No such values

--"order_items" table is clean and is expected to have duplicate "order_ids"


--=======================--
--"order_reviews" table

select *
from order_reviews

--Missing values

select
sum(case when review_id is null then 1 else 0 end) as null_review_id,
sum(case when order_id is null then 1 else 0 end) as null_order_id,
sum(case when review_score is null then 1 else 0 end) as null_review_score,
sum(case when review_comment_title is null then 1 else 0 end) as null_review_comment_title,
sum(case when review_comment_message is null then 1 else 0 end) as null_review_comment_message,
sum(case when review_creation_date is null then 1 else 0 end) as null_creation_date,
sum(case when review_answer_timestamp is null then 1 else 0 end) as null_review_answer_timestamp
from order_reviews

--Check for inconsistent review_score

select *
from order_reviews
where review_score < 1 or
review_score >5

--No such records are there.

--Check if there are multiple reviews for 1 order.

select *
from order_reviews
where review_id in (select review_id
                    from order_reviews
                    group by review_id
                    having count(distinct order_id)>1)
order by review_id

/* It is observed that there are 1603 records where "review_id" is different for same "order_id".
It is clear through inspection that majority of them are simply having the same title and comment_message.
*/

/*Cleaning strategy -> 
1. It is better to consider the latest review since it offers better understanding of customer
review.
2. For null values in "review_comment_title" & "review_comment_message" we can simply replace them with 
"not_mentioned" or "N/A" since it is common for customers to simply rate and not provide any comment.
For our current analysis we can even remove these two columns as they do not provide any insight apart from 
sentiment analysis.*/

with rankreviews as 
(select order_id,review_id,review_score,
 review_creation_date,
 review_answer_timestamp,
 ROW_NUMBER() over (partition by order_id order by review_answer_timestamp desc) as row_number
 from order_reviews)
 
select order_id,review_id,review_score,
review_creation_date,
review_answer_timestamp
from rankreviews
where row_number = 1;

--Clean "order_reviews" table


--=======================--
--"products table"

select *
from products

--Missing values

select
sum(case when product_id is null then 1 else 0 end) as null_product_id,
sum(case when product_category_name is null then 1 else 0 end) as null_product_category_name,
sum(case when product_name_lenght is null then 1 else 0 end) as null_product_name_length,
sum(case when product_description_lenght is null then 1 else 0 end) as null_product_description_length,
sum(case when product_photos_qty is null then 1 else 0 end) as null_products_photos_qty,
sum(case when product_weight_g is null then 1 else 0 end) as null_product_weight_g,
sum(case when product_length_cm is null then 1 else 0 end) as null_product_length_cm,
sum(case when product_height_cm is null then 1 else 0 end) as null_product_height_cm,
sum(case when product_width_cm is null then 1 else 0 end) as null_product_width_cm
from products

--Show null values

select *
from products
where product_category_name is null

select product_id,
ISNULL(product_category_name,'unknown') as product_category_name,
ISNULL(product_photos_qty, 0) as product_photos_qty,
product_weight_g,product_length_cm,product_height_cm,product_width_cm
from products
where product_category_name is null

--There are 610 "product_ids" which do not have "product_category_name" & three other product descriptions.

/*Cleaning strategy -> 
1. Removing these products would affect "orders" table and other connected tables, generating more null values when
joins are made for our analysis.

2. For the purpose of analysis and business insights, product descriptions do not serve much purpose,
hence we can take them out and just keep "product_id","product_category_name" & "product_photos_qty"

3. If we want to still keep them then it is better to change the null values to "unknown".

4. For imputing "product_photos_qty", replace null values with 0.
*/

--=======================--
--"sellers table"

select *
from sellers

--Missing values

select
sum(case when seller_id is null then 1 else 0 end) as null_seller_id,
sum(case when seller_zip_code_prefix is null then 1 else 0 end) as null_seller_zip_code_prefix,
sum(case when seller_city is null then 1 else 0 end) as null_seller_city,
sum(case when seller_state is null then 1 else 0 end) as null_seller_state
from sellers

--No missing values

--sellers data is clean


--=======================--
--"product_category_name_translation"

select *
from product_category_name_translation

--Missing values

select
sum(case when product_category_name is null then 1 else 0 end) as null_product_category_name,
sum(case when product_category_name_english is null then 1 else 0 end) as null_product_category_name_english
from product_category_name_translation


--On inspection, "product_category_name_translation" is clean


----------------------------------------------------------End-------------------------------------------------------------------