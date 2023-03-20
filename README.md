# Stock summary tool

### CREATE YOUR ENVIRONMENT
1. Create virtual environment that you will use for the project and activate it (python3.8+ required):
```
python3 -m venv my_venv/
source my_venv/bin/activate
```
2. Install the package: 
```
pip3 install stock_summary_tool
```
3. Generate and save your token:
   1. Register or log in to the page.
   2. Go to https://rapidapi.com/ and register.
   3. Subscribe to these APIs and obtain your API key:
      1. https://rapidapi.com/sparior/api/yahoo-finance15
      2. https://rapidapi.com/fixer/api/fixer-currency
   4. Save your key for the project:
   ```
   stock_summary_tool save-token <YOUR_TOKEN>
   ```
### DEMO

1. You can download demo datasets and import them:
   ```
   stock_summary_tool import-data -y -e <PATH_TO_DEMO_ENTRIES> -p <PATH_TO_DEMO_PORTFOLIO)
   ```
2. You can generate-html (it should open automatically in your browser):
   ```
   stock_summary_tool generate-html
   ```
3. You can update your portoflio by actual cost and generate again HTML page:
   ```
   stock_summary_tool generate-portfolio
   stock_summary_tool generate-html
   ```

### CREATE YOUR PORTFOLIO

1. Refresh data to empty files:
   ```
   stock_summary_tool import-data -y --rewrite
   ```
2. Add your entries (example) - stock symbol, date, count of stocks, price (sell entries are also supported, just add '-' sign before count):
   ```
   stock_summary_tool add-entry -s BOTZ.MI -d 12/01/2023 -c 20 -p 30
   ```
3. You can enter also your dividends (amount is in original currency):
   ```
   stock_summary_tool add-dividend -s BOTZ.MI -d 12/01/2023 -a 10 
   ```
4. After you add your entries and dividends, generate actual portfolio and HTML:
   ```
   stock_summary_tool generate-portfolio
   stock_summary_tool generate-html
   ```
5. You can also export your data and share them across multiple systems (by importing them again):
   ```
   stock_summary_tool export-data -d <DIRECTORY_FOR_EXPORT>
   ```

### HTML tutorial

*You can open example summary stock_summary/demo_datasets/index.html Right now, there is supported only czech language and CZK currency is taken as base.*

You can see plot with your actual investments in stocks, and also your profit (generated from portfolio file). Below you can see your actual holdings and 
statistics about them. Only actual holdings with >0 count are shown. The last table is for dividends.
### Use cloud (Azure)
1. Create Azure account if you don't have it on: https://azure.microsoft.com/en-us/free
2. Create your Azure storage account as it's described in https://learn.microsoft.com/en-us/azure/storage/files/storage-how-to-use-files-portal?tabs=azure-portal (only part 'Create storage account')
3. In your storage account click on 'Access tokens' and get your connection string.
4. Set up cloud on your application:(if you set up cloud on your second device use `--tactic=cloud`, it determines init sync tactic [cloud files -> local files or local files -> cloud files])
```
stock_summary_tool set-cloud --cloud=azure --azure="{YOUR CONNECTION STRING} --tactic=local
``` 
### Rules about generating portfolio and balance
1. Entries are converted to the base currency with conversion rate for the execution day.
2. Dividends are converted to the base currency with conversion rate for the execution day.
3. Value of your portfolio for the current day is counted as sum of your holdings for the day. (converted to base currency)
4. Profit is comparison of your invested amount with dividends and your actual holdings. If you sell some stocks, profit stays same, only value of your portfolio goes down. Same with buy entries (portfolio up, profit stays same). If you get some dividends, it grows your profit by that amount.
5. ONCE AGAIN: All amounts are automatically converted to base currency by exchange rate of the execution day. It doesn't matter if you convert them or not. Right now it's out of scope of the tool.

### Plans for the future
1. Adding option for fees to the operations.
2. Supporting more languages and base currencies.
3. Adding backward possibility to generate portfolio and no need to generate it manually anymore (blocked by higher number of API calls and subscription)
4. Adding option to track other investments except stocks/cryptocurrencies/dividends.

Be free to open issue or ask me, if you want to know something or you want to help with the project.

