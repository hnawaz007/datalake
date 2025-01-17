with source as (

      select 
			productcategoryname, 
			productsubcategoryname, 
			productname, 
			salesterritorycountry, 
			salesamount, 
			cast(date_format(from_unixtime(cast(orderdate as bigint)/1000000), '%Y-%m-%d') as date) as date
	  from {{ ref('stg_sales') }}

),
renamed as (

    select 
        productcategoryname,
        productsubcategoryname,
        productname,
        salesterritorycountry,
		case 
			when salesterritorycountry in ('Canada', 'United States')
			then 'Americas'
			when salesterritorycountry in ('France', 'Germany', 'United Kingdom')
			then 'Europe'
			when salesterritorycountry in ('Australia')
			then 'Oceania'
			else salesterritorycountry
			end as region,
        salesamount,
        date as orderdate,
		date_trunc('year', date) as year,
		date_trunc('month', date) as month
    from source
)

select * from renamed