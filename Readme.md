# Brazilian E-Commerce Analytics: A Comprehensive Study of Sales Performance, Customer Behavior, Seller Insights \& Customer Satisfaction





## Objective



The primary objective of this project is to analyze sales performance, customer behavior, seller performance, delivery operations, and customer satisfaction for Olist, a Brazilian e-commerce marketplace that connects customers with sellers across Brazil. The project aims to identify key trends and patterns in sales and revenue, customer acquisition, product performance, seller contributions, delivery efficiency, and customer review scores across different geographical and demographic segments. By examining these factors collectively, the analysis seeks to understand their impact on the overall business performance and identify areas of improvement as well as opportunities for growth. Ultimately, the project aims to provide actionable, data-driven insights that enable business and operations leaders to optimize resource allocation, address underperforming areas, recognize high-performing segments, and make informed strategic decisions.



## Business Context



Olist is one of Brazil's largest e-commerce marketplaces, connecting thousands of independent sellers with customers nationwide. As the business scales, managing performance across sales, customers, sellers, and delivery becomes increasingly critical. The client has provided us with sales data from 2016 to 2018, spanning across 9 tables providing data of  99,441 customers, 3095 sellers \& 32,951 products. We are expected to provide data driven analysis of key metrics at product level, customer level, sales level, supplier level, etc.



#### Key goals



* Analyze sales, customer behavior, seller performance, and delivery operations
* Identify trends in orders, revenue, and product categories.
* Evaluate customer satisfaction using reviews, delivery time, and payment methods.
* Measure financial impact on revenue due to cancellations and late deliveries.
* Develop a predictive model to forecast customer review scores.
* Provide actionable recommendations to improve business performance.



#### Key areas of analysis



* Customer behavior and revenue analysis.
* Orders, revenue generated and trends analysis.
* Products, Category penetration and demographics analysis.
* Sellers diversity and delivery delays analysis.
* Root cause for low ratings by customers and it's relationship with the sellers.



#### Tools and technologies used



* Microsoft SQL Server: Data Importing, Data Audit, Data Consistency Checks \& Analysis.
* Python: Descriptive, Diagnostic \& Predictive Analytics, Streamlit applications.
* Power BI Desktop: Visualization and Interactive Dashboard Development.
* Power BI Service: Publishing Dashboards for stakeholder access.
* PowerPoint: Presentation of findings, insights, and recommendations.



#### Key Insights \& Recommendations:

##### 

##### Customer level



###### Insights:



* New customers acquisition showed a positive trend for the majority of analysis but slowed down around August 2018.
* One time buyers were responsible for most of the orders and maximum revenue generated.
* Certain states had more customers who ordered and majority of states had very less number of customers. Same with the cities.
* RFM segmentation showed that majority of customers belong to the silver category and there were far less customers in gold and platinum.
* Most of the customers belong to the low revenue generating segment.
* Customers prefer to pay using credit cards and majority pay with only one method while few paid with vouchers and other payment methods.



###### Recommendations:



* Retail chain can try personalized marketing strategies to retain customers. They could collect Email address of the customer if they are willing to provide. Thus, retail chain can remind them of any new products or upcoming offers.
* Loyalty rewards can be given for retained customers like coupons, discounts etc.
* Credit points can be given for each purchase and when customer reaches a certain threshold, they can get selected products for free. These can be the products which are performing worst in terms of sales.



##### Orders level



###### Insights:



* Over 73% of orders were paid through credit card and least by debit card.
* Weekday sales contribute to majority of the sales and revenue whereas weekend sales has very less contribution.
* Over 89% orders were timely approved, processed and delivered. Certain states are performing bad in terms of order volume and delivery times. Certain orders in cities have average delivery time above 3 months.
* High volume of orders are received during 10AM and 11PM which marks this time as high productive time for increased revenue.
* Average order delivery time increased substantially in Q4. Christmas, Halloween and New year time shows increased order volume which is likely the reason for extended delivery days.
* Certain cities and states are performing worst while handling order volume and the lowest revenue generators.



###### Recommendations:



