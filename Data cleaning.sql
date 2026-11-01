---------------------------------------------------------Data Cleaning------------------------------------------------------------------

--========================--
--Geolocation Table

--Remove duplicates and group by geolocation_zip_code_prefix to select the spelling of city which appears the most.

select geolocation_zip_code_prefix,
geolocation_lat,geolocation_lng,
max(geolocation_city)as geolocation_city,
max(geolocation_state) as geolocation_state --into geolocation_temp
from (select distinct geolocation_zip_code_prefix,geolocation_lat,geolocation_lng,geolocation_city,geolocation_state
      from geolocation) as x
group by geolocation_zip_code_prefix,geolocation_lat,geolocation_lng
order by geolocation_zip_code_prefix

--Change the spellings to one consistent spelling across (English)

SELECT 
    geolocation_zip_code_prefix,geolocation_lat,geolocation_lng,
    TRANSLATE(
        geolocation_city, 
        '·‡‚„‰ÈËÍÎÌÏÓÔÛÚÙıˆ˙˘˚¸Á¡¿¬√ƒ…» ÀÕÃŒœ”“‘’÷⁄Ÿ€‹«', 
        'aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC'
    ) AS geolocation_city,
    geolocation_state 
FROM geolocation_temp;

--Check the cleaned geolocation table.

select *
from geolocation_clean

--Each geolocation_zip_code_prefix is displayed only once and different spellings have been converted to english.


--===========================--

--order_payments table

select *
from order_payments

--Convert the table to wide format by payment_type to remove duplicates.

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

--cleaned order_payments table

select *
from order_payments_clean

--===========================--

--order_items Table

select *
from order_items

--order_items table is clean

--===========================--

--Customer table

select *
from Customer

--Customer table is clean

--===========================--

--order_reviews table

select *
from order_reviews

--Select the latest review where multiple reviews have been provided for the same order

with rankreviews as 
(select order_id,review_id,review_score,
 review_creation_date,
 review_answer_timestamp,
 ROW_NUMBER() over (partition by order_id order by review_answer_timestamp desc) as row_numbers
 from order_reviews)
select order_id,review_id,review_score,
review_creation_date,
review_answer_timestamp into order_reviews_clean
from rankreviews 
where row_numbers = 1;

--check cleaned order_reviews table

select *
from order_reviews_clean

--===========================--

--product_category_name_translation table

select *
from product_category_name_translation

--product_category_name_translation is clean


--===========================--

--"products" table

select *
from products

--"product_name_length" & "product_description_length" do not offer any analysis so we will drop them.
--for null values in "product_photos_qty", replace them with 0.
--for products missing "product_category_name", impute them with the mode of category.

select product_id,
ISNULL(product_category_name, (select top 1 product_category_name
                               from products
                               where product_category_name is not null
                               group by product_category_name
                               order by count(product_id) desc)) as product_category_name,
ISNULL(product_photos_qty,0) as product_photos_qty,
product_weight_g,
product_length_cm,
product_height_cm,
product_width_cm into products_clean
from products

--Check clean products table

select *
from products_clean

--Products table is clean

--===========================--

--"sellers" Table

select distinct *
from sellers

--sellers table is clean


--===========================--

--orders table

--Flag inconsistent date rows

select order_id,customer_id,order_status,order_purchase_timestamp,order_approved_at,
order_delivered_carrier_date,order_delivered_customer_date,order_estimated_delivery_date,
case when
order_approved_at<order_purchase_timestamp then 1
when order_purchase_timestamp>order_delivered_carrier_date then 1
when order_purchase_timestamp>order_delivered_customer_date then 1
when order_approved_at>order_delivered_carrier_date then 1
when order_approved_at>order_delivered_customer_date then 1
when order_delivered_carrier_date>order_delivered_customer_date then 1
else 0
end as date_inconsistency_flag into orders_flagged
from orders_old


select *
from orders
where order_approved_at is null and 
order_status='delivered'


--For missing order approved at, replacing them with their date + Median time it takes for order to be approved.

SELECT DISTINCT 
PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CAST(DATEDIFF(minute, order_purchase_timestamp, order_approved_at) AS FLOAT))
OVER () AS median_approval_mins
FROM orders
WHERE order_approved_at > order_purchase_timestamp
AND order_approved_at IS NOT NULL

--Median order approved time is 21 minutes.

update orders
set order_approved_at=ISNULL(order_approved_at,DATEADD(minute,(SELECT DISTINCT 
                                         PERCENTILE_CONT(0.5) WITHIN GROUP
                                        (ORDER BY CAST(DATEDIFF(minute, order_purchase_timestamp, order_approved_at) AS FLOAT))
                                         OVER () AS median_approval_mins
                                         FROM orders
                                         WHERE order_approved_at > order_purchase_timestamp
                                         AND order_approved_at IS NOT NULL),order_purchase_timestamp))
from orders
where order_status='delivered'

--orders having "order_approved_date" ahead of "order_delivered_carrier_date"

select *
from orders
where order_approved_at>order_delivered_carrier_date

--Change inconsistent values to null and then replace those nulls with added median value

update orders
set order_delivered_carrier_date=null
where order_delivered_carrier_date<order_approved_at
and order_status in ('delivered','shipped')

update orders
set order_delivered_carrier_date=ISNULL(order_delivered_carrier_date,DATEADD(hour,(SELECT DISTINCT 
                                         PERCENTILE_CONT(0.5) WITHIN GROUP
                                        (ORDER BY CAST(DATEDIFF(hour, order_approved_at, order_delivered_carrier_date) AS FLOAT))
                                         OVER () AS median_carrier_delivery_mins
                                         FROM orders
                                         WHERE order_delivered_carrier_date > order_approved_at
                                         AND order_delivered_carrier_date IS NOT NULL),order_approved_at))
where order_status in ('delivered','shipped')

--orders having delivery date to customer before it got delivered to the carrier.

select *
from orders
where order_delivered_carrier_date>order_delivered_customer_date

--Replace inconsistent values with null then replace those null values by added median delivery time to customer.

update orders
set order_delivered_customer_date=null
where order_delivered_customer_date<order_delivered_carrier_date
and order_status = 'delivered'


update orders
set order_delivered_customer_date=ISNULL(order_delivered_customer_date,DATEADD(hour,(SELECT DISTINCT 
                                         PERCENTILE_CONT(0.5) WITHIN GROUP
                                        (ORDER BY CAST(DATEDIFF(hour, order_delivered_carrier_date, order_delivered_customer_date) AS FLOAT))
                                         OVER () AS median_customer_delivery_hours
                                         FROM orders
                                         WHERE order_delivered_customer_date > order_delivered_carrier_date
                                         AND order_delivered_customer_date IS NOT NULL),order_delivered_carrier_date))
where order_status = 'delivered'

--Check cleaned orders table

select *
from orders
where order_approved_at<order_purchase_timestamp
or
order_approved_at>order_delivered_carrier_date
or
order_delivered_carrier_date>order_delivered_customer_date
or 
order_approved_at>order_delivered_customer_date
or 
order_delivered_customer_date<order_approved_at

--"Orders" table is clean
