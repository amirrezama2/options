import yfinance as yf
import  openpyxl
import xlrd
import pandas as pd

ticker = yf.Ticker("^SPX")

x = ticker.option_chain()


calls = x.calls
puts = x.puts


for df in [calls,puts]:
    for col in df.columns:
        if isinstance(df[col].dtype, pd.DatetimeTZDtype):
            df[col] = df[col].dt.tz_localize(None)


with pd.ExcelWriter("SPX_Options.xlsx", engine='openpyxl', mode = 'w') as writer:
    calls.to_excel(writer, sheet_name= "Calls", index=False)
    puts.to_excel(writer, sheet_name="Puts", index = False)