* Logistics \& Regional Delivery: Proactively monitor fulfilment bottlenecks for remote states experiencing extended delivery windows (up to 2 months). Prioritize carrier contract renegotiations in high-delay regions to protect customer satisfaction.
* Holiday Seasonality: Average delivery times spike during the Q4 peak holiday season (Black Friday, Christmas and New Year). Mitigate carrier strain by onboarding temporary logistics staff and introducing performance incentives ahead of Q4.
* Targeted Marketing \& Acquisition: Deploy targeted digital acquisition and competitive first-order incentives in underperforming regions to stimulate localized demand.
* Demand \& Inventory Planning: Capitalize on early-week shopping momentum by ensuring high-demand inventory is fully restocked by Monday morning, supported by weekend promotional push notifications.



##### Products level



###### Insights:



* Health beauty category is the highest revenue generating category followed by bed\_bath\_table and watches\_gift. Health beauty generates 1.22M in revenue.
* Bed bath table category dominates in number of orders and is also the category with most number of products (over 12000) across all states.
* Watches gift category has the most expensive products with an average price of BRL 200.
* Office and household furniture constitute the largest orders in terms of average dimensions and weight, whereas garden supplies have the highest average freight value.
* Bed bath table have the highest category penetration with roughly 11% products per orders belonging to bed bath table.
* Pareto analysis showed that roughly 20% of categories contribute to nearly 78% of all orders.
* Considering the highest selling category (bed\_bath\_table), the highest cross selling products are furniture\_decor, home\_comfort,homewares, baby \& health\_beauty.



###### Recommendations:



* Concentrate on Class A Categories: Focus promotional spend and seller acquisition programs on the top Pareto categories that drive the majority of platform revenue, ensuring high stock availability for high-demand items.
* Leverage High-Penetration Anchors: Use high-penetration categories (such as Bed, Bath \& Table and Health \& Beauty) as traffic drivers on landing pages, cross-promoting complementary lower-penetration items to lift overall catalogue visibility.
* Mitigate Regional Shipping Drag: Address disproportionately high freight-to-price ratios in remote states by partnering with regional carriers or offering localized warehousing options for bulky inventory to protect conversion rates.
* Proactive Q4 Capacity Planning: Average delivery times spike during peak holiday windows due to high order volume. Combat seasonal fulfilment delays by securing advance carrier agreements and onboarding temporary logistics personnel ahead of Q4.
* Automated "Frequently Bought Together" Bundles: Implement data-driven cross-selling modules at checkout based on co-occurrence and association rules (e.g. pairing home decor with furnishing items) to increase Average Order Value (AOV).
* Strategic Product Bundling: Create bundled pricing packages for low-cost, high-freight items where shipping costs otherwise deter single-unit purchases.



##### Sellers level



###### Insights:



* Out of 3095 sellers, a few of them were performing really bad in terms of order volume and average delivery days with few of them having average delivery days in months.
* Seller diversity in terms of product categories is low for majority of sellers with only a few of them selling more than 5 unique products/product categories.
* Certain states have low number of sellers despite handling high order value meanwhile few states have less number of sellers altogether.
* Few sellers performed worst in terms of order delivery times and revenue generated with sellers from SP outperforming the rest.
* State SP has the most number of sellers and also have the highest orders fulfilled by these sellers. On the same scale states like AM, MA, PA and PI have less number of sellers despite fulfilling more orders than some other states.
* State SP also have the highest revenue generated by sellers followed by MG, PR \& RJ.
* Few sellers have order fulfilment and delivery days more than 20 days with maximum being above 6 months. The constitute the worst performing sellers.
* There are certain sellers which have high volume of orders and still manage to keep their median delivery time under 8 days.
* There is only one order from state AC in 2 years.



###### Recommendations:



