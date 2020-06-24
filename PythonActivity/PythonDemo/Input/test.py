import camelot
import pandas
import time
import os
import datetime
import multiprocessing
from time import sleep
import math

def dispatch_jobs(data, job_number):
    total = len(data)
    chunk_size = total / job_number
    slice = chunks(data, int(math.ceil(chunk_size)))
    jobs = []
    mgr = multiprocessing.Manager()
    report = mgr.Namespace()
    report.df = pandas.DataFrame()
    output_final = mgr.Namespace()
    output_final.df = pandas.DataFrame()

    for i, s in enumerate(slice):
        j = multiprocessing.Process(target=do_job, args=(i, s, report,output_final))
        jobs.append(j)
    for j in jobs:
        j.start()
    for j in jobs:
        j.join()
    print("Done")
    output_final.df.to_csv("../../output.csv",index=False)
    report.df.to_csv("../../report.csv",index=False)
# split a list into evenly sized chunks
def chunks(l, n):
    # print([l[i:i+n] for i in range(0, len(l), n)])
    return [l[i:i+n] for i in range(0, len(l), n)]


def do_job(job_id, filenames, report, output_final):
    headers_list=["Invoice Header","Invoice Name","Loan #:", "Loan Type:", "Inv. ID / Cat. ID:", "Date Submitted:", "Invoice Date:", "Invoice #:", "Vendor Ref #:", "Referral Date", "Payee Code:", "Type:", "Order Date", "Order Complete Date", "Acquisition Date:", "Paid in Full Date:", "Foreclosure Removal", "SubmittedDate", "1st Reviewed Date", "Last Reviewed", "Accepted Date", "Approved Date", "Chk Requested", "Chk Confirmed", "Description(s) Category","Description(s) Sub Category", "Item Date", "Qty", "Item Price", "Orig. Billed", "Adjust", "Net", "Note:", "Service From Date:", "Service To Date:"]
    invoice_headers_list = ["Loan #:", "Loan Type:", "Inv. ID / Cat. ID:", "Date Submitted:", "Invoice Date:", "Invoice #:", "Vendor Ref #:", "Referral Date", "Payee Code:", "Type:", "Order Date", "Order Complete Date", "Acquisition Date:", "Paid in Full Date:", "Foreclosure Removal", "SubmittedDate", "1st Reviewed Date", "Last Reviewed", "Accepted Date", "Approved Date", "Chk Requested", "Chk Confirmed"]
    report_headers_list = ["Loan No.", "Total Invoices", "Success", "Fail"]
    temp_df_headers_list = ["Name","Ignore", "Item Date", "Qty", "Item Price", "Orig. Billed", "Adjust", "Net"]
    output_df = pandas.DataFrame(columns=headers_list)
    output_directory = "../../OUTPUT/"+str(datetime.datetime.now()).split('.')[0].replace(":","")+" Multi Job " + str(job_id)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    report_out = []
    for filename in filenames:
        each_file_out = []
        each_file_out.append(filename.split(".")[0])
        final_df = pandas.DataFrame(columns=headers_list)
        temp_directory = "../../TEMP/"+filename.split(".")[0]
        filename = "../../INPUT/"+filename
        print(filename)
        if not os.path.exists(temp_directory):
            os.makedirs(temp_directory)
        i=1
        invoice_start_pages=[]
        tables = camelot.read_pdf(filename, flavor="stream", edge_tol=1, row_tol=10,pages="all")
        for table in tables:
            df = table.df
            s = df[df.eq("Invoice #:").any(1)]
            if s.empty:
                pass
            else:
                invoice_start_pages.append(str(i))
            i=i+1
        number_of_invoices = len(invoice_start_pages)
        each_file_out.append(str(number_of_invoices))
        invoice_scanned = 0
        invoice_failed = 0
        for page in invoice_start_pages:
            try:
                invoice_more_than_one_page = False
                page_list = []
                value_list=[]
                page_list.append(page)
                extract = camelot.read_pdf(filename, flavor="stream", edge_tol=1, row_tol=10,pages=page, table_areas=["290,680,550,430","40,565,260,515"])
                df = pandas.DataFrame()
                for each_extract in extract:
                    df = df.append(each_extract.df)
                extract = camelot.read_pdf(filename, flavor="stream", edge_tol=1, row_tol=10,pages=page, table_areas=["50,345,595,300"])
                for each_extract in extract:
                    each_extract_df = each_extract.df
                    if each_extract_df.iloc[0][0] == "Outsourcer:":
                        each_extract_df = each_extract_df.drop([0])
                        each_extract_df = each_extract_df.reset_index(drop=True)
                    df = df.append(each_extract_df.transpose())
                try:
                    del df[2]
                except:
                    pass
                extract = camelot.read_pdf(filename, flavor="stream", edge_tol=1, row_tol=10,pages=page,table_areas=["100,750,600,630"])
                each_extract_df = extract[0].df
                try:
                    del each_extract_df[1]
                except:
                    pass
                # print(each_extract_df)
                invoice_description_row = 5
                for row_num in range(each_extract_df.shape[0]):
                    if "INVOICE" in each_extract_df.iloc[row_num][0]:
                        invoice_description_row = row_num
                each_extract_df = each_extract_df.iloc[[0,invoice_description_row]]
                # print(each_extract_df)
                each_extract_df.insert(loc=0,column=1, value=["Invoice Header","Invoice Name"])
                each_extract_df.columns=[0,1]
                df = df.append(each_extract_df)

                data_dict = df.set_index(0)[1].to_dict()
                data_dict.pop("",None)
                for each_header in headers_list:
                    try:
                        value_list.append(data_dict[each_header])
                    except:
                        value_list.append("")
                # print(data_dict)
                index_page = invoice_start_pages.index(page)
                try:
                    if (int(invoice_start_pages[index_page+1])-int(page))>2:
                        invoice_more_than_one_page = True
                        number_of_pages = int(invoice_start_pages[index_page+1])-int(page)
                        for p in range(1,number_of_pages-1):
                            page_list.append(str(int(page)+p))
                except:
                    pass


                extract = camelot.read_pdf(filename, flavor="stream", edge_tol=1, row_tol=10,pages=page, table_areas=["40,310,599,25"], columns=["245,296,350,380,433,503,559"])
                for each_extract in extract:
                    df = each_extract.df
                    for row in range(df.shape[0]):
                        if df.iloc[row][0] == "" or df.iloc[row][0] == None:
                            df.iloc[row][0] = df.iloc[row][1]
                        if df.iloc[row][1] == "" or df.iloc[row][1] == None:
                            df.iloc[row][1] = df.iloc[row][2]
                    temp_df = df.loc[(df[3] != "")]
                    temp_df = temp_df.loc[(df[3] != "Qty")]
                    row_items_index = list(temp_df.index.values)
                    new_df = pandas.DataFrame()
                    another_df = pandas.DataFrame()
                    for each_row in row_items_index:
                        if "Note:" in df.loc[each_row+1][0]:
                            try:
                                df.loc[each_row+1][0] =  df.loc[each_row+1][0].split(":")[1]
                            except:
                                pass
                            new_df = new_df.append(df.loc[[each_row+1]])
                        if "Service From" in df.loc[each_row+2][0]:
                            try:
                                df.loc[each_row+2][0] =  df.loc[each_row+2][0].split(" ")[4]
                            except:
                                pass
                            try:
                                df.loc[each_row+2][1] =  df.loc[each_row+2][1].split(" ")[4]
                            except:
                                pass
                            another_df = another_df.append(df.loc[[each_row+2]])
                    new_df = new_df.reset_index(drop=True)
                    new_df.drop(new_df.columns[1:(new_df.shape[1])], axis=1, inplace=True)
                    temp_df = temp_df.reset_index(drop=True)
                    temp_df.columns = temp_df_headers_list
                    # print(temp_df)
                    # print(temp_df.Name.str.split(" - ",n=1,expand=True))
                    temp_df[['Category','Sub Category']] = temp_df.Name.str.split(" - ",n=1,expand=True)
                    cols = temp_df.columns.tolist()
                    cols = cols[-2:] + cols[1:-2]
                    temp_df = temp_df[cols]
                    another_df = another_df.reset_index(drop=True)
                    try:
                        another_df.drop(another_df.columns[2:(another_df.shape[1])], axis=1,inplace=True)
                    except:
                        pass
                    temp_new_df = pandas.concat([temp_df, new_df, another_df], axis=1, ignore_index=True)
                    if len(page_list) > 1:
                        for extra_page_index in range(1,len(page_list)):
                            extract = camelot.read_pdf(filename, flavor="stream", edge_tol=1, row_tol=10,pages=page_list[extra_page_index], columns=["245,296,350,380,433,503,559"])
                            for each_extract in extract:
                                df = each_extract.df
                                for row in range(df.shape[0]):
                                    if df.iloc[row][0] == "" or df.iloc[row][0] == None:
                                        df.iloc[row][0] = df.iloc[row][1]
                                    if df.iloc[row][1] == "" or df.iloc[row][1] == None:
                                        df.iloc[row][1] = df.iloc[row][2]
                                
                                if df.loc[0][3] != "Qty":
                                    pass
                                else:
                                    temp_df = df.loc[(df[3] != "")]
                                    temp_df = temp_df.loc[(df[3] != "Qty")]
                                    if temp_df.empty == False:
                                        row_items_index = list(temp_df.index.values)
                                        new_df = pandas.DataFrame()
                                        another_df = pandas.DataFrame()


                                        for each_row in row_items_index:
                                            try:
                                                if "Note:" in df.loc[each_row+1][0]:
                                                    try:
                                                        df.loc[each_row+1][0] =  df.loc[each_row+1][0].split(":")[1]
                                                    except:
                                                        pass
                                                    new_df = new_df.append(df.loc[[each_row+1]])
                                            except:
                                                pass
                                            if "Service From" in df.loc[each_row+2][0]:
                                                try:
                                                    df.loc[each_row+2][0] =  df.loc[each_row+2][0].split(" ")[4]
                                                except:
                                                    pass
                                                try:
                                                    df.loc[each_row+2][1] =  df.loc[each_row+2][1].split(" ")[4]
                                                except:
                                                    pass
                                                another_df = another_df.append(df.loc[[each_row+2]])
                                        new_df = new_df.reset_index(drop=True)
                                        new_df.drop(new_df.columns[1:(new_df.shape[1])], axis=1, inplace=True)
                                        temp_df = temp_df.reset_index(drop=True)
                                        temp_df.columns = temp_df_headers_list
                                        temp_df[['Category','Sub Category']] = temp_df.Name.str.split(" - ",n=1,expand=True)
                                        cols = temp_df.columns.tolist()
                                        cols = cols[-2:] + cols[1:-2]
                                        temp_df = temp_df[cols]
                                        another_df = another_df.reset_index(drop=True)
                                        try:
                                            another_df.drop(another_df.columns[2:(another_df.shape[1])], axis=1,inplace=True)
                                        except:
                                            pass
                                        temp_new_df = temp_new_df.append(pandas.concat([temp_df, new_df, another_df], axis=1, ignore_index=True))
                    
                del temp_new_df[2]
                invoice_info = pandas.DataFrame([value_list])

                invoice_info.drop(invoice_info.columns[24:(invoice_info.shape[1])], axis=1, inplace=True)
                final_invoice_info = pandas.DataFrame()
                for i in range(temp_new_df.shape[0]):
                    final_invoice_info = final_invoice_info.append(invoice_info)
                # invoice_info.columns = invoice_headers_list
                temp_new_df = temp_new_df.reset_index(drop=True)
                final_invoice_info = final_invoice_info.reset_index(drop=True)
                temp_new_df = pandas.concat([final_invoice_info, temp_new_df], axis=1, ignore_index=True)
                final_df = final_df.append(temp_new_df)
                invoice_scanned += 1
            except:
                invoice_failed += 1
        each_file_out.append(str(invoice_scanned))
        each_file_out.append(str(invoice_failed))
        try:
            final_df.drop(final_df.columns[35:(final_df.shape[1])], axis=1, inplace=True)
            final_df.columns = headers_list
            output_df = output_df.append(final_df)
        except:
            pass
        # print(final_df)
        # final_df.columns = headers_list
        # output_df = output_df.append(final_df)
        # print(output_df)
        final_df.to_csv(temp_directory+"/Final.csv", index=False)
        report_out.append(each_file_out)
    out_report = pandas.DataFrame(report_out)
    out_report.columns = report_headers_list
    out_report.to_csv(output_directory+"/report.csv",index=False)
    report.df = report.df.append(out_report)
    output_df.to_csv(output_directory+"/output.csv",index=False)
    output_final.df = output_final.df.append(output_df)

def uipath_code():
    # raise Exception("Hiiiiiiiiiiiiiiiiiiii")
    raise Exception(__name__)
    exit()
    if __name__ == "__main__":
        os.chdir("C:\\RPA\\LspInvoiceDataScrape\\SRC\\LpsInvoiceDataScrape")
        start_time = time.time()
        dir_path = '../../INPUT'
        suffix = '.pdf'
        filepaths = []
        filenames = filter(lambda x: x.endswith(suffix), os.listdir(dir_path))
        filenames = list(filenames)
        for basename in filenames:
            filename = os.path.join(dir_path, basename)
            if os.path.isfile(filename):
                filepaths.append((basename,os.path.getsize(filename)))
        # print(filepaths)
        # print(filenames)
        dispatch_jobs(filenames,20)
        print("--- %s seconds ---" % (round(time.time() - start_time,2)))
if __name__ == "__main__":
    uipath_code()
    