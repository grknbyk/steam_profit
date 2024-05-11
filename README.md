## Steam Market Analyzer

Steam Profit is a simple Python tool for analyzing the profitability of games on the Steam market. It utilizes the Steam open API to scrape game data and provide quick insights into potential profitability. <br>
### Recent Update
Due to a currency change on Steam (USD for Turkey), the tool's effectiveness in identifying profitable opportunities has been compromised. <br>
<br>
### How to use?
1. **Open the App**: Run the provided Python script or open the executable file

2. **Login to Steam**: Login to your Steam account via any browser.

3. **Retrieve LoginSecure and SessionID**: After logging in, retrieve your Steam `login_secure` and `sessionid` from your browser cookies. These cookies are necessary for the app to access the Steam API. Instructions for retrieving cookies may vary depending on your browser. In Google Chrome, you can typically access cookies by right-clicking on the page, selecting "Inspect," then navigating to the "Application" tab and selecting "Cookies" from the menu on the left. Find and copy the values for `login_secure` and `sessionid`.

4. **Use Steam Profit**: Paste the `login_secure` and `sessionid` values into the appropriate fields in the Steam Profit app. Once entered, the app will be able to access the Steam API and analyze game profitability.

5. **Adjust Settings**: Adjust settings as you intend. For example, you can set the game price limit to 3.

6. **Start Analysis**: Click the "Start Finding" button and wait until it's done. You will see a "Finished" message at the bottom of the info section.




#### Used Libraries
tkinter <br>
requests <br>
beautifulsoup4 <br>

## Screenshot
![Screenshot](https://github.com/grknbyk/steam_profit/blob/main/stmprft.png)
