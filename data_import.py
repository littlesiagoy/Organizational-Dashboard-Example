import pandas as pd

""" KPI #1 Imports"""
currencies = [
    "AUD",
    "CAD",
    "CHF",
    "CNY",
    "CRC",
    "EUR",
    "GBP",
    "JPY",
    "KRW",
    "MYR",
    "SEK",
    "SGD",
    "THB",
    "TWD",
    "USD",
]
valid_years = [22]


def import_sl_data():
    data = pd.DataFrame()
    for x in valid_years:
        data2 = pd.read_excel(
            "Data Inputs/KPI 1/SupplierLineItems FY" + str(x) + ".xlsx",
            engine="openpyxl",
        )
        data = pd.concat([data, data2])

    if ~data["Transaction Currency"].isin(currencies).all():
        raise Exception("Currency not previously encountered.")

    return data.drop_duplicates()


def import_ekbe_data():
    data = pd.DataFrame()

    for x in valid_years:
        data2 = pd.read_csv("Data Inputs/KPI 1/EKBE FY" + str(x) + ".txt")

        data2.columns = data2.columns.map(str.strip)

        data = pd.concat([data, data2])

    data["Mat. Doc."] = pd.to_numeric(data["Mat. Doc."], downcast="integer")
    data["Purch.Doc."] = pd.to_numeric(data["Purch.Doc."], downcast="integer")
    data["Item"] = pd.to_numeric(data["Item"], downcast="integer")
    data["MatYr"] = pd.to_numeric(data["MatYr"], downcast="integer")
    data["Pstng Date"] = pd.to_datetime(data["Pstng Date"], format="%m/%d/%Y")

    return data


def import_ekko_data():
    data = pd.DataFrame()

    for x in valid_years:
        data2 = pd.read_csv("Data Inputs/KPI 1/EKKO FY" + str(x) + ".txt")

        data2.columns = data2.columns.map(str.strip)

        data = pd.concat([data, data2])

    return data


def import_mara_data():
    data = pd.DataFrame()

    for x in valid_years:
        data2 = pd.read_csv("Data Inputs/KPI 1/MARA FY" + str(x) + ".txt")
        data2.columns = data2.columns.map(str.strip)

        data = pd.concat([data, data2])

    return data


def import_bkpf_data():
    data = pd.DataFrame()

    for x in valid_years:
        data2 = pd.read_csv("Data Inputs/KPI 1/BKPF FY" + str(x) + ".txt")

        data2.columns = data2.columns.map(str.strip)

        data = pd.concat([data, data2])

    # This is because Melanie's BKPF extract comes out as Object Key, while mine exports as Obj. key
    data = data.rename(columns={"Object key": "Obj. key"})

    data["DocumentNo"] = data["DocumentNo"].astype("Int64")
    data["Pstng Date"] = pd.to_datetime(data["Pstng Date"], format="%m/%d/%Y")
    data["Type"] = data["Type"].map(str.strip)
    data["Obj. key"] = pd.to_numeric(
        data["Obj. key"], downcast="integer", errors="coerce"
    ).astype(str)
    data["Reference"] = data["Reference"].str.strip()

    return data


def import_val_1_6_handling():
    data = pd.read_csv("Error Handling/Val 1.6 - Mixed Spend Type POs.csv")

    return data


""" KPI #2 Imports"""


def import_pr_data():
    raw_pr_data = pd.read_csv("Data Inputs/KPI 2/Requisition Base.csv")

    raw_pr_data["Requisitioning Date - PR"] = pd.to_datetime(
        raw_pr_data["Requisitioning Date - PR"], format="%Y-%m-%d"
    )

    raw_pr_data["Approved Date - PR"] = pd.to_datetime(
        raw_pr_data["Approved Date - PR"].replace("Unclassified", pd.NA),
        format="%Y-%m-%d",
    )

    return raw_pr_data


