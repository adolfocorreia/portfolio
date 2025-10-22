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


update_curve_data <- function(file_name, yc_get_function) {
  if (file.exists(file_name)) {
    previous_df <- readr::read_csv(file_name, show_col_types = FALSE)
    first_date <- as.Date(max(previous_df$refdate)) + 1
  } else {
    previous_df <- NULL
    first_date <- make_date(YEAR, 1, 1)
  }
  last_date <- min(make_date(YEAR, 12, 31), NOW)

  new_df <- yc_get_function(first_date = first_date, last_date = last_date)

  df <- rbind(previous_df, new_df)
  df <- dplyr::distinct(df)

  readr::write_csv(df, file_name)
}


library(rb3)
# options(rb3.cachedir = file.path(here::here(), 'rb3-cache'))
options(rb3.clear.cache = TRUE)
options(rb3.silent = TRUE)

print('Downloading DI x Pre curves...')
pre_file_name <- file.path(here::here(), paste0('yc_di_pre_', YEAR, '.csv'))
update_curve_data(pre_file_name, yc_mget)

print('Downloading DI x IPCA curves...')
ipca_file_name <- file.path(here::here(), paste0('yc_di_ipca_', YEAR, '.csv'))
update_curve_data(ipca_file_name, yc_ipca_mget)
