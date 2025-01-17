
with source as (

      select * from {{ source('src_trino', 'sales') }}

),
renamed as (

    select 
        productcategoryname,
        productsubcategoryname,
        productname,
        salesterritorycountry,
        salesamount,
        orderdate
    from source
)

select * from renamed