def import_po_data():
    raw_po_data = pd.read_csv(
        "Data Inputs/KPI 2/PO Base.csv", dtype={"[PO-P&I] Order Id": "str"}
    )

    raw_po_data = raw_po_data.rename(
        columns={
            "[PO-P&I] PO Id": "PO Id",
            "[PO-P&I] Order Id": "Order Id",
            "[PO-P&I]Ordered Date (Date)": "Ordered Date - PO",
            "[REQ]Requisition Date (Date)": "Requisition Date - PO",
            "[REQ] Requisition ID": "PR #",
            "[PO-P&I] Is PunchOut Item": "PunchOut Item?",
            "[PO-P&I]Supplier (ERP Supplier)": "Supplier Name",
            "sum(PO Spend)": "PO Spend",
        }
    )

    raw_po_data["Ordered Date - PO"] = pd.to_datetime(
        raw_po_data["Ordered Date - PO"], format="%Y-%m-%d"
    )

    return raw_po_data


def import_ahr_data():
    raw_ahr_data = pd.read_csv("Data Inputs/KPI 2/AHR.csv")

    raw_ahr_data.loc[
        raw_ahr_data["Approved Date - AHR"] == "Unclassified", "Approved Date - AHR"
    ] = pd.NaT
    raw_ahr_data["Approved Date - AHR"] = pd.to_datetime(
        raw_ahr_data["Approved Date - AHR"], format="%Y-%m-%d"
    )

    raw_ahr_data["Submit Date - AHR"] = pd.to_datetime(
        raw_ahr_data["Submit Date - AHR"], format="%Y-%m-%d"
    )

    raw_ahr_data["Assigned Date - AHR"] = pd.to_datetime(
        raw_ahr_data["Assigned Date - AHR"], format="%Y-%m-%d"
    )

    raw_ahr_data["Action Date - AHR"] = pd.to_datetime(
        raw_ahr_data["Action Date - AHR"], format="%Y-%m-%d %H:%M:%S"
    )

    return raw_ahr_data


def import_apr_data():
    raw_apr_data = pd.read_csv("Data Inputs/KPI 2/APR Base.csv")

    raw_apr_data = raw_apr_data.rename(
        columns={
            "Approved Date - Date": "Approved Date - APR",
            "Submit Date - Date": "Submit Date - APR",
        }
    )

    return raw_apr_data


def import_val_2_2_handling():
    data = pd.read_csv("Error Handling/Val 2.2 - Fixed Ordered Date.csv")

    data["Fixed Ordered Date"] = pd.to_datetime(
        data["Fixed Ordered Date"], format="%m/%d/%Y"
    )

    return data


def import_val_2_4_handling():
    data = pd.read_csv("Error Handling/Val 2.4 - Fixed Approved Date.csv")

    data["Fixed Approved Date"] = pd.to_datetime(
        data["Fixed Approved Date"], format="%m/%d/%Y"
    )

    return data


def import_val_2_6_handling():
    data = pd.read_csv("Error Handling/Val 2.6 - Straggler PR Entries.csv")

    return data


def import_val_2_9_handling():
    data = pd.read_csv("Error Handling/Val 2.9 - Fixed Submit Date.csv")

    data["Fixed Submit Date"] = pd.to_datetime(
        data["Fixed Submit Date"], format="%m/%d/%Y"
    )

    return data


def import_val_2_10_handling():
    data = pd.read_csv("Error Handling/Val 2.10 - Fixed Submit Date2.csv")

    data["Fixed Submit Date"] = pd.to_datetime(
        data["Fixed Submit Date"], format="%m/%d/%Y"
    )

    return data


def import_val_2_15_handling():
    data = pd.read_csv("Error Handling/Val 2.15 - Updated Relevant.csv")

    return data


""" KPI #3 Imports"""


def import_ah_inv_data():
    data = pd.read_csv("Data Inputs/KPI 3/Ariba/AH - Inv.csv")

    return data


