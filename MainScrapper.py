from Classes import TopMarketScrapper, StockScrapper, IndustryScrapper, SectorScrapper, API_Scrapper
from Database.Database import Database
from config import *
from selenium import webdriver
import pandas as pd
import argparse
import sys


def stock_parser():
    """
    The program receives user arguments and prints the info under query.
    """
    parser = argparse.ArgumentParser(
        description="usage: MainScrapper.py [-h] [-ticker_to_scrap] [concise|expanded] ")
    parser.add_argument('scrapper', choices=['concise', 'expanded'], help='select the query to perform')
    parser.add_argument('-ticker_to_scrap', '--ticker', type=str, nargs='?', default='all_stocks',
                        help='choose stock to scrap')
    args = parser.parse_args()
    return args.scrapper, args.ticker


def main():
    """
    Given a URL of the stock market and the url's for each stock imported from TopMarketScrapper.py,
    creates a printable DataFrame and financial table for all the stocks.
    :return: DF and dict
    """
    db = Database()
    user_options = stock_parser()
    print(f'{user_options[ARG_SCRAP].title()} Scrapping On {user_options[ARG_TICKER]}...')
    if user_options[ARG_SCRAP] == 'concise':
        scrap_sectors = SectorScrapper.SectorScrapper(URL_SECTOR)
        top_sectors = scrap_sectors.summarizer()
        dict_sectors = db.dict_sectors(top_sectors)
        print('Sectors Summary', top_sectors, sep='\n')
        db.insert_sectors_table(top_sectors)

        scrap_industries = IndustryScrapper.IndustryScrapper(URL_INDUSTRY)
        top_industries = scrap_industries.summarizer()
        print('Industry Summary', top_industries, sep='\n')
        db.insert_industry_table(top_industries, dict_sectors)

        scrap_top = TopMarketScrapper.TopMarketScrapper(URL)
        top_stocks = scrap_top.summarizer()
        db.insert_main_table(top_stocks, dict_sectors)
        print('', 'Stock Summary', top_stocks, sep='\n')

    elif user_options[0] == 'expanded':
        scrap_sectors = SectorScrapper.SectorScrapper(URL_SECTOR)
        top_sectors = scrap_sectors.summarizer()
        dict_sectors = db.dict_sectors(top_sectors)
        db.insert_sectors_table(top_sectors)

        scrap_industries = IndustryScrapper.IndustryScrapper(URL_INDUSTRY)
        top_industries = scrap_industries.summarizer()
        db.insert_industry_table(top_industries, dict_sectors)

        scrap_top = TopMarketScrapper.TopMarketScrapper(URL)
        top_stocks = scrap_top.summarizer()
        db.insert_main_table(top_stocks, dict_sectors)
        ids_list = db.read_from_db('Main')

        top_stocks = StockScrapper.main(user_options[ARG_TICKER])
        print('Stock Summary', top_stocks, sep='\n')
        db.insert_valuation_table(top_stocks, ids_list)
        db.insert_metrics_table(top_stocks, ids_list)
        db.insert_balance_sheet_table(top_stocks, ids_list)
        db.insert_price_history_table(top_stocks, ids_list)
        db.insert_dividends_table(top_stocks, ids_list)
        db.insert_margins_table(top_stocks, ids_list)
        db.insert_income_table(top_stocks, ids_list)
        api_overview = API_Scrapper.api_overview(user_options[ARG_TICKER])
        db.insert_api_table(api_overview, ids_list)

    db.close_connect_db()


if __name__ == '__main__':
    main()
