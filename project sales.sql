-- Retail sales Analysis.
use sql_project_p2;

drop table if exists retail_sales;


select * from retail_sales
;

Create table retail_sales (
transactions_id INT PRIMARY KEY,	
sale_date	DATE,
sale_time	TIME,
customer_id	INT,
gender	VARCHAR(25),
age	int,
category VARCHAR(25),	
quantiy	INT,
price_per_unit	Float,
cogs	float,
total_sale Float
);
-- Data cleaning
Delete from retail_sales
where 
transactions_id IS NULL
or
SALE_DATE IS NULL
OR 
sale_time is NULL
or
customer_id is null
or gender is null or age is null or category is null or quantiy is null or price_per_unit is null or cogs is null or total_sale is null;

select * from retail_sales
where 
transactions_id IS NULL
or
SALE_DATE IS NULL
OR 
sale_time is NULL
or
customer_id is null
or gender is null or age is null or category is null or quantiy is null or price_per_unit is null or cogs is null or total_sale is null;


-- data exploration
select count(distinct customer_id) from retail_sales;