def import_ah_pre_data():
    data = pd.read_csv("Data Inputs/KPI 3/Ariba/AH - Pre.csv")

    return data


def import_app_inv_data():
    data = pd.read_csv("Data Inputs/KPI 3/Ariba/App - Inv.csv")

    data["Approvable ID"] = data["Approvable ID"].str.replace("^IR", "INV", regex=True)

    return data


def import_app_pre_data():
    data = pd.read_csv("Data Inputs/KPI 3/Ariba/App - Pre.csv")

    return data


def import_inv_exc_data():
    data = pd.read_csv("Data Inputs/KPI 3/Ariba/Invoice - Exc.csv")

    return data


def import_inv_pay_data():
    data = pd.read_csv("Data Inputs/KPI 3/Ariba/Invoice - Pay.csv")

    data = data.rename(
        columns={
            "[IPT] Invoice ID": "Invoice ID",
            "[INV-P&I] Invoice Source Document": "Invoice Source - INVPAY",
            "[INV-P&I] PO Id": "PO Id",
        }
    )

    data["Invoice ID"] = data["Invoice ID"].str.replace("^IR", "INV", regex=True)

    return data


def import_inv_pro_data():
    data = pd.read_csv("Data Inputs/KPI 3/Ariba/Invoice - Pro.csv")
    data = data.rename(
        columns={
            "Supplier - ERP Supplier": "Supplier - INVPRO",
            "Supplier - ERP Supplier ID": "Supplier # - INVPRO",
            "Company Code - Company Code": "Company Code - INVPRO",
        }
    )

    data["Invoice ID"] = data["Invoice ID"].str.replace("^IR", "INV", regex=True)
    data["Company Code - INVPRO"] = pd.to_numeric(
        data["Company Code - INVPRO"], errors="coerce"
    )

    return data


def import_prerec_inv_data():
    data = pd.read_csv("Data Inputs/KPI 3/Ariba/Prerec - Inv.csv")

    return data


def import_rejected_inv_data():
    data = pd.read_csv("Data Inputs/KPI 3/Ariba/Rejected Inv.csv")

    return data


def import_val_3_1_handling():
    data = pd.read_csv("Error Handling/Val 3.1 - Fixed Submission Method.csv")

    return data


def import_val_3_3_handling():
    data = pd.read_csv(
        "Error Handling/Val 3.3 - Fixed Direct Indirect Classification.csv"
    )

    return data


def import_val_3_4_handling():
    data = pd.read_csv(
        "Error Handling/Val 3.4 - Fixed Direct Indirect Classification.csv"
    )

    return data


def import_val_3_7_handling():
    data = pd.read_csv("Error Handling/Val 3.7 - Fixed Supplier Names.csv")

    return data


def import_val_3_8_handling():
    data = pd.read_csv("Error Handling/Val 3.8 - Fixed Invoice Submission.csv")

    return data


def import_val_3_10_handling():
    data = pd.read_csv("Error Handling/Val 3.10 - Fixed Company Code.csv")

    return data


def import_document_query_data():
    data = pd.read_csv(
        "Data Inputs/KPI 3/Onbase/KPI 3 - DQ.csv",
        dtype={
            "Upload DateTime": str,
            "Note Type Name": str,
            "Note Contents": str,
            "Status Code": str,
        },
    )

    data["Document Date"] = pd.to_datetime(
        data["Document Date"], format="%m/%d/%Y %I:%M:%S %p"
    )
    data["Invoice Date"] = pd.to_datetime(
        data["Invoice Date"], format="%m/%d/%Y %I:%M:%S %p"
    )
    data["Upload DateTime"] = pd.to_datetime(
        data["Upload DateTime"], format="%m/%d/%Y %I:%M:%S %p"
    )
    data["Doc Import Date"] = pd.to_datetime(
        data["Doc Import Date"], format="%m/%d/%Y %I:%M:%S %p"
    )

    return data


