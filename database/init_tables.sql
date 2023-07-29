create table users(
  user_uuid                  uuid        primary key    not null
  , username                 varchar(50)
  , telegram_account         varchar(50)
  , email                    varchar(50)
  , default_currency_code    varchar(10)
);

create table transactions(
  transaction_id               uuid                  primary key                           not null
  , lcl_dttm                   timestamp             default (now() at time zone 'utc')
  , entity_type                varchar(50)
  , category                   varchar(50)
  , user_uuid                  varchar(50)
  , amount_lcy                 numeric
  , currency_code              varchar(10)
  , place                      varchar(100)
  , description                varchar(100)
  , expected_transaction_id    uuid
);

create table expected_transactions(
  expected_transaction_uuid    uuid          primary key
  , lcl_dttm                   timestamp       default (now() at time zone 'utc')
  , entity_type                varchar(50)
  , category                   varchar(50)
  , place                      varchar(100)
  , description                varchar(100)
  , user_uuid                  varchar(50)
  , amount_lcy                 numeric
  , currency_code              varchar(10)
);

create table currencies(
  currency_num_code    int            primary key
  , currency_code      varchar(10)
  , currency_name      varchar(50)
  , prec               int            default 0
  , aliases            varchar ARRAY
);

create table exchange_rates(
  from_currency_code       int
  , to_currency_code       int
  , buyrate                decimal
  , sellrate               decimal
  , utc_valid_from_dttm    timestamp
  , utc_valid_to_dttm      timestamp
);

select
  *
from pg_catalog.pg_tables 
where schemaname = 'public'


