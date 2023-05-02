# Stock summary tool

## Features
* Import and export your portfolio data in CSV format.
* Add and remove transactions, including buying and selling stocks and receiving dividends.
* View and track the real-time market data of stocks and currencies.
* Generate an HTML report of your portfolio, including the current value of your portfolio, profit, and loss.
* Supports Azure cloud for keeping your portfolio data in sync between multiple devices.

## Prerequisites
* Python 3.8 or higher
* pip


## Create your environment

1. Create a virtual environment for the project and activate it (Python 3.8+ required):

    ```
    python3 -m venv my_venv/
    source my_venv/bin/activate
    ```

2. Install the package:

    ```
    pip3 install stock_summary_tool
    ```

3. Generate and save your API key:

   1. Register or log in to the [Yahoo Finance API page](https://rapidapi.com/sparior/api/yahoo-finance15).
   2. Register or log in to the [Exchange API page](https://rapidapi.com/principalapis/api/currency-conversion-and-exchange-rates).
   3. Subscribe to both APIs and obtain your API key.
   4. Save your key for the project:

    ```
    stock_summary_tool save-token <YOUR_TOKEN>
    ```

## Demo

1. Download the demo datasets and import them:

    ```
    stock_summary_tool import-data -y -e <PATH_TO_DEMO_ENTRIES> -p <PATH_TO_DEMO_PORTFOLIO)
    ```

2. Generate an HTML report (it should open automatically in your browser):

    ```
    stock_summary_tool generate-html
    ```

3. Update your portfolio with actual costs and generate the HTML report again:

    ```
    stock_summary_tool generate-portfolio
    stock_summary_tool generate-html
    ```

## Create your portfolio

1. Refresh the data in the empty files:

    ```
    stock_summary_tool import-data -y --rewrite
    ```

2. Add your entries (example) - stock symbol, date, count of stocks, price (sell entries are also supported, just add '-' sign before count):

    ```
    stock_summary_tool add-entry -s BOTZ.MI -d 12/01/2023 -c 20 -p 30
    ```

3. Enter your dividends (amount is in the original currency):

    ```
    stock_summary_tool add-dividend -s BOTZ.MI -d 12/01/2023 -a 10 
    ```

4. After you add your entries and dividends, generate the actual portfolio and HTML:

    ```
    stock_summary_tool generate-portfolio
    stock_summary_tool generate-html
    ```

5. Export your data and share it across multiple systems by importing it again:

    ```
    stock_summary_tool export-data -d <DIRECTORY_FOR_EXPORT>
    ```

## HTML tutorial

You can open the example summary `stock_summary/demo_datasets/index.html`. Currently, only the Czech language is supported, and the CZK currency is taken as the base.

You can see a plot with your actual investments in stocks, and also your profit (generated from the portfolio file). Below, you can see your actual holdings and statistics about them. Only actual holdings with >0 count are shown. The last table is for dividends.

## Use cloud (Azure)
1. Create an Azure account if you don't have it on: https://azure.microsoft.com/en-us/free

2. Create your Azure storage account as described in https://learn.microsoft.com/en-us/azure/storage/files/storage-how-to-use-files-portal?tabs=azure-portal (only part 'Create storage account').

3. In your storage account, click on 'Access tokens' and get your connection string.

4. Set up the cloud on your application:
```
stock_summary_tool set-cloud --cloud=azure --azure="{YOUR CONNECTION STRING}" --tactic=local
```
*Note: If you set up the cloud on your second device, use `--tactic=cloud`. It determines the init sync tactic [cloud files -> local files or local files -> cloud files].*


## Plans for the future
- Adding option for fees to the operations.
- Supporting more languages and base currencies.
- Adding backward possibility to generate portfolio and no need to generate it manually anymore (blocked by higher number of API calls and subscription)
- Adding option to track other investments except stocks/cryptocurrencies/dividends.

Feel free to open an issue or ask me if you want to know something or you want to help with the project.