* Geographic Expansion \& Regional Hub Optimization: Decentralize fulfilment from State SP: Given that State SP concentrates the highest density of sellers and order volume, establish localized regional fulfilment hubs or warehouses in underrepresented states (such as AM, MA, PA, and PI) where demand outpaces local seller representation. This will reduce shipping distances and transit bottlenecks.
* Sellers SLA Enforcement \& Performance Governance: Implement Strict Delivery Thresholds: Identify and penalize the underperforming tail of sellers whose fulfillment and delivery cycles stretch beyond 20 days (and up to 6 months). Establish automated warning flags, penalize low SLA compliance with lower search visibility on the marketplace, or suspend chronically delayed vendors to protect customer satisfaction.
* Benchmark \& Scale High-Performing Vendor Practices: Study \& Replicate Efficiency: Conduct a best-practice audit on high-volume sellers who successfully maintain a median delivery time under 8 days despite heavy order loads. Create incentive structures or priority placement programs for these high-efficiency vendors and share their operational playbooks across the platform.
* Establish localized regional fulfilment hubs per state where demand is more than what the sellers can handle. It will reduce the distance between customers and sellers and ensure higher delivery speed.
* Create an audit report for such underperforming sellers and offer them implementation practices from high performing sellers.



##### Customer Satisfaction level



###### Insights:



* Majority of states performed well in terms of review rating while a small fraction  performed worst in terms of average rating.
* Majority of orders were rated 5, followed by rating 4 and a few intermediatory  2 and 3 rating. Review score 1 has substantial number.
* Certain sellers performed better than others and received higher rating than those sellers.
* Certain product categories receive consistent poor reviews and others receive consistent higher review scores.
* State AC and AM have the least average rating, whereas states MS and PA have the highest rating of 4.5 indicating high customer satisfaction.
* States like SP, SC \& RS also show good review score of around 4. showing consistent good score.
* “Cds\_dvds\_musicals” is the highest rated category with an average rating  of about 4.5 meanwhile “security\_and\_services” is the least rated category with average rating of 2.5.
* December 2016 had the highest rating of 5 across all orders while October and November 2016 received the lowest  average rating of 1 across all orders. All other months in both years have had an average rating of 4 showing majority of orders across months have a consistent high rating.



##### Recommendations:



* Analyze review score and comments in comparison to customer 360 and understand if reviews are from genuine customers or bots.
* Understand competitions and implement their strategy for better customer satisfaction.
* Send a follow up survey on email or phone number of low rating customers and understand the reason in depth. Reward them for taking this survey by offers for next orders.
* States having consistent lower rating should be audited and the sellers and logistics hub there should be kept in check.
* Consider improving product quality, delivery times, or customer service in the  to boost satisfaction.
* Sustain high performance in musicals, fashion and books by rewarding loyal customers with promotions or discounts to strengthen loyalty.
* Launch customer satisfaction improvement programs across all categories with a focus on personalization, better customer service, and optimized shopping experiences.
* For sellers having a low rating, stricter checks should be done on them and they should be provided with measures to improve.



## 

## Analytics \& Machine Learning Dashboard



An interactive, multi-tab Business Intelligence web application built to analyze customer behavior, sales trends, product categories, seller performance, and customer satisfaction for Olist Brazilian E-Commerce data. It also features a machine learning **Review Score Prediction Model** powered by Logistic Regression.

## 

#### Live App (Requires Login Credentials) 



Explore the live application here: [View Streamlit App](https://brazilian-e-commerce-analytics-divyamraj-e4jrruzemd6fdn7gphsxe7.streamlit.app/)



##### Login Credentials:



**username: admin**

**password: olist2026**





#### Key Dashboards \& Features



* **Customer Dashboard:** Geographic distribution, RFM segmentation, payment preferences, and active filtering by city and month.
* **Orders \& Sales Trends:** Revenue metrics, delivery efficiency, top cities analysis, and hourly/weekly ordering patterns.
* **Products Dashboard:** Category penetration metrics, price-freight correlations, and top-performing product categories.
* **Sellers Dashboard:** Seller diversity metrics, delivery delays identification, and regional performance.
* **Customer Satisfaction (CSAT):** Review score distributions, response turnaround times, and sentiment tracking.
* **⭐ Review Prediction Model:** An interactive ML portal where users can input order characteristics to predict customer review scores in real-time.



#### Tech Stack



* **Language:** Python
* **Data Processing \& Analysis:** Pandas, NumPy, Parquet
* **Machine Learning:** Scikit-learn, Logistic Regression, Joblib
* **Data Visualization:** Plotly (Express \& Graph Objects)
* **Web Framework:** Streamlit (Deployed on Streamlit Community Cloud)