def import_workflow_activity_adhoc_data():
    data = pd.read_csv("Data Inputs/KPI 3/Onbase/KPI 3 - WA Adhoc.csv")

    return data


def import_workflow_activity_trans_data():
    data = pd.read_csv("Data Inputs/KPI 3/Onbase/KPI 3 - WA Trans.csv")

    return data


def import_val_3_23_handling():
    data = pd.read_csv("Error Handling/Val 3.23 - Fixed Approved Date.csv")

    data["Fixed Approved Date"] = pd.to_datetime(
        data["Fixed Approved Date"], format="%m/%d/%Y"
    )

    return data


""" KPI #4 Imports"""


def kpi4_import_prerec():
    data = pd.read_csv("Data Inputs/KPI 4/Ariba/PREREC.csv")

    data["Date Created - PREREC"] = pd.to_datetime(
        data["Date Created - PREREC"], format="%m/%d/%Y"
    )

    return data


def kpi4_import_invpay():
    data = pd.read_csv("Data Inputs/KPI 4/Ariba/INVPAY.csv")

    data["App Date - INVPAY"] = pd.to_datetime(
        data["App Date - INVPAY"], format="%Y-%m-%d", errors="coerce"
    )

    data["Date Created - INVPAY"] = pd.to_datetime(
        data["Date Created - INVPAY"], format="%Y-%m-%d", errors="coerce"
    )

    return data


def kpi4_import_invrec():
    data = pd.read_csv("Data Inputs/KPI 4/Ariba/INVREC.csv", low_memory=False)

    data["Approved Date - INVREC"] = pd.to_datetime(
        data["Approved Date - INVREC"], format="%Y-%m-%d", errors="coerce"
    )

    data["Submit Date - INVREC"] = pd.to_datetime(
        data["Submit Date - INVREC"], format="%Y-%m-%d", errors="coerce"
    )

    return data


def import_val_3_16_handling():
    data = pd.read_csv("Error Handling/Val 3.16 - Fixed PREREC Direct-Indirect.csv")

    return data


def import_val_3_19_handling():
    data = pd.read_csv("Error Handling/Val 3.19 - Fixed INVREC Direct-Indirect.csv")

    return data


def import_val_3_26_handling():
    data = pd.read_csv(
        "Error Handling/Val 3.26 - Fixed Submission Method.csv",
        dtype={"Final Supplier": "str"},
    )

    return data


def import_apinv_data():
    data = pd.read_csv("Data Inputs/KPI 4/Ariba/APINV.csv")

    data["Action Date - APINV"] = pd.to_datetime(
        data["Action Date - APINV"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
    )

    return data


def import_appre_data():
    data = pd.read_csv("Data Inputs/KPI 4/Ariba/APPRE.csv")

    data["Action Date - APPRE"] = pd.to_datetime(
        data["Action Date - APPRE"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
    )

    return data


def import_ahinv_data():
    data = pd.read_csv("Data Inputs/KPI 4/Ariba/AHINV.csv")

    data["Action Date - AHINV"] = pd.to_datetime(
        data["Action Date - AHINV"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
    )
    data["Assign Date - AHINV"] = pd.to_datetime(
        data["Assign Date - AHINV"], format="%Y-%m-%d", errors="coerce"
    )

    return data


def import_ahpre_data():
    data = pd.read_csv("Data Inputs/KPI 4/Ariba/AHPRE.csv")

    data["Action Date - AHPRE"] = pd.to_datetime(
        data["Action Date - AHPRE"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
    )
    data["Assigned Date - AHPRE"] = pd.to_datetime(
        data["Assigned Date - AHPRE"], format="%Y-%m-%d", errors="coerce"
    )

    return data


def import_val_4_5_handling():
    data = pd.read_csv(
        "Error Handling/Val 4.5 - Fix Direct Indirect Classification.csv"
    )

    return data
