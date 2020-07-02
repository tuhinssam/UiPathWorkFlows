import pandas as pd
import xlwings as xw
def process():
    filename = "C:/Users/chetan.sharma/Desktop/Python_Projects/UipathTesting/Test.xlsx"
    wb = xw.Book(filename)
    sheet_no = 0
    column_no = 2
    output_file = "C:/Users/chetan.sharma/Desktop/Python_Projects/UipathTesting/Test1.xlsx"
    sheet = wb.sheets[int(sheet_no)]
    df = sheet.used_range.options(pd.DataFrame, index=False, header=True).value
    df_1 = df.iloc[: int(column_no)]
    df_1.to_excel(output_file, header=True)
    wb.close()