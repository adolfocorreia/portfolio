#!/usr/bin/env Rscript

shhh <- suppressPackageStartupMessages
shhh(library(argparser))
shhh(library(lubridate))

NOW <- Sys.Date()

parser <- arg_parser('Download B3 curves')
parser <- add_argument(
  parser,
  'year',
  help = 'year to download',
  type = 'numeric',
  default = year(NOW)
)

argv <- commandArgs(trailingOnly = TRUE)
if (length(argv) > 0) {
  YEAR <- parse_args(parser, argv = argv)$year
} else {
  YEAR <- year(NOW)
}


library(rb3)
# options(rb3.cachedir = file.path(here::here(), 'rb3-cache'))
options(rb3.clear.cache = TRUE)
options(rb3.silent = TRUE)

first_date <- make_date(YEAR, 1, 1)
last_date <- min(make_date(YEAR, 12, 31), NOW)

print('Downloading DI x Pre and DI x IPCA curves...')
df_pre <- yc_mget(first_date = first_date, last_date = last_date)
df_ipca <- yc_ipca_mget(first_date = first_date, last_date = last_date)

readr::write_csv(df_pre,  file.path(here::here(), paste0('yc_di_pre_', YEAR, '.csv')))
readr::write_csv(df_ipca, file.path(here::here(), paste0('yc_di_ipca_', YEAR, '.csv')))
