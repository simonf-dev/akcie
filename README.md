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
   2. Go to https://rapidapi.com/sparior/api/yahoo-finance15/ and obtain your API key.
   3. Save your key for the project:
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
2. Add your entries (example) - stock symbol, date, count of stocks, price:
   ```
   stock_summary_tool add-entry -s BOTZ.MI -d 12/01/2023 -c 20 -p 30
   ```
3. After you add your entries, generate actual portfolio and HTML:
   ```
   stock_summary_tool generate-portfolio
   stock_summary_tool generate-html
   ```
4. You can also export your data and share them across multiple systems (by importing them again):
   ```
   stock_summary_tool export-data -d <DIRECTORY_FOR_EXPORT>
   ```





