import pandas as pd
import numpy as np
import data_import as di


encountered_company_codes = [
    "Company 1",
    "Company 2",
    "Company 3",
    "Company 4",
    "Company 4",
    "Company 5",
    "Company 6",
    "Company 7",
    "Company 8",
    "Company 9",
    "Company 10",
    "Company 11",
    "Company 12",
    "Company 13",
    "Company 14",
    "Company 15",
    "Company 16",
]
relevant_company_codes = [
    "Company 1",
    "Company 2",
    "Company 3",
    "Company 4",
    "Company 5",
    "Company 6",
    "Company 10",
    "Company 12",
    "Company 13",
    "Company 14",
]
company_code_groupings = {
    "All": relevant_company_codes,
    "Holding Org 1": [
        "Company 1",
        "Company 2",
        "Company 3",
        "Company 4",
        "Company 5",
        "Company 14",
    ],
    "Holding Org 2": ["Company 12", "Company 13", "Company 15"],
    "Holding Org 3": ["Company 6", "Company 10"],
}

encountered_mtypes = [
    "ALB",
    "AWA",
    "ERT",
    "IDK",
    "MLB",
    "MRH",
    "MRO",
    "MRT",
    "NBW",
    "ROH",
    pd.NA,
]
relevant_mtype_groupings = {"Holding Org 1": ["MRO", "NBW"], "Holding Org 3": ["MRO"]}

encountered_je_types = [
    "Journal Entry Type 0",
    "Journal Entry Type 1",
    "Journal Entry Type 2",
    "Journal Entry Type 3",
    "Journal Entry Type 4",
    "Journal Entry Type 5",
    "Journal Entry Type 6",
    "Journal Entry Type 7",
    "Journal Entry Type 8",
    "Journal Entry Type 9",
    "Journal Entry Type 10",
    "Journal Entry Type 11",
    "Journal Entry Type 12",
    "Journal Entry Type 13",
    "Journal Entry Type 14",
    "Journal Entry Type 15",
    "Journal Entry Type 16",
    "Journal Entry Type 17",
    "Journal Entry Type 18",
    "Journal Entry Type 19",
    "Journal Entry Type 20",
    "Journal Entry Type 21",
    "Journal Entry Type 22",
    "Journal Entry Type 23",
    "Journal Entry Type 24",
    "Journal Entry Type 25",
    "Journal Entry Type 26",
    "Journal Entry Type 27",
]
irrelevant_je_types = [
    "Journal Entry Type 4",
    "Journal Entry Type 6",
    "Journal Entry Type 8",
    "Journal Entry Type 9",
    "Journal Entry Type 11",
    "Journal Entry Type 13",
    "Journal Entry Type 14",
    "Journal Entry Type 15",
    "Journal Entry Type 16",
    "Journal Entry Type 17",
    "Journal Entry Type 18",
    "Journal Entry Type 19",
    "Journal Entry Type 20",
    "Journal Entry Type 21",
    "Journal Entry Type 23",
    "Journal Entry Type 24",
    "Journal Entry Type 26",
]
relevant_je_types_groupings = {
    "Holding Org 1": [
        "Journal Entry Type 7",
        "Journal Entry Type 10",
        "Journal Entry Type 12",
        "Journal Entry Type 22",
        "Journal Entry Type 25",
        "Journal Entry Type 27",
    ],
    "Holding Org 2": ["Journal Entry Type 2", "Journal Entry Type 10"],
    "Holding Org 3": [
        "Journal Entry Type 0",
        "Journal Entry Type 1",
        "Journal Entry Type 2",
        "Journal Entry Type 5",
        "Journal Entry Type 10",
        "Journal Entry Type 22",
        "Journal Entry Type 25",
        "Journal Entry Type 27",
    ],
    "Holding Org 4": [
        "Journal Entry Type 2",
        "Journal Entry Type 10",
        "Journal Entry Type 12",
        "Journal Entry Type 22",
        "Journal Entry Type 27",
    ],
}

irrelevant_supplier_types = ["TIC", "TEV"]

encountered_ic_vendors = [
    "IC01",
    "IC02",
    "IC03",
    "IC04",
    "IC05",
    "IC06",
    "IC07",
    "IC08",
    "IC09",
    "IC10",
    "IC11",
    "IC12",
    "IC13",
    "IC14",
    "IC15",
    "IC16",
    "IC17",
    "IC18",
    "IC19",
    "IC20",
    "IC21",
    "IC22",
    "IC23",
    "IC24",
    "IC25",
    "IC26",
    "IC27",
    "IC28",
    "IC29",
]

""" KPI #1 - % of PO vs Non-PO Transactions"""

# 1) Import Supplier Line Item Data
# check0 = input(
#     'Did you export Supplier Line Data from S4 using the "KPI1" filter and "KPI1" column variant as an xlsx?'
# )
kpi1_sl_data = di.import_sl_data()

# 2) Import EKBE Data
# check1 = input(
#     "Did you export EKBE for only Invoice Postings (Q & O & N types), used the Spend variant, and "
#     "exported as txt file?"
# )
ekbe = di.import_ekbe_data()

# 3) Import EKKO data
pd.DataFrame(set(ekbe["Purch.Doc."])).to_csv("EKKO Input.csv")
# check2 = input("Did you export EKKO as txt using EKKO Input file & the Spend Variant?")
ekko = di.import_ekko_data()

# 4) Determine which entries in EKBE are relevant or not.
data = ekbe.copy()


def kpi1_determine_ekbe_relevant_entries(data):
    data = data.merge(
        ekko[["Purch.Doc.", "CoCd", "Vendor"]], how="left", on="Purch.Doc."
    )

    # Hard Validation 1.1 - Ensure that all entries in data have a corresponding company code.
    if data["CoCd"].isna().any():
        data.loc[data["CoCd"].isna()].to_csv("test1.1.csv")

    data["Relevant CoCd?"] = pd.NA
    data["Relevant CoCd?"] = data["CoCd"].isin(relevant_company_codes)

    # Hard Validation 1.2 - Check that there are 0 EKBE entries with a previously unaccounted for company code.
    val_1_2_bool = data["CoCd"].isin(encountered_company_codes)
    if ~val_1_2_bool.all():
        data.loc[~val_1_2_bool].to_csv("test1.2.csv")

    # Import MARA data
    pd.DataFrame(set(data["Material"])).to_excel("MARA Input.xlsx")
    # check3 = input(
    #     "Did you use the Mara Input file, & Spend variant to export Mara as a txt?"
    # )
    mara = di.import_mara_data()

    # We ignore all RM & FG material types.
    data = data.merge(mara, on="Material", how="left")
    data["Relevant MType?"] = False

    for group in relevant_mtype_groupings:
        company_list = company_code_groupings[group]
        company_mtype_list = relevant_mtype_groupings[group]

        rel_mtype_bool = [
            all(t)
            for t in zip(
                data["CoCd"].isin(company_list), data["MTyp"].isin(company_mtype_list)
            )
        ]

        data.loc[rel_mtype_bool, "Relevant MType?"] = True

    data.loc[data["MTyp"].isna(), "Relevant MType?"] = True

    # Assumption 1.3
    val_1_6_handling = di.import_val_1_6_handling()
    for x in val_1_6_handling["Mat. Doc."]:
        data.loc[data["Mat. Doc."] == x, "Relevant MType?"] = val_1_6_handling.loc[
            val_1_6_handling["Mat. Doc."] == x, "Adjusted Spend"
        ].squeeze()

    # Hard Validation 1.3 - Check that there are 0 EKBE entries where a new material type was used.
    val_1_3_bool = [
        all(t)
        for t in zip(~data["MTyp"].isin(encountered_mtypes), ~data["MTyp"].isna())
    ]
    if data.loc[val_1_3_bool].shape[0] > 0:
        data.loc[val_1_3_bool].to_csv("test1.3.csv")

    # Hard Validation 1.4 - Check that there are 0 EKBE entries where there is a material populated, but no type.
    data.loc[data["Material"] == "Material 0", "Material"] = ""

    val_1_4_bool = [all(t) for t in zip(data["Material"] != "", data["MTyp"].isna())]
    if data.loc[val_1_4_bool].shape[0] > 0:
        data.loc[val_1_4_bool].to_csv("test1.4.csv")

    data["Final Relevant?"] = pd.NA
    data.loc[data["Relevant MType?"] & data["Relevant CoCd?"], "Final Relevant?"] = True
    data.loc[
        (data["Relevant MType?"].isin([False]))
        | (data["Relevant CoCd?"].isin([False])),
        "Final Relevant?",
    ] = False

    # Hard Validation 1.5 - Check that there are 0 EKBE entries not classified as relevant or not.
    val_1_5_bool = data["Final Relevant?"].isnull()
    if val_1_5_bool.any():
        data.loc[val_1_5_bool].to_csv("test1.5.csv")

    # Hard Validation 1.6 - Check that there are 0 EKBE mat docs that contain both irrelevant/relevant entries.
    val_1_6_table = (
        data[["Mat. Doc.", "Final Relevant?"]]
        .groupby("Mat. Doc.")
        .nunique("Final Relevant?")
    )
    if (val_1_6_table > 1).any().squeeze():
        data.to_csv("test1.6 data.csv")
        val_1_6_table.to_csv("test1.6.csv")

    # Hard Validation 1.7 - Check that there are 0 EKBE mat docs that contain multiple date postings.
    val_1_7_table = (
        data[["Mat. Doc.", "Pstng Date"]].groupby("Mat. Doc.").nunique("Pstng Date")
    )
    if (val_1_7_table > 1).any().squeeze():
        val_1_7_table.to_csv("test1.7.csv")

    # Hard Validation 1.8 - Check that there are 0 relevant EKBE mat docs that contain mult vendors.
    val_1_8_table = (
        data.loc[data["Final Relevant?"], ["Mat. Doc.", "Vendor"]]
        .groupby("Mat. Doc.")
        .nunique("Vendor")
    )
    if (val_1_8_table > 1).any().squeeze():
        val_1_8_table.to_csv("test1.8.csv")

    return data


ekbe = kpi1_determine_ekbe_relevant_entries(ekbe)

# 5) Create links from EKBE to SL


def kpi1_create_ek_to_sl_link(data):
    data["In SL?"] = data["Mat. Doc."].isin(kpi1_sl_data["Journal Entry"])

    # Assumption #1.1 - From 7/1/20 - 3/31/22 there's an amount difference of ~$500K between SL & ekbe.
    # Acceptable since overall spend of Journal Entry Type 3 types in both files is ~$1B.

    # Export list of unaccounted data entries for BKPF extract
    ekbe_unaccounted_bool = [
        all(t) for t in zip(~data["In SL?"], data["Relevant CoCd?"])
    ]

    data["BKPF Key"] = pd.NA
    data.loc[ekbe_unaccounted_bool, "BKPF Key"] = data.loc[
        ekbe_unaccounted_bool, "Mat. Doc."
    ].astype(str) + data.loc[ekbe_unaccounted_bool, "MatYr"].astype(str)

    data.loc[~data["BKPF Key"].isnull(), "BKPF Key"].to_excel("BKPF Input.xlsx")

    # Create BKPF Link to SL
    # check4 = input(
    #     "Did you export BKPF as a txt using the spend variant, using the BKPF Input file? Remember to put "
    #     "filter onto the Object Key field not doc number."
    # )
    bkpf = di.import_bkpf_data()
    bkpf["SL Key"] = (
        bkpf["DocumentNo"].astype(str)
        + "-"
        + bkpf["Type"]
        + "-"
        + bkpf["Pstng Date"].astype(str)
        + "-"
        + bkpf["Reference"]
        + "-"
        + bkpf["CoCd"].astype(str)
    )
    bkpf = bkpf.merge(
        data[["BKPF Key", "Final Relevant?"]],
        left_on="Obj. key",
        right_on="BKPF Key",
        how="left",
    ).drop_duplicates()

    return data, bkpf


def kpi1_link_sl_ekbe_(sl, ek):
    ek, bkpf = kpi1_create_ek_to_sl_link(ek)

    # Create SL Reference Key
    sl["SL Key"] = (
        sl["Journal Entry"].astype(str)
        + "-"
        + sl["Journal Entry Type"]
        + "-"
        + sl["Posting Date"].astype(str)
        + "-"
        + sl["Reference"]
        + "-"
        + sl["Company Code"].astype(str)
    )

    # 6) Using the Journal Entry & SL Key, flag which SL entries are irrelevant.

    sl = sl.merge(
        ek[["Mat. Doc.", "Final Relevant?"]],
        how="left",
        left_on="Journal Entry",
        right_on="Mat. Doc.",
    ).drop_duplicates()

    sl = sl.merge(
        bkpf[["SL Key", "Final Relevant?"]],
        how="left",
        on="SL Key",
        suffixes=("_ekbe", "_bkpf"),
    ).drop_duplicates()

    return sl


kpi1_sl_data = kpi1_link_sl_ekbe_(kpi1_sl_data, ekbe)


def kpi1_determine_sl_relevant_entries(data):
    data["Relevant?"] = pd.NA

    # We know the following Types are always irrelevant
    auto_irrelevant_je_bool = data["Journal Entry Type"].isin(irrelevant_je_types)
    data.loc[auto_irrelevant_je_bool, "Relevant?"] = False

    # 7) Using the relevant columns pulled form EKBE & BKPF, flag the relevant entries.
    data.loc[data["Final Relevant?_ekbe"].isin([True]), "Relevant?"] = True
    data.loc[data["Final Relevant?_ekbe"].isin([False]), "Relevant?"] = False

    data.loc[data["Final Relevant?_bkpf"].isin([True]), "Relevant?"] = True
    data.loc[data["Final Relevant?_bkpf"].isin([False]), "Relevant?"] = False

    # Hard Validation 1.11
    val_1_11_bool = pd.Series(list(set(data["Journal Entry Type"]))).isin(
        encountered_je_types
    )
    if ~val_1_11_bool.all():
        data.loc[~data["Journal Entry Type"].isin(encountered_je_types)].to_csv(
            "test1.11.csv"
        )

    # Assumption 1.2 - Due to BKPF entries being able to span multiple PO #s, any Journal Entry Type 3 from Company 14
    # and supplier is IC'Company 4' is auto classified as irrelevant even though mtype is relevant.
    data.loc[data["Journal Entry Type"] == "Journal Entry Type 1", "Relevant?"] = False

    # Apply relevant JE by Company (note that Journal Entry Type 3 not included since already accounted through EKBE).
    for group, values in relevant_je_types_groupings.items():
        if group == "Holding Org 4":
            relevant_je_bool = [
                all(t)
                for t in zip(
                    data["Company Code"].isin(["Company 9"]),
                    data["Journal Entry Type"].isin(values),
                )
            ]
        else:
            relevant_je_bool = [
                all(t)
                for t in zip(
                    data["Company Code"].isin(company_code_groupings[group]),
                    data["Journal Entry Type"].isin(values),
                )
            ]

        data.loc[relevant_je_bool, "Relevant?"] = True

    # 9) we will flag all intercompany/employee entries as irrelevant as part of our criteria.
    data.loc[
        data["Supplier Acct Group"].isin(irrelevant_supplier_types), "Relevant?"
    ] = False

    # Assumption 1.4
    val_1_4_bool = [
        all(t)
        for t in zip(
            data["Relevant?"].isna(),
            data["Journal Entry Type"].isin(["Journal Entry Type 3"]),
        )
    ]
    data.loc[val_1_4_bool, "Relevant?"] = True

    # Hard Validation 1.9 - Check that there are 0 entries in SL that have not been accounted for.
    if data["Relevant?"].isna().any():
        data.loc[data["Relevant?"].isna()] = False

    return data


kpi1_sl_data = kpi1_determine_sl_relevant_entries(kpi1_sl_data)


def kpi1_determine_po_non_po_breakdown(data):
    # 10) Determine PO vs Non-PO Breakdown
    data["Transaction Type"] = pd.NA

    # If an entry has a relevance flag in ekbe or bkpf, then it is tied to a PO.  Otherwise, non-po.
    po_classification_bool = [
        any(t)
        for t in zip(
            ~data["Final Relevant?_ekbe"].isna(), ~data["Final Relevant?_bkpf"].isna()
        )
    ]

    non_po_classification_bool = [
        all(t)
        for t in zip(
            data["Final Relevant?_ekbe"].isna(), data["Final Relevant?_bkpf"].isna()
        )
    ]

    data.loc[po_classification_bool, "Transaction Type"] = "PO"
    data.loc[non_po_classification_bool, "Transaction Type"] = "Non-PO"

    # Hard Validation 1.10 - Check that there are 0 entries in SL that has not been classified as non-po vs po.
    if data["Transaction Type"].isna().any():
        data.loc[data["Transaction Type"].isna()].to_csv("test1.10.csv")

    return data


kpi1_sl_data = kpi1_determine_po_non_po_breakdown(kpi1_sl_data)


""" KPI #2 - PR/PO Approval Turnaround Time"""

# check5 = input("Have you exported the Ariba data for KPI 2,3,4?")
raw_pr_data = di.import_pr_data()
raw_po_data = di.import_po_data()
raw_ahr_data = di.import_ahr_data()
raw_apr_data = di.import_apr_data()

# Hard Validation 2.2
val_2_2_handling = di.import_val_2_2_handling()
raw_po_data = raw_po_data.merge(val_2_2_handling, how="left", on="PR #")

raw_po_data.loc[
    ~raw_po_data["Fixed Ordered Date"].isna(), "Ordered Date - PO"
] = raw_po_data.loc[~raw_po_data["Fixed Ordered Date"].isna(), "Fixed Ordered Date"]
raw_po_data = raw_po_data.drop("Fixed Ordered Date", axis=1)
raw_po_data = raw_po_data.drop_duplicates()

val_2_2_bool = (
    raw_po_data[["PR #", "Ordered Date - PO"]].groupby("PR #").nunique() > 1
).reset_index()
if val_2_2_bool.loc[val_2_2_bool["Ordered Date - PO"]].shape[0] > 0:
    val_2_2_bool.loc[val_2_2_bool["Ordered Date - PO"]].to_csv("test2.2.csv")


# Generate master PR list from PO/PR/AHR/APR based on PR #
kpi2_master_pr_list = pd.DataFrame(
    pd.concat(
        [
            raw_pr_data["PR #"],
            raw_po_data["PR #"],
            raw_ahr_data["Approvable ID"],
            raw_apr_data["Approvable ID"],
        ]
    ).drop_duplicates()
)

kpi2_master_pr_list.columns = ["PR #"]

# Determine sources of PR.
kpi2_master_pr_list["In PR?"] = kpi2_master_pr_list["PR #"].isin(raw_pr_data["PR #"])
kpi2_master_pr_list["In PO?"] = kpi2_master_pr_list["PR #"].isin(raw_po_data["PR #"])
kpi2_master_pr_list["In AHR?"] = kpi2_master_pr_list["PR #"].isin(
    raw_ahr_data["Approvable ID"]
)
kpi2_master_pr_list["In APR?"] = kpi2_master_pr_list["PR #"].isin(
    raw_apr_data["Approvable ID"]
)


# Pull in Supplier Names from PR/PO.
supplier_name_table = pd.concat(
    [raw_pr_data[["PR #", "Supplier Name"]], raw_po_data[["PR #", "Supplier Name"]]]
).drop_duplicates()
kpi2_master_pr_list = kpi2_master_pr_list.merge(
    supplier_name_table, how="left", on="PR #"
)


# Pull in Punchout indicator from PR/PO.
punchout_table = pd.concat(
    [
        raw_pr_data[["PR #", "Supplier Name", "PunchOut Item?"]],
        raw_po_data[["PR #", "Supplier Name", "PunchOut Item?"]],
    ]
).drop_duplicates()
kpi2_master_pr_list = kpi2_master_pr_list.merge(
    punchout_table, how="left", on=["PR #", "Supplier Name"]
)


# Assumption 2.1
def determine_rel1(data):
    num_of_approvals_table = (
        raw_apr_data[["Approvable ID", "Approver"]]
        .groupby("Approvable ID")
        .count()
        .rename(columns={"Approver": "# of Approvals"})
    )
    data = data.merge(
        num_of_approvals_table, how="left", left_on="PR #", right_index=True
    )

    approvals_deleted_data = raw_apr_data.loc[
        ~raw_apr_data["Approver Deleted By"].isna(), ["Approvable ID", "Approver"]
    ]
    approvals_deleted_table = (
        approvals_deleted_data.groupby("Approvable ID")
        .count()
        .rename(columns={"Approver": "# of Deleted Approvers"})
    )
    data = data.merge(
        approvals_deleted_table, how="left", left_on="PR #", right_index=True
    )

    data["# Delete == # App?"] = (
        data["# of Approvals"] == data["# of Deleted Approvers"]
    )

    data["Rel 1?"] = pd.NA
    data.loc[data["# Delete == # App?"], "Rel 1?"] = False

    return data


kpi2_master_pr_list = determine_rel1(kpi2_master_pr_list)


def determine_rel2_3_4(data):
    # Assumption 2.2
    data["Rel 2?"] = pd.NA
    relevant_bool2 = [
        all(t)
        for t in zip(
            data["Rel 1?"].isna(),
            data["In AHR?"].isin([False]),
            data["In APR?"].isin([False]),
            data["PunchOut Item?"].isin([True]),
        )
    ]
    data.loc[relevant_bool2, "Rel 2?"] = False

    # Assumption 2.3
    data["Rel 3?"] = pd.NA
    relevant_bool3 = [
        all(t)
        for t in zip(
            data["Rel 1?"].isna(),
            data["Rel 2?"].isna(),
            data["In AHR?"].isin([False]),
            data["In APR?"].isin([False]),
            data["Supplier Name"].isin(["PRACTICAL TOOLS INC"]),
        )
    ]
    data.loc[relevant_bool3, "Rel 3?"] = False

    # Assumption 2.4
    data["Rel 4?"] = pd.NA
    relevant_bool4 = [
        all(t)
        for t in zip(
            data["Rel 1?"].isna(),
            data["Rel 2?"].isna(),
            data["Rel 3?"].isna(),
            data["In AHR?"].isin([False]),
            data["In APR?"].isin([False]),
            ~data["Supplier Name"].isin(["PRACTICAL TOOLS INC"]),
        )
    ]
    data.loc[relevant_bool4, "Rel 4?"] = False

    return data


kpi2_master_pr_list = determine_rel2_3_4(kpi2_master_pr_list)


# Assumption 2.5
def determine_rel5(data):
    submitted_pr_bool = [
        all(t)
        for t in zip(
            raw_apr_data["Type"] == "Approver",
            raw_apr_data["Approver State"] == "Active",
        )
    ]
    submitted_prs = raw_apr_data.loc[submitted_pr_bool, "Approvable ID"]

    rel5_bool = data["PR #"].isin(submitted_prs)

    data["Rel 5?"] = pd.NA
    data.loc[rel5_bool, "Rel 5?"] = False

    return data


kpi2_master_pr_list = determine_rel5(kpi2_master_pr_list)


# Assumption 2.6
def determine_rel6(data):
    raw_data = raw_apr_data.copy()

    # Filter for Prs that has had an approver status of denied.
    denied_pr_table = raw_data.loc[
        raw_data["Approver State"] == "Denied", "Approvable ID"
    ].drop_duplicates()
    relevant_data = raw_data.loc[raw_data["Approvable ID"].isin(denied_pr_table)]

    # Pull the latest action date entry for each PR.
    relevant_data.loc[~relevant_data["Action Date"].isna()].sort_values(
        "Action Date", ascending=False
    )
    latest_entry_data = (
        relevant_data.loc[~relevant_data["Action Date"].isna()]
        .sort_values("Action Date", ascending=False)
        .groupby("Approvable ID")
        .head(1)
    )

    denied_prs_table = latest_entry_data.loc[
        latest_entry_data["Approver State"] == "Denied", "Approvable ID"
    ]

    data["Rel 6?"] = pd.NA

    data.loc[data["PR #"].isin(denied_prs_table), "Rel 6?"] = False

    return data


kpi2_master_pr_list = determine_rel6(kpi2_master_pr_list)


# Assumption 2.7
def determine_rel7(data):
    data["Rel 7?"] = pd.NA
    mixed_item_types = (
        data[["PR #", "PunchOut Item?"]]
        .groupby(["PR #"])
        .nunique()
        .rename(columns={"PunchOut Item?": "# of Types"})
    )
    mixed_item_types = mixed_item_types.loc[mixed_item_types["# of Types"] > 1]

    data.loc[data["PR #"].isin(mixed_item_types.index), "Rel 7?"] = True

    return data


kpi2_master_pr_list = determine_rel7(kpi2_master_pr_list)


# Assumption 2.8
def determine_rel8(data):
    data["Rel 8?"] = pd.NA

    rel_bool = [
        all(t)
        for t in zip(~data["In PR?"], ~data["In PO?"], data["In AHR?"], data["In APR?"])
    ]
    data.loc[rel_bool, "Rel 8?"] = False

    # Hard Validation 2.1
    val_2_1_bool = [
        all(t) for t in zip(data["Rel 7?"].isin([True]), data["Rel 8?"].isin([False]))
    ]
    if data.loc[val_2_1_bool].shape[0] > 0:
        data.loc[val_2_1_bool].to_csv("test2.1.csv")

    return data


kpi2_master_pr_list = determine_rel8(kpi2_master_pr_list)


# Assumption 2.9
def determine_rel9(data):
    data["Rel 9?"] = pd.NA

    data.loc[data["PR #"].isin(raw_po_data["PR #"]), "Rel 9?"] = True

    return data


kpi2_master_pr_list = determine_rel9(kpi2_master_pr_list)


# Assumption 2.10
def determine_rel10(data):
    data["Rel 10?"] = pd.NA

    data.loc[
        data["PR #"].isin(
            raw_pr_data.loc[raw_pr_data["PO Id"] != "Unclassified", "PR #"]
        ),
        "Rel 10?",
    ] = True

    return data


kpi2_master_pr_list = determine_rel10(kpi2_master_pr_list)


# Assumption 2.13
def determine_rel11(data):
    data["Rel 11?"] = pd.NA

    rel11_bool = [
        all(t)
        for t in zip(
            data["In PR?"].isin([False]),
            data["In PO?"].isin([False]),
            data["In AHR?"].isin([True]),
            data["In APR?"].isin([False]),
        )
    ]

    data.loc[rel11_bool, "Rel 11?"] = True

    return data


kpi2_master_pr_list = determine_rel11(kpi2_master_pr_list)


def determine_final_relevant(data):
    data["Final Relevant?"] = pd.NA

    bool1 = [
        all(t)
        for t in zip(data["Final Relevant?"].isna(), data["Rel 1?"].isin([False]))
    ]
    data.loc[bool1, "Final Relevant?"] = False

    bool2 = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isna(),
            data["Rel 1?"].isna(),
            data["Rel 2?"].isin([False]),
        )
    ]
    data.loc[bool2, "Final Relevant?"] = False

    bool3 = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isna(),
            data["Rel 1?"].isna(),
            data["Rel 2?"].isna(),
            data["Rel 3?"].isin([False]),
        )
    ]
    data.loc[bool3, "Final Relevant?"] = False

    bool4 = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isna(),
            data["Rel 1?"].isna(),
            data["Rel 2?"].isna(),
            data["Rel 3?"].isna(),
            data["Rel 4?"].isin([False]),
        )
    ]
    data.loc[bool4, "Final Relevant?"] = False

    bool5 = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isna(),
            data["Rel 1?"].isna(),
            data["Rel 2?"].isna(),
            data["Rel 3?"].isna(),
            data["Rel 4?"].isna(),
            data["Rel 5?"].isin([False]),
        )
    ]
    data.loc[bool5, "Final Relevant?"] = False

    bool6 = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isna(),
            data["Rel 1?"].isna(),
            data["Rel 2?"].isna(),
            data["Rel 3?"].isna(),
            data["Rel 4?"].isna(),
            data["Rel 5?"].isna(),
            data["Rel 6?"].isin([False]),
        )
    ]
    data.loc[bool6, "Final Relevant?"] = False

    bool7 = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isna(),
            data["Rel 1?"].isna(),
            data["Rel 2?"].isna(),
            data["Rel 3?"].isna(),
            data["Rel 4?"].isna(),
            data["Rel 5?"].isna(),
            data["Rel 6?"].isna(),
            data["Rel 7?"].isin([True]),
        )
    ]
    data.loc[bool7, "Final Relevant?"] = True

    bool8 = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isna(),
            data["Rel 1?"].isna(),
            data["Rel 2?"].isna(),
            data["Rel 3?"].isna(),
            data["Rel 4?"].isna(),
            data["Rel 5?"].isna(),
            data["Rel 6?"].isna(),
            data["Rel 7?"].isna(),
            data["Rel 8?"].isin([False]),
        )
    ]
    data.loc[bool8, "Final Relevant?"] = False

    bool9 = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isna(),
            data["Rel 1?"].isna(),
            data["Rel 2?"].isna(),
            data["Rel 3?"].isna(),
            data["Rel 4?"].isna(),
            data["Rel 5?"].isna(),
            data["Rel 6?"].isna(),
            data["Rel 7?"].isna(),
            data["Rel 8?"].isna(),
            data["Rel 9?"].isin([True]),
        )
    ]
    data.loc[bool9, "Final Relevant?"] = True

    bool10 = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isna(),
            data["Rel 1?"].isna(),
            data["Rel 2?"].isna(),
            data["Rel 3?"].isna(),
            data["Rel 4?"].isna(),
            data["Rel 5?"].isna(),
            data["Rel 6?"].isna(),
            data["Rel 7?"].isna(),
            data["Rel 8?"].isna(),
            data["Rel 9?"].isna(),
            data["Rel 10?"].isin([True]),
        )
    ]
    data.loc[bool10, "Final Relevant?"] = True

    bool11 = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isna(),
            data["Rel 1?"].isna(),
            data["Rel 2?"].isna(),
            data["Rel 3?"].isna(),
            data["Rel 4?"].isna(),
            data["Rel 5?"].isna(),
            data["Rel 6?"].isna(),
            data["Rel 7?"].isna(),
            data["Rel 8?"].isna(),
            data["Rel 9?"].isna(),
            data["Rel 10?"].isna(),
            data["Rel 11?"].isin([True]),
        )
    ]
    data.loc[bool11, "Final Relevant?"] = True

    return data


kpi2_master_pr_list = determine_final_relevant(kpi2_master_pr_list)


def cleanse_ahr_app_data(data):
    val_2_4_handling = di.import_val_2_4_handling()

    for x in val_2_4_handling["Approvable ID"]:
        data.loc[
            data["Approvable ID"] == x, "Approved Date - AHR"
        ] = val_2_4_handling.loc[
            val_2_4_handling["Approvable ID"] == x, "Fixed Approved Date"
        ].values[
            0
        ]

    # Hard Validation 2.4
    val_2_4_bool = (
        data.loc[
            ~data["Approved Date - AHR"].isna(),
            ["Approvable ID", "Approved Date - AHR"],
        ]
        .groupby("Approvable ID")
        .nunique()
        > 1
    ).reset_index()
    if val_2_4_bool["Approved Date - AHR"].any():
        val_2_4_bool.to_csv("test2.4.csv")

    return data.drop("count()", axis=1).drop_duplicates().dropna()


def pull_in_approved_dates(data):
    data = data.merge(
        cleanse_ahr_app_data(raw_ahr_data)[
            ["Approvable ID", "Approved Date - AHR"]
        ].drop_duplicates(),
        how="left",
        left_on="PR #",
        right_on="Approvable ID",
    ).drop("Approvable ID", axis=1)

    return data


kpi2_master_pr_list = pull_in_approved_dates(kpi2_master_pr_list)


# Assumption 2.14
def update_rel_11(data):
    updated_rel_11_bool = [
        all(t)
        for t in zip(data["Rel 11?"].isin([True]), data["Approved Date - AHR"].isna())
    ]

    data.loc[updated_rel_11_bool, "Rel 11?"] = False
    data.loc[updated_rel_11_bool, "Final Relevant?"] = False

    return data


kpi2_master_pr_list = update_rel_11(kpi2_master_pr_list)


# Hard Validation 2.6
def val_2_6_handling(data):
    val_2_6_data = di.import_val_2_6_handling()

    for x in val_2_6_data["PR #"]:
        data.loc[data["PR #"] == x, "Final Relevant?"] = val_2_6_data.loc[
            val_2_6_data["PR #"] == x, "Identified Relevant?"
        ].values[0]

    return data


kpi2_master_pr_list = val_2_6_handling(kpi2_master_pr_list)


def calc_sub_date_single_submission(data):
    # Handle Single submission, Non-denied, is non-catalog
    non_deny_non_cat_bool = [
        all(t)
        for t in zip(data["Denied?"].isin([False]), data["Non-Cat?"].isin([True]))
    ]
    non_deny_non_cat_table = (
        data.loc[non_deny_non_cat_bool, ["Assigned Date - AHR", "Approvable ID"]]
        .sort_values("Assigned Date - AHR")
        .groupby("Approvable ID")
        .head(1)
        .rename(columns={"Assigned Date - AHR": "New Assigned Date1"})
    )
    data = data.merge(non_deny_non_cat_table, how="left", on="Approvable ID")

    # Handle Single Submission, non-denied, catalog
    non_deny_cat_bool = [
        all(t)
        for t in zip(data["Denied?"].isin([False]), data["Non-Cat?"].isin([False]))
    ]
    non_deny_cat_table = (
        data.loc[non_deny_cat_bool, ["Assigned Date - AHR", "Approvable ID"]]
        .sort_values("Assigned Date - AHR")
        .groupby("Approvable ID")
        .head(1)
        .rename(columns={"Assigned Date - AHR": "New Assigned Date2"})
    )
    data = data.merge(non_deny_cat_table, how="left", on="Approvable ID")

    # Handle single submission, denied, is non-catalog
    # Note that there will be slight inaccuracies, due to constant withdrawing & resubmit without Approver Reason - AHR.
    last_deny_non_cat_bool = [
        all(t)
        for t in zip(
            data["Denied?"].isin([True]),
            data["Non-Cat?"].isin([True]),
            data["Approver State - AHR"].isin(["Denied"]),
        )
    ]

    latest_deny_non_cat_table = (
        data.loc[last_deny_non_cat_bool, ["Approvable ID", "Action Date - AHR"]]
        .sort_values("Action Date - AHR")
        .groupby("Approvable ID")
        .tail(1)
        .rename(columns={"Action Date - AHR": "Latest Deny Date"})
    )
    data = data.merge(latest_deny_non_cat_table, how="left", on="Approvable ID")

    deny_non_cat_bool = [
        all(t)
        for t in zip(
            data["Denied?"].isin([True]),
            data["Non-Cat?"].isin([True]),
            data["Action Date - AHR"] > data["Latest Deny Date"],
        )
    ]
    deny_non_cat_table = (
        data.loc[deny_non_cat_bool, ["Assigned Date - AHR", "Approvable ID"]]
        .sort_values("Assigned Date - AHR")
        .groupby("Approvable ID")
        .head(1)
        .rename(columns={"Assigned Date - AHR": "New Assigned Date3"})
    )
    data = data.merge(deny_non_cat_table, how="left", on="Approvable ID")

    # Calc Final Submit Date
    data["Submit Date - Single"] = pd.NA
    data.loc[~data["New Assigned Date1"].isna(), "Submit Date - Single"] = data.loc[
        ~data["New Assigned Date1"].isna(), "New Assigned Date1"
    ]

    data.loc[~data["New Assigned Date2"].isna(), "Submit Date - Single"] = data.loc[
        ~data["New Assigned Date2"].isna(), "New Assigned Date2"
    ]

    data.loc[~data["New Assigned Date3"].isna(), "Submit Date - Single"] = data.loc[
        ~data["New Assigned Date3"].isna(), "New Assigned Date3"
    ]

    return data[["Approvable ID", "Submit Date - Single"]].drop_duplicates()


def calc_sub_date_mult_submission(data):
    # Handle Non-catalog, non-denied.
    # Assumption 2.17

    non_cat_non_deny_bool = [
        all(t)
        for t in zip(
            data["Non-Cat?"].isin([True]),
            data["Denied?"].isin([False]),
            data["Approver Reason - AHR"]
            == "Buyer needs to approve ALL Non-Catalog PRs",
        )
    ]
    non_cat_non_deny_table = (
        data.loc[non_cat_non_deny_bool, ["Approvable ID", "Assigned Date - AHR"]]
        .sort_values("Assigned Date - AHR")
        .groupby("Approvable ID")
        .tail(1)
        .rename(columns={"Assigned Date - AHR": "Assigned Date4"})
    )

    data = data.merge(non_cat_non_deny_table, how="left", on="Approvable ID")

    # Hard Validation 2.10
    val_2_10_handling = di.import_val_2_10_handling()

    for x in val_2_10_handling["Approvable ID"]:
        data.loc[data["Approvable ID"] == x, "Assigned Date4"] = val_2_10_handling.loc[
            val_2_10_handling["Approvable ID"] == x, "Fixed Submit Date"
        ].values[0]

    val_2_10_bool = [
        all(t)
        for t in zip(
            data["Non-Cat?"].isin([True]),
            data["Denied?"].isin([False]),
            data["Assigned Date4"].isna(),
        )
    ]
    if data.loc[val_2_10_bool].shape[0] > 0:
        data.loc[val_2_10_bool].to_csv("test2.10.csv")

    # Handle catalog, non-denied.
    # Assumption 2.18
    cat_non_deny_bool = [
        all(t)
        for t in zip(
            data["Non-Cat?"].isin([False]),
            data["Denied?"].isin([False]),
            data["Approver Reason - AHR"] == "Supervisor must approve",
        )
    ]
    cat_non_deny_table = (
        data.loc[cat_non_deny_bool, ["Approvable ID", "Assigned Date - AHR"]]
        .sort_values("Assigned Date - AHR")
        .groupby("Approvable ID")
        .tail(1)
        .rename(columns={"Assigned Date - AHR": "Assigned Date5"})
    )

    data = data.merge(cat_non_deny_table, how="left", on="Approvable ID")

    # Hard Validation 2.11
    val_2_11_bool = [
        all(t)
        for t in zip(
            data["Non-Cat?"].isin([False]),
            data["Denied?"].isin([False]),
            data["Assigned Date5"].isna(),
        )
    ]
    if data.loc[val_2_11_bool].shape[0] > 0:
        data.loc[val_2_11_bool].to_csv("test2.11.csv")

    # Handle Non-catalog, denied.
    # Assumption 2.19
    non_cat_deny_bool = [
        all(t)
        for t in zip(
            data["Non-Cat?"].isin([True]),
            data["Denied?"].isin([True]),
            data["Approver Reason - AHR"]
            == "Buyer needs to approve ALL Non-Catalog PRs",
        )
    ]
    non_cat_deny_table = (
        data.loc[non_cat_deny_bool, ["Approvable ID", "Assigned Date - AHR"]]
        .sort_values("Assigned Date - AHR")
        .groupby("Approvable ID")
        .tail(1)
        .rename(columns={"Assigned Date - AHR": "Assigned Date6"})
    )
    data = data.merge(non_cat_deny_table, how="left", on="Approvable ID")

    # Hard Validation 2.12
    val_2_12_bool = [
        all(t)
        for t in zip(
            data["Non-Cat?"].isin([True]),
            data["Denied?"].isin([True]),
            data["Assigned Date6"].isna(),
        )
    ]
    if data.loc[val_2_12_bool].shape[0] > 0:
        data.loc[val_2_12_bool].to_csv("test2.12.csv")

    # Handle catalog, denied.
    # Assumption 2.20
    cat_deny_bool = [
        all(t)
        for t in zip(
            data["Non-Cat?"].isin([False]),
            data["Denied?"].isin([True]),
            data["Approver Reason - AHR"] == "Supervisor must approve",
        )
    ]
    cat_deny_table = (
        data.loc[cat_deny_bool, ["Approvable ID", "Assigned Date - AHR"]]
        .sort_values("Assigned Date - AHR")
        .groupby("Approvable ID")
        .tail(1)
        .rename(columns={"Assigned Date - AHR": "Assigned Date7"})
    )
    data = data.merge(cat_deny_table, how="left", on="Approvable ID")

    # Hard Validation 2.13
    val_2_13_bool = [
        all(t)
        for t in zip(
            data["Non-Cat?"].isin([False]),
            data["Denied?"].isin([True]),
            data["Assigned Date7"].isna(),
        )
    ]
    if data.loc[val_2_13_bool].shape[0] > 0:
        data.loc[val_2_13_bool].to_csv("test2.13.csv")

    # Calc Submit Date - Multiple
    data["Submit Date - Multiple"] = pd.NA
    data.loc[~data["Assigned Date4"].isna(), "Submit Date - Multiple"] = data.loc[
        ~data["Assigned Date4"].isna(), "Assigned Date4"
    ]

    data.loc[~data["Assigned Date5"].isna(), "Submit Date - Multiple"] = data.loc[
        ~data["Assigned Date5"].isna(), "Assigned Date5"
    ]

    data.loc[~data["Assigned Date6"].isna(), "Submit Date - Multiple"] = data.loc[
        ~data["Assigned Date6"].isna(), "Assigned Date6"
    ]

    data.loc[~data["Assigned Date7"].isna(), "Submit Date - Multiple"] = data.loc[
        ~data["Assigned Date7"].isna(), "Assigned Date7"
    ]

    return data[["Approvable ID", "Submit Date - Multiple"]].drop_duplicates()


def calc_sub_date_blank_submission(data):
    # Contains a denial
    last_deny_table = data.loc[
        data["Approver State - AHR"] == "Denied", ["Approvable ID", "Action Date - AHR"]
    ].rename(columns={"Action Date - AHR": "Last Denial Date"})
    data = data.merge(last_deny_table, how="left", on="Approvable ID")

    deny_bool = [
        all(t)
        for t in zip(
            data["Denied?"].isin([True]),
            data["Action Date - AHR"] > data["Last Denial Date"],
        )
    ]
    deny_table = (
        data.loc[deny_bool, ["Assigned Date - AHR", "Approvable ID"]]
        .sort_values("Assigned Date - AHR")
        .groupby("Approvable ID")
        .head(1)
        .rename(columns={"Assigned Date - AHR": "New Assigned Date8"})
    )
    data = data.merge(deny_table, how="left", on="Approvable ID")

    # Doesn't contain a denial
    no_deny_bool = data["Denied?"].isin([False])
    no_deny_table = (
        data.loc[no_deny_bool, ["Assigned Date - AHR", "Approvable ID"]]
        .sort_values("Assigned Date - AHR")
        .groupby("Approvable ID")
        .head(1)
        .rename(columns={"Assigned Date - AHR": "New Assigned Date9"})
    )
    data = data.merge(no_deny_table, how="left", on="Approvable ID")

    # Calc Submit Date - Blank
    data["Submit Date - Blank"] = pd.NA
    data.loc[~data["New Assigned Date8"].isna(), "Submit Date - Blank"] = data.loc[
        ~data["New Assigned Date8"].isna(), "New Assigned Date8"
    ]

    data.loc[~data["New Assigned Date9"].isna(), "Submit Date - Blank"] = data.loc[
        ~data["New Assigned Date9"].isna(), "New Assigned Date9"
    ]

    return data[["Approvable ID", "Submit Date - Blank"]].drop_duplicates()


def populate_apr_sub_date(base_data):
    data = di.import_ahr_data()

    # Flag whether a PR was ever denied in the approval flow.
    data["Denied?"] = data["Approvable ID"].isin(
        data.loc[
            data["Approver State - AHR"] == "Denied", "Approvable ID"
        ].drop_duplicates()
    )

    # Calculate the number of times a PR was denied.
    denied_data_count = (
        data.loc[
            data["Approver State - AHR"] == "Denied",
            ["Approvable ID", "Assigned Date - AHR"],
        ]
        .groupby("Approvable ID")
        .count()
        .rename(columns={"Assigned Date - AHR": "# of Times Denied"})
    )
    data = data.merge(denied_data_count, how="left", on="Approvable ID")

    # Shrink down the list of relevant entries.
    relevant_data = data.merge(
        kpi2_master_pr_list[["PR #", "Final Relevant?"]].drop_duplicates(),
        how="left",
        left_on="Approvable ID",
        right_on="PR #",
    )
    relevant_data = relevant_data.loc[relevant_data["Final Relevant?"].isin([True])]

    # Flag which ones had to contain non-catalog items.
    non_catalog_reasons = [
        "Supervisor Must Approve - Non Catalog",
        "Buyer needs to approve ALL Non-Catalog PRs",
        "Cost Center Owner must approve-Non Catalog",
        "Error in processing business rule: ariba.approvable.rules.JavaScriptTemplateSimpleRule - "
        "Non-Catalog Buyer Approval Flow AddGroup.",
    ]

    relevant_data["Non-Cat?"] = relevant_data["Approvable ID"].isin(
        relevant_data.loc[
            relevant_data["Approver Reason - AHR"].isin(non_catalog_reasons),
            "Approvable ID",
        ].drop_duplicates()
    )

    # For catalog entries, figure out how many submissions performed.
    catalog_reasons = ["Supervisor must approve", "Cost Center Owner must approve"]
    num_cat_sub_bool = [
        all(t)
        for t in zip(
            relevant_data["Non-Cat?"].isin([False]),
            relevant_data["Approver Reason - AHR"].isin(catalog_reasons),
        )
    ]
    num_sub_cat_table = pd.pivot_table(
        relevant_data.loc[
            num_cat_sub_bool,
            ["Approvable ID", "Approver Reason - AHR", "Approver State - AHR"],
        ],
        index="Approvable ID",
        columns="Approver Reason - AHR",
        aggfunc="count",
    )
    num_sub_cat_table.columns.names = ["C1", "Approver Reason - AHR"]
    num_sub_cat_table = num_sub_cat_table.droplevel("C1", axis=1)

    # For non-catalog entries, figure out how many submissions performed.
    num_non_cat_sub_bool = [
        all(t)
        for t in zip(
            relevant_data["Non-Cat?"].isin([True]),
            relevant_data["Approver Reason - AHR"].isin(non_catalog_reasons),
        )
    ]
    num_sub_non_cat_table = pd.pivot_table(
        relevant_data.loc[
            num_non_cat_sub_bool,
            ["Approvable ID", "Approver Reason - AHR", "Approver State - AHR"],
        ],
        index="Approvable ID",
        columns="Approver Reason - AHR",
        aggfunc="count",
    )
    num_sub_non_cat_table.columns.names = ["C1", "Approver Reason - AHR"]
    num_sub_non_cat_table = num_sub_non_cat_table.droplevel("C1", axis=1)

    # Calc final number of submissions.
    num_sub_table = pd.concat([num_sub_non_cat_table, num_sub_cat_table])
    num_sub_table["Final # of Submissions"] = num_sub_table.max(axis=1)

    relevant_data = relevant_data.merge(
        num_sub_table["Final # of Submissions"],
        how="left",
        left_on="Approvable ID",
        right_index=True,
    )

    # Calc sub date for entries with single submissions.
    relevant_data = relevant_data.merge(
        calc_sub_date_single_submission(
            relevant_data.loc[relevant_data["Final # of Submissions"] == 1]
        ),
        how="left",
        on="Approvable ID",
    )

    # Calc sub date for entries with mult submissions.
    relevant_data = relevant_data.merge(
        calc_sub_date_mult_submission(
            relevant_data.loc[relevant_data["Final # of Submissions"] > 1]
        ),
        how="left",
        on="Approvable ID",
    )

    # Calc sub date for entries with no calculated submissions.
    relevant_data = relevant_data.merge(
        calc_sub_date_blank_submission(
            relevant_data.loc[relevant_data["Final # of Submissions"].isna()]
        ),
        how="left",
        on="Approvable ID",
    )

    # Calc Final Sub Date
    relevant_data["Final Submit Date"] = pd.NA

    relevant_data.loc[
        ~relevant_data["Submit Date - Single"].isna(), "Final Submit Date"
    ] = relevant_data.loc[
        ~relevant_data["Submit Date - Single"].isna(), "Submit Date - Single"
    ]

    relevant_data.loc[
        ~relevant_data["Submit Date - Multiple"].isna(), "Final Submit Date"
    ] = relevant_data.loc[
        ~relevant_data["Submit Date - Multiple"].isna(), "Submit Date - Multiple"
    ]

    relevant_data.loc[
        ~relevant_data["Submit Date - Blank"].isna(), "Final Submit Date"
    ] = relevant_data.loc[
        ~relevant_data["Submit Date - Blank"].isna(), "Submit Date - Blank"
    ]

    # Merge results back into master pr list.
    base_data = base_data.merge(
        relevant_data[["Approvable ID", "Final Submit Date"]].drop_duplicates(),
        how="left",
        left_on="PR #",
        right_on="Approvable ID",
    ).drop("Approvable ID", axis=1)

    # Assumption 2.21
    base_data.loc[base_data["Final Submit Date"].isna(), "Final Relevant?"] = False

    return base_data


kpi2_master_pr_list = populate_apr_sub_date(kpi2_master_pr_list)


def populate_final_approved_date(data):
    raw_data = di.import_ahr_data()

    last_app_table = (
        raw_data.loc[
            raw_data["Approver State - AHR"] == "Approved",
            ["Approvable ID", "Action Date - AHR"],
        ]
        .sort_values("Action Date - AHR", ascending=False)
        .groupby("Approvable ID")
        .head(1)
        .rename(columns={"Action Date - AHR": "Final Approved Date"})
    )

    # Assumption 2.22
    data = data.merge(
        last_app_table, how="left", left_on="PR #", right_on="Approvable ID"
    ).drop("Approvable ID", axis=1)

    assume_2_22_bool = [
        all(t)
        for t in zip(
            data["Final Approved Date"].isna(), data["Final Relevant?"].isin([True])
        )
    ]
    data.loc[assume_2_22_bool, "Final Relevant?"] = False

    return data


kpi2_master_pr_list = populate_final_approved_date(kpi2_master_pr_list)


# As of 2/23/23 - 1139 entries company code unclassified.
def determine_final_company_code(data):
    data = data.merge(
        raw_pr_data[["PR #", "Purchasing Unit - PR"]].drop_duplicates(),
        how="left",
        on="PR #",
    )

    pop_codes_data = data.loc[
        ~data["Purchasing Unit - PR"].isna(), ["PR #", "Purchasing Unit - PR"]
    ]
    pop_codes_data["Original Ver"] = pop_codes_data["PR #"].replace(
        "-[^-]*$", "", regex=True
    )
    pop_codes_data = pop_codes_data.drop("PR #", axis=1).drop_duplicates()
    pop_codes_data = pop_codes_data.rename(
        columns={"Purchasing Unit - PR": "Final Company Code"}
    )

    data["Original Ver"] = data["PR #"].replace("-[^-]*$", "", regex=True)

    data = data.merge(pop_codes_data, how="left", on="Original Ver")

    data = data.drop(["Original Ver", "Purchasing Unit - PR"], axis=1)

    return data


kpi2_master_pr_list = determine_final_company_code(kpi2_master_pr_list)


def determine_pr_turnaround_time(data):
    data["Final Approved Date"] = pd.to_datetime(
        data["Final Approved Date"].dt.date, format="%Y-%m-%d"
    )
    data["Final Submit Date"] = pd.to_datetime(
        data["Final Submit Date"], format="%Y-%m-%d"
    )

    data["Turnaround (Days)"] = data["Final Approved Date"] - data["Final Submit Date"]
    data["Turnaround (Days)"] = data["Turnaround (Days)"].dt.days

    # Hard Validation 2.14
    val_2_14_bool = [
        all(t)
        for t in zip(
            data["Turnaround (Days)"].isna(), data["Final Relevant?"].isin([True])
        )
    ]
    if data.loc[val_2_14_bool].shape[0] > 0:
        data.loc[val_2_14_bool].to_csv("test2.14.csv")

    # Hard Validation 2.15
    val_2_15_handling = di.import_val_2_15_handling()

    for item, value in val_2_15_handling.iterrows():
        relevant_row = data["PR #"] == value["PR #"]
        data.loc[relevant_row, "Final Relevant?"] = value["Updated Relevant?"]

    val_2_15_bool = [
        all(t) for t in zip(data["Turnaround (Days)"] < 0, data["Final Relevant?"])
    ]
    if data.loc[val_2_15_bool].shape[0] > 0:
        data.loc[val_2_15_bool].to_csv("test2.15.csv")

    return data


kpi2_master_pr_list = determine_pr_turnaround_time(kpi2_master_pr_list)


""" KPI #3 - Invoice 1st Time Match Rate"""

""" Ariba Match Rate"""
raw_ah_inv = di.import_ah_inv_data()
raw_ah_pre = di.import_ah_pre_data()
raw_app_inv = di.import_app_inv_data()
raw_app_pre = di.import_app_pre_data()
raw_inv_exc = di.import_inv_exc_data()
raw_inv_pay = di.import_inv_pay_data()
raw_inv_pro = di.import_inv_pro_data()
raw_prerec_inv = di.import_prerec_inv_data()
raw_reject_inv = di.import_rejected_inv_data()


def kpi3_create_ariba_master_inv_data():
    data = pd.concat(
        [
            raw_ah_inv["Approvable ID"],
            raw_ah_pre["Approvable ID"],
            raw_app_inv["Approvable ID"],
            raw_app_pre["Approvable ID"],
            raw_inv_exc["Invoice ID"],
            raw_inv_pay["Invoice ID"],
            raw_inv_pro["Invoice ID"],
            raw_prerec_inv["Invoice ID"],
            raw_reject_inv["Invoice ID"],
        ]
    ).drop_duplicates()

    data = pd.DataFrame(data, columns=["Invoice #"])

    return data


kpi3_master_ariba_inv_list = kpi3_create_ariba_master_inv_data()


def kpi3_add_supplier_number_ariba_inv(data):
    relevant_data = pd.concat(
        [
            raw_prerec_inv[["Invoice ID", "Supplier # - PREREC"]].rename(
                columns={"Supplier # - PREREC": "Supplier #"}
            ),
            raw_inv_pro[["Invoice ID", "Supplier # - INVPRO"]].rename(
                columns={"Supplier # - INVPRO": "Supplier #"}
            ),
        ]
    ).drop_duplicates()

    data = data.merge(
        relevant_data, how="left", left_on="Invoice #", right_on="Invoice ID"
    )
    data = data.drop("Invoice ID", axis=1)

    return data


kpi3_master_ariba_inv_list = kpi3_add_supplier_number_ariba_inv(
    kpi3_master_ariba_inv_list
)


def kpi3_determine_inv_source(data):
    data["In AH - INV?"] = data["Invoice #"].isin(raw_ah_inv["Approvable ID"])
    data["In AH - PRE?"] = data["Invoice #"].isin(raw_ah_pre["Approvable ID"])
    data["In APP - INV?"] = data["Invoice #"].isin(raw_app_inv["Approvable ID"])
    data["In APP - PRE?"] = data["Invoice #"].isin(raw_app_pre["Approvable ID"])
    data["In INV - EXC?"] = data["Invoice #"].isin(raw_inv_exc["Invoice ID"])
    data["In INV - PAY?"] = data["Invoice #"].isin(raw_inv_pay["Invoice ID"])
    data["In INV - PRO?"] = data["Invoice #"].isin(raw_inv_pro["Invoice ID"])
    data["In PREREC - INV?"] = data["Invoice #"].isin(raw_prerec_inv["Invoice ID"])
    data["In Rej - INV?"] = data["Invoice #"].isin(raw_reject_inv["Invoice ID"])

    return data


kpi3_master_ariba_inv_list = kpi3_determine_inv_source(kpi3_master_ariba_inv_list)


def kpi3_add_invoice_source(data):
    # Pull in Source Document from Prereconciled file
    data = (
        data.merge(
            raw_prerec_inv[["Invoice ID", "Invoice Source - PREREC"]],
            how="left",
            left_on="Invoice #",
            right_on="Invoice ID",
        )
        .drop("Invoice ID", axis=1)
        .drop_duplicates()
    )

    # Pull in Source Document from Inv Pay
    data = (
        data.merge(
            raw_inv_pay[["Invoice ID", "Invoice Source - INVPAY"]],
            how="left",
            left_on="Invoice #",
            right_on="Invoice ID",
        )
        .drop("Invoice ID", axis=1)
        .drop_duplicates()
    )

    # Fill in Source Doc gaps
    data["Final Source Doc"] = pd.NA

    data["Final Source Doc"] = data["Invoice Source - PREREC"]

    data.loc[data["Final Source Doc"].isna(), "Final Source Doc"] = data.loc[
        data["Final Source Doc"].isna(), "Invoice Source - INVPAY"
    ]

    # Hard Validation 3.1
    val_3_1_handling = di.import_val_3_1_handling()

    data = data.merge(val_3_1_handling, how="left", on="Invoice #")
    data.loc[~data["Fixed Invoice Source"].isna(), "Final Source Doc"] = data.loc[
        ~data["Fixed Invoice Source"].isna(), "Fixed Invoice Source"
    ]
    data.drop("Fixed Invoice Source", axis=1)

    val_3_1_bool = [
        all(t)
        for t in zip(data["Final Relevant?"].isna(), data["Final Source Doc"].isna())
    ]
    if data.loc[val_3_1_bool].shape[0] > 0:
        data.loc[val_3_1_bool].to_csv("test3.1.csv")

    # Hard Validation 3.11
    val_3_11_table = (
        data[["Invoice #", "Supplier #", "Final Source Doc"]]
        .groupby(["Invoice #", "Supplier #"])
        .nunique("Final Source Doc")
    )
    if (val_3_11_table.loc[:, "Final Source Doc"] > 1).any():
        val_3_11_table.to_csv("test3.11.csv")

    return data


def kpi3_determine_inv_relevant(data):
    data["Final Relevant?"] = pd.NA

    # Assumption 3.1
    assume_3_1_bool = [
        all(t)
        for t in zip(
            data["In AH - PRE?"].isin([True]),
            data["In AH - INV?"].isin([False]),
            data["In APP - INV?"].isin([False]),
            data["In APP - PRE?"].isin([False]),
            data["In INV - EXC?"].isin([False]),
            data["In INV - PAY?"].isin([False]),
            data["In INV - PRO?"].isin([False]),
            data["In PREREC - INV?"].isin([False]),
            data["Final Relevant?"].isna(),
        )
    ]
    data.loc[assume_3_1_bool, "Final Relevant?"] = False

    # Assumption 3.2
    assume_3_2_bool = [
        all(t)
        for t in zip(
            data["In AH - PRE?"].isin([True]),
            data["In APP - PRE?"].isin([True]),
            data["In AH - INV?"].isin([False]),
            data["In APP - INV?"].isin([False]),
            data["In INV - EXC?"].isin([False]),
            data["In INV - PAY?"].isin([False]),
            data["In INV - PRO?"].isin([False]),
            data["In PREREC - INV?"].isin([False]),
            data["Final Relevant?"].isna(),
        )
    ]
    data.loc[assume_3_2_bool, "Final Relevant?"] = False

    # Assumption 3.3
    assume_3_3_bool = [
        all(t)
        for t in zip(
            data["In APP - PRE?"].isin([True]),
            data["In AH - INV?"].isin([False]),
            data["In AH - PRE?"].isin([False]),
            data["In APP - INV?"].isin([False]),
            data["In INV - EXC?"].isin([False]),
            data["In INV - PAY?"].isin([False]),
            data["In INV - PRO?"].isin([False]),
            data["In PREREC - INV?"].isin([False]),
            data["Final Relevant?"].isna(),
        )
    ]
    data.loc[assume_3_3_bool, "Final Relevant?"] = False

    data = kpi3_add_invoice_source(data)

    # Assumption 3.4
    irrelevant_inv_types = ["Sales Order", "Non-PO", "Contract", "Blanket PO"]
    data.loc[
        data["Final Source Doc"].isin(irrelevant_inv_types), "Final Relevant?"
    ] = False

    relevant_inv_types = ["Purchase Order"]
    data.loc[
        data["Final Source Doc"].isin(relevant_inv_types), "Final Relevant?"
    ] = True

    # Assumption 3.5
    assume_3_5_bool = [
        all(t)
        for t in zip(
            data["Invoice Source - PREREC"] == "Purchase Order",
            data["Invoice #"].isin(
                raw_prerec_inv.loc[
                    ~raw_prerec_inv["Contract ID - PREREC"].isna(),
                    "Invoice ID",
                ]
            ),
        )
    ]
    data.loc[assume_3_5_bool, "Final Relevant?"] = False

    # Hard Validation 3.2
    val_3_2_bool = data["Final Relevant?"].isna()
    if data.loc[val_3_2_bool].shape[0] > 0:
        data.loc[val_3_2_bool].to_csv("test3.2.csv")

    return data


kpi3_master_ariba_inv_list = kpi3_determine_inv_relevant(kpi3_master_ariba_inv_list)


def kpi3_determine_inv_type_prerec(data):
    data["Inv Type - PREREC"] = pd.NA

    indirect_entries_bool = [
        all(t)
        for t in zip(
            data["Invoice Source - PREREC"].isin(
                ["Non-PO", "Sales Order", "Blanket PO", "Contract"]
            )
        )
    ]
    data.loc[indirect_entries_bool, "Inv Type - PREREC"] = "Indirect"

    indirect_po_entries_bool = [
        all(t)
        for t in zip(
            data["Invoice Source - PREREC"] == "Purchase Order",
            data["PO Id"].str.contains("^EP", regex=True),
        )
    ]
    data.loc[indirect_po_entries_bool, "Inv Type - PREREC"] = "Indirect"

    direct_po_entries_bool = [
        all(t)
        for t in zip(
            data["Invoice Source - PREREC"] == "Purchase Order",
            data["PO Id"].str.contains("^CC", regex=True),
        )
    ]
    data.loc[direct_po_entries_bool, "Inv Type - PREREC"] = "Direct"

    # Okay to remove unclassified PO entries, because they're already classified.
    po_unclassified_bool = np.array(
        [
            all(t)
            for t in zip(
                data["Invoice Source - PREREC"] == "Purchase Order",
                data["PO Id"] == "Unclassified",
            )
        ],
        dtype=bool,
    )

    data = data.loc[np.logical_not(po_unclassified_bool)]

    # Hard Validation 3.3
    val_3_3_handling = di.import_val_3_3_handling()

    for x in val_3_3_handling.index:
        entry = val_3_3_handling.loc[0, "Invoice ID"]
        value = val_3_3_handling.loc[0, "Direct/Indirect?"]

        data.loc[data["Invoice ID"].isin([entry]), "Inv Type - PREREC"] = value

    val_3_3_table = (
        data[["Invoice ID", "Inv Type - PREREC"]].groupby("Invoice ID").nunique() > 1
    )
    if val_3_3_table["Inv Type - PREREC"].any():
        val_3_3_table.loc[val_3_3_table["Inv Type - PREREC"]].to_csv("test3.3.csv")

    return data


raw_prerec_inv = kpi3_determine_inv_type_prerec(raw_prerec_inv)


def kpi3_determine_inv_type_invpay(data):
    data["Inv Type - INVPAY"] = pd.NA

    indirect_entries_bool = [
        all(t)
        for t in zip(
            data["Invoice Source - INVPAY"].isin(
                ["Non-PO", "Sales Order", "Blanket PO", "Contract"]
            )
        )
    ]
    data.loc[indirect_entries_bool, "Inv Type - INVPAY"] = "Indirect"

    indirect_po_entries_bool = [
        all(t)
        for t in zip(
            data["Invoice Source - INVPAY"] == "Purchase Order",
            data["PO Id"].str.contains("^EP", regex=True),
        )
    ]
    data.loc[indirect_po_entries_bool, "Inv Type - INVPAY"] = "Indirect"

    direct_po_entries_bool = [
        all(t)
        for t in zip(
            data["Invoice Source - INVPAY"] == "Purchase Order",
            data["PO Id"].str.contains("^CC", regex=True),
        )
    ]
    data.loc[direct_po_entries_bool, "Inv Type - INVPAY"] = "Direct"

    # Okay to remove unclassified PO entries, because they're already classified.
    po_unclassified_bool = np.array(
        [
            all(t)
            for t in zip(
                data["Invoice Source - INVPAY"] == "Purchase Order",
                data["PO Id"] == "Unclassified",
            )
        ],
        dtype=bool,
    )

    data = data.loc[np.logical_not(po_unclassified_bool)]

    # Hard Validation 3.4
    val_3_4_handling = di.import_val_3_4_handling()

    for x in val_3_4_handling.index:
        entry = val_3_4_handling.loc[x, "Invoice ID"]
        value = val_3_4_handling.loc[x, "Direct/Indirect?"]

        data.loc[data["Invoice ID"].isin([entry]), "Inv Type - INVPAY"] = value

    val_3_4_table = (
        data[["Invoice ID", "Inv Type - INVPAY"]].groupby("Invoice ID").nunique() > 1
    )
    if val_3_4_table["Inv Type - INVPAY"].any():
        val_3_4_table.loc[val_3_4_table["Inv Type - INVPAY"]].to_csv("test3.4.csv")

    return data


raw_inv_pay = kpi3_determine_inv_type_invpay(raw_inv_pay)


def kpi3_determine_inv_direct_indirect(data):
    data = data.merge(
        raw_prerec_inv[
            ["Invoice ID", "Inv Type - PREREC", "Contract ID - PREREC", "PO Id"]
        ].drop_duplicates(),
        how="left",
        left_on="Invoice #",
        right_on="Invoice ID",
    ).drop("Invoice ID", axis=1)

    data = data.merge(
        raw_inv_pay[["Invoice ID", "Inv Type - INVPAY"]].drop_duplicates(),
        how="left",
        left_on="Invoice #",
        right_on="Invoice ID",
    ).drop("Invoice ID", axis=1)

    data["Final Inv Type"] = pd.NA

    data.loc[~data["Inv Type - PREREC"].isna(), "Final Inv Type"] = data.loc[
        ~data["Inv Type - PREREC"].isna(), "Inv Type - PREREC"
    ]
    data.loc[data["Final Inv Type"].isna(), "Final Inv Type"] = data.loc[
        data["Final Inv Type"].isna(), "Inv Type - INVPAY"
    ]

    # Assumption 3.6
    assume_3_6_bool = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isin([True]),
            data["Invoice Source - PREREC"] == "Purchase Order",
            data["Contract ID - PREREC"].isna(),
            data["PO Id"].isna(),
        )
    ]
    data.loc[assume_3_6_bool, "Final Relevant?"] = False

    # Hard Validation 3.5
    val_3_5_bool = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isin([True]), data["Final Inv Type"].isna()
        )
    ]
    if data.loc[val_3_5_bool].shape[0] > 0:
        data.loc[val_3_5_bool].to_csv("test3.5.csv")

    return data


kpi3_master_ariba_inv_list = kpi3_determine_inv_direct_indirect(
    kpi3_master_ariba_inv_list
)


def kpi3_determine_ariba_match_rate(data):
    data["1st Match?"] = pd.NA

    data.loc[data["Final Relevant?"].isin([False]), "1st Match?"] = "N/A"

    # Assumption 3.7
    assume_3_7_bool = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isin([True]),
            data["In Rej - INV?"].isin([True]),
            data["1st Match?"].isna(),
        )
    ]
    data.loc[assume_3_7_bool, "1st Match?"] = False

    # Assumption 3.8
    assume_3_8_bool = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isin([True]),
            data["1st Match?"].isna(),
            data["In INV - EXC?"].isin([False]),
            data["In AH - INV?"].isin([True]),
        )
    ]
    data.loc[assume_3_8_bool, "1st Match?"] = False

    # Assumption 3.9
    assume_3_9_bool = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isin([True]),
            data["1st Match?"].isna(),
            data["In INV - EXC?"].isin([False]),
            data["In AH - PRE?"].isin([True]),
        )
    ]
    data.loc[assume_3_9_bool, "1st Match?"] = False

    # Assumption 3.10
    assume_3_10_bool = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isin([True]),
            data["1st Match?"].isna(),
            data["In INV - EXC?"].isin([False]),
            data["In APP - INV?"].isin([True]),
        )
    ]
    data.loc[assume_3_10_bool, "1st Match?"] = False

    # Assumption 3.11
    assume_3_11_bool = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isin([True]),
            data["1st Match?"].isna(),
            data["In INV - EXC?"].isin([False]),
            data["In APP - PRE?"].isin([True]),
        )
    ]
    data.loc[assume_3_11_bool, "1st Match?"] = False

    # Assumption 3.12
    assume_3_12_bool = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isin([True]),
            data["1st Match?"].isna(),
            data["In INV - EXC?"].isin([False]),
            data["In AH - INV?"].isin([False]),
            data["In AH - PRE?"].isin([False]),
            data["In APP - INV?"].isin([False]),
            data["In APP - PRE?"].isin([False]),
            data["In INV - PAY?"].isin([False]),
            data["In INV - PRO?"].isin([False]),
            data["In PREREC - INV?"].isin([True]),
            data["In Rej - INV?"].isin([False]),
        )
    ]
    data.loc[assume_3_12_bool, "1st Match?"] = False

    # Assumption 3.13
    assume_3_13_bool = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isin([True]),
            data["1st Match?"].isna(),
            data["In INV - EXC?"].isin([False]),
            data["In AH - INV?"].isin([False]),
            data["In AH - PRE?"].isin([False]),
            data["In APP - INV?"].isin([False]),
            data["In APP - PRE?"].isin([False]),
            data["In INV - PAY?"].isin([True]),
            data["In INV - PRO?"].isin([False]),
            data["In PREREC - INV?"].isin([True]),
            data["In Rej - INV?"].isin([False]),
        )
    ]
    data.loc[assume_3_13_bool, "1st Match?"] = False

    # Assumption 3.14
    assume_3_14_bool = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isin([True]),
            data["1st Match?"].isna(),
            data["In INV - EXC?"].isin([True]),
        )
    ]
    data.loc[assume_3_14_bool, "1st Match?"] = False

    # Assumption 3.15
    assume_3_15_bool = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isin([True]),
            data["1st Match?"].isna(),
            data["In INV - EXC?"].isin([False]),
            data["In AH - INV?"].isin([False]),
            data["In AH - PRE?"].isin([False]),
            data["In APP - INV?"].isin([False]),
            data["In APP - PRE?"].isin([False]),
            data["In INV - PAY?"].isin([True]),
            data["In INV - PRO?"].isin([True]),
            data["In PREREC - INV?"].isin([False]),
            data["In Rej - INV?"].isin([False]),
        )
    ]
    data.loc[assume_3_15_bool, "1st Match?"] = True

    # Assumption 3.16
    assume_3_16_bool = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isin([True]),
            data["1st Match?"].isna(),
            data["In INV - EXC?"].isin([False]),
            data["In AH - INV?"].isin([False]),
            data["In AH - PRE?"].isin([False]),
            data["In APP - INV?"].isin([False]),
            data["In APP - PRE?"].isin([False]),
            data["In INV - PAY?"].isin([True]),
            data["In INV - PRO?"].isin([True]),
            data["In PREREC - INV?"].isin([True]),
            data["In Rej - INV?"].isin([False]),
        )
    ]
    data.loc[assume_3_16_bool, "1st Match?"] = True

    # Assumption 3.17
    assume_3_17_bool = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isin([True]),
            data["1st Match?"].isna(),
            data["In INV - EXC?"].isin([False]),
            data["In AH - INV?"].isin([False]),
            data["In AH - PRE?"].isin([False]),
            data["In APP - INV?"].isin([False]),
            data["In APP - PRE?"].isin([False]),
            data["In INV - PAY?"].isin([False]),
            data["In INV - PRO?"].isin([True]),
            data["In PREREC - INV?"].isin([True]),
            data["In Rej - INV?"].isin([False]),
        )
    ]
    data.loc[assume_3_17_bool, "1st Match?"] = True

    # Hard Validation 3.6
    val_3_6_bool = [
        all(t)
        for t in zip(data["Final Relevant?"].isin([True]), data["1st Match?"].isna())
    ]
    if data.loc[val_3_6_bool].shape[0] > 0:
        data.loc[val_3_6_bool].to_csv("test3.6.csv")

    return data


kpi3_master_ariba_inv_list = kpi3_determine_ariba_match_rate(kpi3_master_ariba_inv_list)


def kpi3_determine_ariba_supplier(data):
    data = data.merge(
        raw_prerec_inv[["Invoice ID", "Supplier - PREREC"]].drop_duplicates(),
        how="left",
        left_on="Invoice #",
        right_on="Invoice ID",
    ).drop("Invoice ID", axis=1)

    data = data.merge(
        raw_inv_pro[["Invoice ID", "Supplier - INVPRO"]].drop_duplicates(),
        how="left",
        left_on="Invoice #",
        right_on="Invoice ID",
    ).drop("Invoice ID", axis=1)

    data["Supplier Name"] = pd.NA

    data["Supplier Name"] = data["Supplier - PREREC"].copy()

    data.loc[data["Supplier Name"].isna(), "Supplier Name"] = data.loc[
        data["Supplier Name"].isna(), "Supplier - INVPRO"
    ]

    # Hard Validation 3.7
    val_3_7_handling = di.import_val_3_7_handling()

    data = data.merge(val_3_7_handling, how="left", on="Invoice #")

    data.loc[~data["Fixed Supplier #"].isna(), "Supplier #"] = data.loc[
        ~data["Fixed Supplier #"].isna(), "Fixed Supplier #"
    ]

    data.loc[~data["Fixed Supplier Name"].isna(), "Supplier Name"] = data.loc[
        ~data["Fixed Supplier Name"].isna(), "Fixed Supplier Name"
    ]

    data = data.drop(["Fixed Supplier Name", "Fixed Supplier #"], axis=1)

    val_3_7_bool = [
        all(t)
        for t in zip(
            data["Supplier Name"].isin([pd.NA, "Unclassified"]),
            data["Final Relevant?"].isin([True]),
        )
    ]
    if data.loc[val_3_7_bool].shape[0] > 0:
        data.loc[val_3_7_bool].to_csv("test3.7.csv")

    return data


kpi3_master_ariba_inv_list = kpi3_determine_ariba_supplier(kpi3_master_ariba_inv_list)


def kpi3_determine_ariba_submission_method(data):
    data = data.merge(
        raw_prerec_inv[["Invoice ID", "Inv Submission - PREREC"]].drop_duplicates(),
        how="left",
        left_on="Invoice #",
        right_on="Invoice ID",
    ).drop("Invoice ID", axis=1)

    val_3_8_handling = di.import_val_3_8_handling()
    for x in val_3_8_handling["Supplier Name"]:
        val_3_8_bool = [
            all(t)
            for t in zip(
                data["Inv Submission - PREREC"].isna(), data["Supplier Name"] == x
            )
        ]
        data.loc[val_3_8_bool, "Inv Submission - PREREC"] = val_3_8_handling.loc[
            val_3_8_handling["Supplier Name"] == x, "Fixed Submission Method"
        ].values[0]

    # Hard Validation 3.8
    val_3_8_bool = [
        all(t)
        for t in zip(
            data["Final Relevant?"].isin([True]), data["Inv Submission - PREREC"].isna()
        )
    ]
    if data.loc[val_3_8_bool].shape[0] > 0:
        data.loc[val_3_8_bool].to_csv("test3.8.csv")

    return data


kpi3_master_ariba_inv_list = kpi3_determine_ariba_submission_method(
    kpi3_master_ariba_inv_list
)


def kpi3_determine_company_code_ariba_inv(data):
    data = data.merge(
        raw_prerec_inv[
            [
                "Invoice ID",
                "Company Code",
                "Company Code - PC",
                "Purchasing - PO ID",
                "Purchasing - PU",
            ]
        ].drop_duplicates(),
        how="left",
        left_on="Invoice #",
        right_on="Invoice ID",
    ).drop("Invoice ID", axis=1)
    data = data.merge(
        raw_inv_pro[["Invoice ID", "Company Code - INVPRO"]],
        how="left",
        left_on="Invoice #",
        right_on="Invoice ID",
    ).drop("Invoice ID", axis=1)

    data["Final Company Code"] = pd.NA

    all_same_bool = [
        all(t)
        for t in zip(
            data["Final Company Code"].isna(),
            ~data["Company Code"].isna(),
            data["Company Code"] == data["Company Code - PC"],
            data["Company Code"] == data["Purchasing - PO ID"],
            data["Company Code"] == data["Purchasing - PU"],
        )
    ]
    data.loc[all_same_bool, "Final Company Code"] = data.loc[
        all_same_bool, "Company Code"
    ]

    # Assumption 3.18
    assume_3_18_bool = [
        all(t)
        for t in zip(
            data["Final Company Code"].isna(),
            ~data["Company Code"].isna(),
            data["Company Code"] == data["Company Code - PC"],
            data["Company Code"] != data["Purchasing - PO ID"],
            data["Company Code"] == data["Purchasing - PU"],
        )
    ]
    data.loc[assume_3_18_bool, "Final Company Code"] = data.loc[
        assume_3_18_bool, "Company Code"
    ]

    # Assumption 3.19
    assume_3_19_bool = [
        all(t)
        for t in zip(
            data["Final Company Code"].isna(),
            ~data["Company Code"].isna(),
            data["Purchasing - PO ID"].isna(),
            data["Company Code - PC"].isna(),
            data["Company Code"] == data["Purchasing - PU"],
        )
    ]
    data.loc[assume_3_19_bool, "Final Company Code"] = data.loc[
        assume_3_19_bool, "Company Code"
    ]

    # Assumption 3.20
    assume_3_20_bool = [
        all(t)
        for t in zip(
            data["Final Company Code"].isna(),
            ~data["Company Code"].isna(),
            data["Purchasing - PO ID"].isna(),
            data["Company Code - PC"].isna(),
            data["Purchasing - PU"].isna(),
        )
    ]
    data.loc[assume_3_20_bool, "Final Company Code"] = data.loc[
        assume_3_20_bool, "Company Code"
    ]

    # Assumption 3.21
    assume_3_21_bool = [
        all(t)
        for t in zip(
            data["Final Company Code"].isna(),
            ~data["Company Code"].isna(),
            ~data["Purchasing - PO ID"].isna(),
            ~data["Company Code - PC"].isna(),
            ~data["Purchasing - PU"].isna(),
            data["Company Code"] == data["Purchasing - PU"],
            data["Company Code - PC"] == data["Purchasing - PO ID"],
            data["Company Code"] != data["Company Code - PC"],
        )
    ]
    data.loc[assume_3_21_bool, "Final Company Code"] = data.loc[
        assume_3_21_bool, "Company Code"
    ]

    # Assumption 3.31
    assume_3_31_bool = [
        all(t)
        for t in zip(
            data["Final Company Code"].isna(),
            data["Company Code"].isna(),
            ~data["Purchasing - PO ID"].isna(),
            ~data["Company Code - PC"].isna(),
            ~data["Purchasing - PU"].isna(),
            data["Company Code - PC"] == data["Purchasing - PO ID"],
            data["Company Code - PC"] == data["Purchasing - PU"],
        )
    ]
    data.loc[assume_3_31_bool, "Final Company Code"] = data.loc[
        assume_3_31_bool, "Company Code - PC"
    ]

    # Assumption 3.32
    assume_3_32_bool = [
        all(t)
        for t in zip(
            data["Final Company Code"].isna(),
            data["Company Code"].isna(),
            data["Purchasing - PO ID"].isna(),
            data["Company Code - PC"].isna(),
            ~data["Purchasing - PU"].isna(),
        )
    ]
    data.loc[assume_3_32_bool, "Final Company Code"] = data.loc[
        assume_3_32_bool, "Purchasing - PU"
    ]

    # Assumption 3.33
    assume_3_33_bool = ~data["Company Code - INVPRO"].isna()
    data.loc[assume_3_33_bool, "Final Company Code"] = data.loc[
        assume_3_33_bool, "Company Code - INVPRO"
    ]

    # Assumption 3.42
    assume_3_42_bool = [
        all(t)
        for t in zip(
            data["Company Code"].isna(),
            data["Final Company Code"].isna(),
            data["Company Code - INVPRO"].isna(),
            ~data["Company Code - PC"].isna(),
            ~data["Purchasing - PO ID"].isna(),
            ~data["Purchasing - PU"].isna(),
            data["Company Code - PC"] == data["Purchasing - PO ID"],
            data["Company Code - PC"] != data["Purchasing - PU"],
        )
    ]
    data.loc[assume_3_42_bool, "Final Company Code"] = data.loc[
        assume_3_42_bool, "Company Code - PC"
    ]

    # Hard Validation 3.10
    val_3_10_handling = di.import_val_3_10_handling()

    data = data.merge(val_3_10_handling, how="left", on="Invoice #")
    data.loc[data["Final Company Code"].isna(), "Final Company Code"] = data.loc[
        data["Final Company Code"].isna(), "Adjusted Company Code"
    ]

    data = data.drop(["Adjusted Company Code"], axis=1)

    val_3_10_bool = [
        all(t)
        for t in zip(
            data["Final Company Code"].isna(), data["Final Relevant?"].isin([True])
        )
    ]

    if data.loc[val_3_10_bool].shape[0] > 0:
        data.loc[val_3_10_bool].to_csv("test3.10.csv")

    return data


kpi3_master_ariba_inv_list = kpi3_determine_company_code_ariba_inv(
    kpi3_master_ariba_inv_list
)


def kpi3_create_master_inv_list(ariba):
    ariba_data = ariba.loc[ariba["Final Relevant?"]].copy()
    ariba_data["Invoice Number"] = ariba_data["Invoice #"].replace(
        "-[^-]*$", "", regex=True
    )
    ariba_data["Invoice Number"] = ariba_data["Invoice Number"].replace(
        "^INV", "", regex=True
    )

    # onbase = onbase.loc[onbase["Final Relevant?"]].copy()

    base_data = pd.concat(
        [
            ariba_data[["Invoice Number", "Supplier #"]],
        ]
    )
    base_data = base_data.drop_duplicates()

    return base_data


kpi3_master_ovr_invoice_data = kpi3_create_master_inv_list(kpi3_master_ariba_inv_list)


def kpi3_ovr_inv_reconciliation(data):
    ariba_key = kpi3_master_ariba_inv_list.copy()
    ariba_key["Invoice Number"] = kpi3_master_ariba_inv_list["Invoice #"].replace(
        "-[^-]*$", "", regex=True
    )
    ariba_key["Invoice Number"] = ariba_key["Invoice Number"].replace(
        "^INV", "", regex=True
    )
    ariba_key["Key"] = (
        ariba_key["Invoice Number"].astype(str)
        + "-"
        + ariba_key["Supplier #"].astype(str)
    )

    data["Key"] = (
        data["Invoice Number"].astype(str) + "-" + data["Supplier #"].astype(str)
    )
    data["In Ariba?"] = data["Key"].isin(ariba_key["Key"])

    # Assumption 3.34
    ariba_match_table = ariba_key[["Key", "1st Match?"]].drop_duplicates()
    ariba_match_table = (
        ariba_match_table.groupby("Key")
        .nunique()
        .rename(columns={"1st Match?": "Match Criteria 1"})
    )

    ariba_match_table["Ariba 1st Match?"] = pd.NA
    ariba_match_table.loc[
        ariba_match_table["Match Criteria 1"] != 1, "Ariba 1st Match?"
    ] = False

    data = data.merge(
        ariba_match_table["Ariba 1st Match?"],
        how="left",
        left_on="Key",
        right_index=True,
    )

    # Assumption 3.35
    ariba_mult_source_table = ariba_key[["Key", "Final Source Doc"]].drop_duplicates()
    ariba_mult_source_table = ariba_mult_source_table.groupby("Key").nunique()

    ariba_mult_source_table["Ariba 1st Match2?"] = pd.NA
    ariba_mult_source_table.loc[
        ariba_mult_source_table["Final Source Doc"] != 1, "Ariba 1st Match2?"
    ] = False

    data = data.merge(
        ariba_mult_source_table["Ariba 1st Match2?"],
        how="left",
        left_on="Key",
        right_index=True,
    )

    # Get the Original Ariba Match.
    ariba_match_table2 = ariba_key[["Key", "1st Match?"]].copy()
    ariba_match_table2 = (
        ariba_match_table2.groupby("Key")
        .nunique()
        .rename(columns={"1st Match?": "# of Values"})
    )
    ariba_match_table2 = ariba_match_table2.merge(
        ariba_key[["Key", "1st Match?"]], how="left", left_index=True, right_on="Key"
    )
    ariba_match_table2.loc[ariba_match_table2["# of Values"] != 1, "1st Match?"] = False
    ariba_match_table2 = ariba_match_table2.drop("# of Values", axis=1)

    ariba_match_table2 = ariba_match_table2.drop_duplicates()
    ariba_match_table2 = ariba_match_table2.rename(
        columns={"1st Match?": "Original Ariba Match"}
    )

    data = data.merge(ariba_match_table2, how="left", on="Key")

    # Add Ariba Company Code (size increase by 6 due to multiple company codes for invoices).
    data = data.merge(
        ariba_key.loc[
            ariba_key["Final Relevant?"], ["Key", "Final Company Code"]
        ].drop_duplicates(),
        how="left",
        on="Key",
    ).rename(columns={"Final Company Code": "Ariba Company Code"})

    return data


kpi3_master_ovr_invoice_data = kpi3_ovr_inv_reconciliation(kpi3_master_ovr_invoice_data)


def kpi3_add_company_master_inv_list(data):
    data["Final Company Code"] = pd.NA

    onbase_ariba_agree_bool = [
        all(t)
        for t in zip(
            data["Final Company Code"].isna(),
            ~data["Ariba Company Code"].isna(),
        )
    ]

    data.loc[onbase_ariba_agree_bool, "Final Company Code"] = data.loc[
        onbase_ariba_agree_bool, "Ariba Company Code"
    ]

    only_ariba_bool = [
        all(t)
        for t in zip(
            data["Final Company Code"].isna(),
            ~data["Ariba Company Code"].isna(),
        )
    ]
    data.loc[only_ariba_bool, "Final Company Code"] = data.loc[
        only_ariba_bool, "Ariba Company Code"
    ]

    # Hard Validation 3.13
    if data.loc[data["Final Company Code"].isna()].shape[0] > 0:
        data.loc[data["Final Company Code"].isna()].to_csv("test3.13.csv")

    return data


kpi3_master_ovr_invoice_data = kpi3_add_company_master_inv_list(
    kpi3_master_ovr_invoice_data
)


def kpi3_determine_final_1st_match(data):
    data["Final 1st Match"] = pd.NA

    ariba_fail_bool = [
        all(t)
        for t in zip(
            data["Final 1st Match"].isna(),
            ~data["Original Ariba Match"].isna(),
            (
                (data["Ariba 1st Match?"].isin([False]))
                | (data["Ariba 1st Match2?"].isin([False]))
            ),
        )
    ]
    data.loc[ariba_fail_bool, "Final 1st Match"] = False

    ariba_fail_bool2 = [
        all(t)
        for t in zip(
            data["Final 1st Match"].isna(), data["Original Ariba Match"].isin([False])
        )
    ]
    data.loc[ariba_fail_bool2, "Final 1st Match"] = False

    only_ariba_bool = [
        all(t)
        for t in zip(
            data["Final 1st Match"].isna(),
            data["Original Ariba Match"].isin([True]),
        )
    ]
    data.loc[only_ariba_bool, "Final 1st Match"] = True

    both_onbase_ariba_good_bool = [
        all(t)
        for t in zip(
            data["Final 1st Match"].isna(),
            data["Original Ariba Match"].isin([True]),
        )
    ]
    data.loc[both_onbase_ariba_good_bool, "Final 1st Match"] = True

    return data


kpi3_master_ovr_invoice_data = kpi3_determine_final_1st_match(
    kpi3_master_ovr_invoice_data
)


""" KPI #4 - Invoice Processing Time"""

kpi4_raw_prerec_data = di.kpi4_import_prerec()
kpi4_raw_invpay_data = di.kpi4_import_invpay()
kpi4_raw_invrec_data = di.kpi4_import_invrec()


def kpi4_determine_ariba_prerec_type():
    data = kpi4_raw_prerec_data.copy()

    data["Direct/Indirect?"] = pd.NA

    indirect_bool = [
        any(t)
        for t in zip(
            data["Invoice Source - PREREC"] == "Blanket PO",
            data["Invoice Source - PREREC"] == "Non-PO",
            data["Invoice Source - PREREC"] == "Sales Order",
            data["Invoice Source - PREREC"] == "Contract",
            data["PO ID - PREREC"].str.contains("^EP"),
        )
    ]
    data.loc[indirect_bool, "Direct/Indirect?"] = "Indirect"

    irrelevant_bool = [
        all(t)
        for t in zip(
            data["Invoice Source - PREREC"] == "Purchase Order",
            data["PO ID - PREREC"].isna(),
        )
    ]
    data.loc[irrelevant_bool, "Direct/Indirect?"] = "N/A"

    direct_bool = [
        all(t)
        for t in zip(
            data["Direct/Indirect?"].isna(), data["PO ID - PREREC"].str.contains("^CC")
        )
    ]
    data.loc[direct_bool, "Direct/Indirect?"] = "Direct"

    # Hard Validation 3.14
    val_3_14_bool = data["Direct/Indirect?"].isna().any()
    if val_3_14_bool:
        data.loc[val_3_14_bool].to_csv("test3.14.csv")

    data.loc[
        data["Supplier - PREREC"].isin(encountered_ic_vendors), "Direct/Indirect?"
    ] = "N/A"

    # Hard Validation 3.15
    val_3_15_bool = [
        all(t)
        for t in zip(
            data["Supplier - PREREC"].str.contains("^IC", regex=True),
            ~data["Supplier - PREREC"].isin(encountered_ic_vendors),
        )
    ]
    val_3_15_bool2 = [
        all(t)
        for t in zip(
            data["Supplier - PREREC"].str.len() == 4,
            ~data["Supplier - PREREC"].isin(encountered_ic_vendors),
        )
    ]
    if data.loc[val_3_15_bool].shape[0] > 0:
        data.loc[val_3_15_bool].to_csv("test3.15.csv")
    elif data.loc[val_3_15_bool2].shape[0] > 0:
        data.loc[val_3_15_bool2].to_csv("test2.3.15.csv")

    # Hard Validation 3.16
    val_3_16_handling = di.import_val_3_16_handling()
    data = data.merge(val_3_16_handling, how="left", on="Invoice ID")
    data.loc[
        data["Invoice ID"].isin(val_3_16_handling["Invoice ID"]), "Direct/Indirect?"
    ] = data.loc[data["Invoice ID"].isin(val_3_16_handling["Invoice ID"]), "Fixed Type"]
    data = data.drop("Fixed Type", axis=1)

    val_3_16_table = (
        data[["Invoice ID", "Direct/Indirect?"]].groupby("Invoice ID").nunique()
    )
    val_3_16_bool = val_3_16_table.loc[val_3_16_table["Direct/Indirect?"] > 1]
    if val_3_16_bool.shape[0] > 0:
        data.loc[data["Invoice ID"].isin(val_3_16_bool.index)].to_csv("test3.16.csv")

    return (
        data.drop(["PO ID - PREREC", "sum(Invoice Count)"], axis=1)
        .drop_duplicates()
        .rename(columns={"Direct/Indirect?": "Direct/Indirect - PREREC"})
    )


def kpi4_determine_ariba_invrec_type():
    data = kpi4_raw_invrec_data.copy()

    data["Direct/Indirect?"] = pd.NA

    indirect_bool = [
        any(t)
        for t in zip(
            data["Invoice Source - INVREC"] == "Blanket PO",
            data["Invoice Source - INVREC"] == "Non-PO",
            data["Invoice Source - INVREC"] == "Sales Order",
            data["Invoice Source - INVREC"] == "Contract",
            data["PO ID - INVREC"].str.contains("^EP"),
        )
    ]
    data.loc[indirect_bool, "Direct/Indirect?"] = "Indirect"

    irrelevant_bool = [
        all(t)
        for t in zip(
            data["Invoice Source - INVREC"] == "Purchase Order",
            data["PO ID - INVREC"].isna(),
        )
    ]
    data.loc[irrelevant_bool, "Direct/Indirect?"] = "N/A"

    direct_bool = [
        all(t)
        for t in zip(
            data["Direct/Indirect?"].isna(), data["PO ID - INVREC"].str.contains("^CC")
        )
    ]
    data.loc[direct_bool, "Direct/Indirect?"] = "Direct"

    # Hard Validation 3.17
    val_3_17_bool = data["Direct/Indirect?"].isna().any()
    if val_3_17_bool:
        data.loc[val_3_17_bool].to_csv("test3.17.csv")

    data.loc[
        data["Supplier - INVREC"].isin(encountered_ic_vendors), "Direct/Indirect?"
    ] = "N/A"

    # Hard Validation 3.18
    val_3_18_bool = [
        all(t)
        for t in zip(
            data["Supplier - INVREC"].str.contains("^IC", regex=True),
            ~data["Supplier - INVREC"].isin(encountered_ic_vendors),
        )
    ]
    val_3_18_bool2 = [
        all(t)
        for t in zip(
            data["Supplier - INVREC"].str.len() == 4,
            ~data["Supplier - INVREC"].isin(encountered_ic_vendors),
        )
    ]
    if data.loc[val_3_18_bool].shape[0] > 0:
        data.loc[val_3_18_bool].to_csv("test3.18.csv")
    elif data.loc[val_3_18_bool2].shape[0] > 0:
        data.loc[val_3_18_bool2].to_csv("test2.3.18.csv")

    # Hard Validation 3.19
    val_3_19_handling = di.import_val_3_19_handling()
    data = data.merge(val_3_19_handling, how="left", on="Invoice ID")
    data.loc[
        data["Invoice ID"].isin(val_3_19_handling["Invoice ID"]), "Direct/Indirect?"
    ] = data.loc[data["Invoice ID"].isin(val_3_19_handling["Invoice ID"]), "Fixed Type"]
    data = data.drop("Fixed Type", axis=1)

    val_3_19_table = (
        data[["Invoice ID", "Direct/Indirect?"]].groupby("Invoice ID").nunique()
    )
    val_3_19_bool = val_3_19_table.loc[val_3_19_table["Direct/Indirect?"] > 1]
    if val_3_19_bool.shape[0] > 0:
        data.loc[data["Invoice ID"].isin(val_3_19_bool.index)].to_csv("test3.19.csv")

    return (
        data.drop(["PO ID - INVREC", "sum(Invoice Count)"], axis=1)
        .drop_duplicates()
        .rename(columns={"Direct/Indirect?": "Direct/Indirect - INVREC"})
    )


def kpi4_determine_ariba_company(data):
    relevant_data = data[
        [
            "Invoice ID",
            "Company Code - PREREC",
            "Company Code - INVREC",
            "Purchasing Unit - INVPAY",
        ]
    ].copy()

    relevant_data["Final Company"] = pd.NA

    all_same_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Company"].isna(),
            ~relevant_data["Company Code - PREREC"].isna(),
            ~relevant_data["Company Code - INVREC"].isna(),
            ~relevant_data["Purchasing Unit - INVPAY"].isna(),
            relevant_data["Company Code - PREREC"]
            == relevant_data["Company Code - INVREC"],
            relevant_data["Company Code - PREREC"]
            == relevant_data["Purchasing Unit - INVPAY"],
        )
    ]

    relevant_data.loc[all_same_bool, "Final Company"] = relevant_data.loc[
        all_same_bool, "Company Code - PREREC"
    ]

    only_invrec_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Company"].isna(),
            relevant_data["Company Code - PREREC"].isna(),
            ~relevant_data["Company Code - INVREC"].isna(),
            relevant_data["Purchasing Unit - INVPAY"].isna(),
        )
    ]
    relevant_data.loc[only_invrec_bool, "Final Company"] = relevant_data.loc[
        only_invrec_bool, "Company Code - INVREC"
    ]

    # Assumption 3.39
    unknown_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Company"].isna(),
            relevant_data["Company Code - PREREC"].isna(),
            relevant_data["Company Code - INVREC"].isna(),
            relevant_data["Purchasing Unit - INVPAY"].isna(),
        )
    ]
    relevant_data.loc[unknown_bool, "Final Company"] = "N/A"

    only_invpay_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Company"].isna(),
            relevant_data["Company Code - PREREC"].isna(),
            relevant_data["Company Code - INVREC"].isna(),
            ~relevant_data["Purchasing Unit - INVPAY"].isna(),
        )
    ]
    relevant_data.loc[only_invpay_bool, "Final Company"] = relevant_data.loc[
        only_invpay_bool, "Purchasing Unit - INVPAY"
    ]

    only_prerec_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Company"].isna(),
            ~relevant_data["Company Code - PREREC"].isna(),
            relevant_data["Company Code - INVREC"].isna(),
            relevant_data["Purchasing Unit - INVPAY"].isna(),
        )
    ]
    relevant_data.loc[only_prerec_bool, "Final Company"] = relevant_data.loc[
        only_prerec_bool, "Company Code - PREREC"
    ]

    only_rec_pay_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Company"].isna(),
            relevant_data["Company Code - PREREC"].isna(),
            ~relevant_data["Company Code - INVREC"].isna(),
            ~relevant_data["Purchasing Unit - INVPAY"].isna(),
            relevant_data["Company Code - INVREC"]
            == relevant_data["Purchasing Unit - INVPAY"],
        )
    ]
    relevant_data.loc[only_rec_pay_bool, "Final Company"] = relevant_data.loc[
        only_rec_pay_bool, "Company Code - INVREC"
    ]

    only_pre_pay_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Company"].isna(),
            ~relevant_data["Company Code - PREREC"].isna(),
            relevant_data["Company Code - INVREC"].isna(),
            ~relevant_data["Purchasing Unit - INVPAY"].isna(),
            relevant_data["Company Code - PREREC"]
            == relevant_data["Purchasing Unit - INVPAY"],
        )
    ]
    relevant_data.loc[only_pre_pay_bool, "Final Company"] = relevant_data.loc[
        only_pre_pay_bool, "Company Code - PREREC"
    ]

    only_pre_rec_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Company"].isna(),
            ~relevant_data["Company Code - PREREC"].isna(),
            ~relevant_data["Company Code - INVREC"].isna(),
            relevant_data["Purchasing Unit - INVPAY"].isna(),
            relevant_data["Company Code - PREREC"]
            == relevant_data["Company Code - INVREC"],
        )
    ]
    relevant_data.loc[only_pre_rec_bool, "Final Company"] = relevant_data.loc[
        only_pre_rec_bool, "Company Code - PREREC"
    ]

    pre_rec_same_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Company"].isna(),
            ~relevant_data["Company Code - PREREC"].isna(),
            ~relevant_data["Company Code - INVREC"].isna(),
            ~relevant_data["Purchasing Unit - INVPAY"].isna(),
            relevant_data["Company Code - PREREC"]
            == relevant_data["Company Code - INVREC"],
        )
    ]
    relevant_data.loc[pre_rec_same_bool, "Final Company"] = relevant_data.loc[
        pre_rec_same_bool, "Company Code - PREREC"
    ]

    only_rec_good_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Company"].isna(),
            ~relevant_data["Company Code - PREREC"].isna(),
            ~relevant_data["Company Code - INVREC"].isna(),
            ~relevant_data["Purchasing Unit - INVPAY"].isna(),
            relevant_data["Company Code - PREREC"]
            == relevant_data["Purchasing Unit - INVPAY"],
            relevant_data["Company Code - PREREC"]
            != relevant_data["Company Code - INVREC"],
        )
    ]
    relevant_data.loc[only_rec_good_bool, "Final Company"] = relevant_data.loc[
        only_rec_good_bool, "Company Code - INVREC"
    ]

    prerec_bad_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Company"].isna(),
            ~relevant_data["Company Code - PREREC"].isna(),
            ~relevant_data["Company Code - INVREC"].isna(),
            ~relevant_data["Purchasing Unit - INVPAY"].isna(),
            relevant_data["Company Code - INVREC"]
            == relevant_data["Purchasing Unit - INVPAY"],
            relevant_data["Company Code - PREREC"]
            != relevant_data["Company Code - INVREC"],
        )
    ]
    relevant_data.loc[prerec_bad_bool, "Final Company"] = relevant_data.loc[
        prerec_bad_bool, "Company Code - INVREC"
    ]

    both_rec_pay_pop_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Company"].isna(),
            relevant_data["Company Code - PREREC"].isna(),
            ~relevant_data["Company Code - INVREC"].isna(),
            ~relevant_data["Purchasing Unit - INVPAY"].isna(),
            relevant_data["Company Code - INVREC"]
            != relevant_data["Purchasing Unit - INVPAY"],
        )
    ]
    relevant_data.loc[both_rec_pay_pop_bool, "Final Company"] = relevant_data.loc[
        both_rec_pay_pop_bool, "Company Code - INVREC"
    ]

    # Hard Validation 3.20
    val_3_20 = relevant_data["Final Company"].isna()
    if val_3_20.any():
        relevant_data.loc[val_3_20].to_csv("test3.20.csv")

    return relevant_data[["Invoice ID", "Final Company"]]


def kpi4_determine_ariba_submit_date(data):
    relevant_data = data[
        [
            "Invoice ID",
            "Date Created - PREREC",
            "Date Created - INVPAY",
            "Submit Date - INVREC",
        ]
    ].copy()

    relevant_data["Final Submit Date"] = pd.NA

    all_agree_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Submit Date"].isna(),
            ~relevant_data["Date Created - PREREC"].isna(),
            ~relevant_data["Date Created - INVPAY"].isna(),
            ~relevant_data["Submit Date - INVREC"].isna(),
            relevant_data["Date Created - PREREC"]
            == relevant_data["Date Created - INVPAY"],
            relevant_data["Date Created - PREREC"]
            == relevant_data["Submit Date - INVREC"],
        )
    ]
    relevant_data.loc[all_agree_bool, "Final Submit Date"] = relevant_data.loc[
        all_agree_bool, "Date Created - PREREC"
    ]

    only_invrec_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Submit Date"].isna(),
            relevant_data["Date Created - PREREC"].isna(),
            relevant_data["Date Created - INVPAY"].isna(),
            ~relevant_data["Submit Date - INVREC"].isna(),
        )
    ]
    relevant_data.loc[only_invrec_bool, "Final Submit Date"] = relevant_data.loc[
        only_invrec_bool, "Submit Date - INVREC"
    ]

    only_prerec_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Submit Date"].isna(),
            ~relevant_data["Date Created - PREREC"].isna(),
            relevant_data["Date Created - INVPAY"].isna(),
            relevant_data["Submit Date - INVREC"].isna(),
        )
    ]
    relevant_data.loc[only_prerec_bool, "Final Submit Date"] = relevant_data.loc[
        only_prerec_bool, "Date Created - PREREC"
    ]

    pay_rec_good_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Submit Date"].isna(),
            relevant_data["Date Created - PREREC"].isna(),
            ~relevant_data["Date Created - INVPAY"].isna(),
            ~relevant_data["Submit Date - INVREC"].isna(),
            relevant_data["Submit Date - INVREC"]
            == relevant_data["Date Created - INVPAY"],
        )
    ]
    relevant_data.loc[pay_rec_good_bool, "Final Submit Date"] = relevant_data.loc[
        pay_rec_good_bool, "Submit Date - INVREC"
    ]

    only_pre_rec_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Submit Date"].isna(),
            ~relevant_data["Date Created - PREREC"].isna(),
            relevant_data["Date Created - INVPAY"].isna(),
            ~relevant_data["Submit Date - INVREC"].isna(),
            relevant_data["Submit Date - INVREC"]
            == relevant_data["Date Created - PREREC"],
        )
    ]
    relevant_data.loc[only_pre_rec_bool, "Final Submit Date"] = relevant_data.loc[
        only_pre_rec_bool, "Submit Date - INVREC"
    ]

    all_dif_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Submit Date"].isna(),
            ~relevant_data["Date Created - PREREC"].isna(),
            ~relevant_data["Date Created - INVPAY"].isna(),
            ~relevant_data["Submit Date - INVREC"].isna(),
            relevant_data["Date Created - PREREC"]
            != relevant_data["Submit Date - INVREC"],
            relevant_data["Date Created - PREREC"]
            != relevant_data["Date Created - INVPAY"],
            relevant_data["Submit Date - INVREC"]
            != relevant_data["Date Created - INVPAY"],
        )
    ]
    relevant_data.loc[all_dif_bool, "Final Submit Date"] = relevant_data.loc[
        all_dif_bool, "Submit Date - INVREC"
    ]

    pre_rec_same_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Submit Date"].isna(),
            ~relevant_data["Date Created - PREREC"].isna(),
            ~relevant_data["Date Created - INVPAY"].isna(),
            ~relevant_data["Submit Date - INVREC"].isna(),
            relevant_data["Date Created - PREREC"]
            == relevant_data["Submit Date - INVREC"],
            relevant_data["Date Created - PREREC"]
            != relevant_data["Date Created - INVPAY"],
        )
    ]
    relevant_data.loc[pre_rec_same_bool, "Final Submit Date"] = relevant_data.loc[
        pre_rec_same_bool, "Submit Date - INVREC"
    ]

    pay_rec_same_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Submit Date"].isna(),
            ~relevant_data["Date Created - PREREC"].isna(),
            ~relevant_data["Date Created - INVPAY"].isna(),
            ~relevant_data["Submit Date - INVREC"].isna(),
            relevant_data["Submit Date - INVREC"]
            == relevant_data["Date Created - INVPAY"],
            relevant_data["Date Created - PREREC"]
            != relevant_data["Date Created - INVPAY"],
        )
    ]
    relevant_data.loc[pay_rec_same_bool, "Final Submit Date"] = relevant_data.loc[
        pay_rec_same_bool, "Date Created - INVPAY"
    ]

    only_rec_good_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Submit Date"].isna(),
            ~relevant_data["Date Created - PREREC"].isna(),
            relevant_data["Date Created - INVPAY"].isna(),
            ~relevant_data["Submit Date - INVREC"].isna(),
            relevant_data["Date Created - PREREC"]
            != relevant_data["Submit Date - INVREC"],
        )
    ]
    relevant_data.loc[only_rec_good_bool, "Final Submit Date"] = relevant_data.loc[
        only_rec_good_bool, "Submit Date - INVREC"
    ]

    only_pay_good_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Submit Date"].isna(),
            ~relevant_data["Date Created - PREREC"].isna(),
            ~relevant_data["Date Created - INVPAY"].isna(),
            relevant_data["Submit Date - INVREC"].isna(),
            relevant_data["Date Created - PREREC"]
            != relevant_data["Date Created - INVPAY"],
        )
    ]
    relevant_data.loc[only_pay_good_bool, "Final Submit Date"] = relevant_data.loc[
        only_pay_good_bool, "Date Created - INVPAY"
    ]

    pre_pay_same_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Submit Date"].isna(),
            ~relevant_data["Date Created - PREREC"].isna(),
            ~relevant_data["Date Created - INVPAY"].isna(),
            relevant_data["Submit Date - INVREC"].isna(),
            relevant_data["Date Created - PREREC"]
            == relevant_data["Date Created - INVPAY"],
        )
    ]
    relevant_data.loc[pre_pay_same_bool, "Final Submit Date"] = relevant_data.loc[
        pre_pay_same_bool, "Date Created - INVPAY"
    ]

    only_rec_good_bool2 = [
        all(t)
        for t in zip(
            relevant_data["Final Submit Date"].isna(),
            relevant_data["Date Created - PREREC"].isna(),
            ~relevant_data["Date Created - INVPAY"].isna(),
            ~relevant_data["Submit Date - INVREC"].isna(),
            relevant_data["Submit Date - INVREC"]
            != relevant_data["Date Created - INVPAY"],
        )
    ]
    relevant_data.loc[only_rec_good_bool2, "Final Submit Date"] = relevant_data.loc[
        only_rec_good_bool2, "Submit Date - INVREC"
    ]

    # Hard Validation 3.21
    val_3_21_bool = relevant_data["Final Submit Date"].isna()
    if val_3_21_bool.any():
        relevant_data.loc[val_3_21_bool].to_csv("test3.21.csv")

    return relevant_data[["Invoice ID", "Final Submit Date"]]


def kpi4_determine_ariba_inv_status(data):
    relevant_data = data[
        [
            "Invoice ID",
            "Inv Status - PREREC",
            "Invoice Status - INVREC",
            "Rec Status - INVREC",
            "Inv Status - INVPAY",
        ]
    ].copy()

    relevant_data["Final Status"] = pd.NA

    relevant_data["Base Status Same?"] = (
        relevant_data["Inv Status - PREREC"] == relevant_data["Invoice Status - INVREC"]
    )

    relevant_data["Base Status"] = pd.NA

    cancelled_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Status"].isna(),
            relevant_data["Base Status Same?"],
            relevant_data.loc[
                :,
                [
                    "Inv Status - PREREC",
                    "Invoice Status - INVREC",
                    "Rec Status - INVREC",
                ],
            ]
            .isin(["Canceling"])
            .all(axis=1),
        )
    ]
    relevant_data.loc[cancelled_bool, "Final Status"] = "Canceling"

    reconciled_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Status"].isna(),
            relevant_data["Base Status Same?"],
            relevant_data["Inv Status - PREREC"] == "Reconciled",
            relevant_data["Invoice Status - INVREC"] == "Reconciled",
            relevant_data["Rec Status - INVREC"].isin(
                ["Paying", "Paid", "Paying Failed"]
            ),
        )
    ]
    relevant_data.loc[reconciled_bool, "Final Status"] = "Reconciled"

    false_reconciled_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Status"].isna(),
            relevant_data["Base Status Same?"],
            relevant_data["Inv Status - PREREC"] == "Reconciled",
            relevant_data["Invoice Status - INVREC"] == "Reconciled",
            relevant_data["Rec Status - INVREC"].isin(["Reconciling", "Approving"]),
        )
    ]
    relevant_data.loc[false_reconciled_bool, "Final Status"] = relevant_data.loc[
        false_reconciled_bool, "Rec Status - INVREC"
    ]

    reconciling_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Status"].isna(),
            relevant_data["Base Status Same?"],
            relevant_data["Inv Status - PREREC"] == "Reconciling",
            relevant_data["Invoice Status - INVREC"] == "Reconciling",
            relevant_data["Rec Status - INVREC"].isin(["Reconciling", "Approving"]),
        )
    ]
    relevant_data.loc[reconciling_bool, "Final Status"] = relevant_data.loc[
        reconciling_bool, "Rec Status - INVREC"
    ]

    rejected_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Status"].isna(),
            relevant_data["Base Status Same?"],
            relevant_data["Inv Status - PREREC"] == "Rejected",
            relevant_data["Invoice Status - INVREC"] == "Rejected",
            relevant_data["Rec Status - INVREC"].isin(["Rejected", "Failed Rejecting"]),
        )
    ]
    relevant_data.loc[rejected_bool, "Final Status"] = "Rejected"

    only_prerec_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Status"].isna(),
            ~relevant_data["Base Status Same?"],
            ~relevant_data["Inv Status - PREREC"].isna(),
            relevant_data["Invoice Status - INVREC"].isna(),
            relevant_data["Rec Status - INVREC"].isna(),
        )
    ]
    relevant_data.loc[only_prerec_bool, "Final Status"] = relevant_data.loc[
        only_prerec_bool, "Inv Status - PREREC"
    ]

    invrec_good_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Status"].isna(),
            ~relevant_data["Base Status Same?"],
            relevant_data["Inv Status - PREREC"].isna(),
            ~relevant_data["Invoice Status - INVREC"].isna(),
            ~relevant_data["Rec Status - INVREC"].isna(),
            relevant_data["Invoice Status - INVREC"] == "Reconciled",
            relevant_data["Rec Status - INVREC"].isin(["Paying", "Paid"]),
        )
    ]
    relevant_data.loc[invrec_good_bool, "Final Status"] = relevant_data.loc[
        invrec_good_bool, "Invoice Status - INVREC"
    ]

    invrec_good_bool2 = [
        all(t)
        for t in zip(
            relevant_data["Final Status"].isna(),
            ~relevant_data["Base Status Same?"],
            relevant_data["Inv Status - PREREC"].isna(),
            ~relevant_data["Invoice Status - INVREC"].isna(),
            ~relevant_data["Rec Status - INVREC"].isna(),
            relevant_data["Invoice Status - INVREC"] == "Rejected",
            relevant_data["Rec Status - INVREC"].isin(["Rejected"]),
        )
    ]
    relevant_data.loc[invrec_good_bool2, "Final Status"] = relevant_data.loc[
        invrec_good_bool2, "Invoice Status - INVREC"
    ]

    invrec_good_bool3 = [
        all(t)
        for t in zip(
            relevant_data["Final Status"].isna(),
            ~relevant_data["Base Status Same?"],
            relevant_data["Inv Status - PREREC"].isna(),
            ~relevant_data["Invoice Status - INVREC"].isna(),
            ~relevant_data["Rec Status - INVREC"].isna(),
            relevant_data["Invoice Status - INVREC"] == "Reconciling",
            relevant_data["Rec Status - INVREC"].isin(["Reconciling"]),
        )
    ]
    relevant_data.loc[invrec_good_bool3, "Final Status"] = relevant_data.loc[
        invrec_good_bool3, "Invoice Status - INVREC"
    ]

    # Assumption 3.43
    raise_from_dead_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Status"].isna(),
            relevant_data["Base Status Same?"],
            relevant_data["Inv Status - PREREC"].isin(["Rejected"]),
            relevant_data["Invoice Status - INVREC"].isin(["Rejected"]),
            relevant_data["Rec Status - INVREC"].isin(["Reconciling"]),
            relevant_data["Inv Status - INVPAY"].isin(["Rejected"]),
        )
    ]
    relevant_data.loc[raise_from_dead_bool, "Final Status"] = relevant_data.loc[
        raise_from_dead_bool, "Invoice Status - INVREC"
    ]

    # Hard Validation 3.22
    val_3_22_bool = relevant_data["Final Status"].isna()
    if val_3_22_bool.any():
        relevant_data.loc[val_3_22_bool].to_csv("test3.22.csv")

    return relevant_data[["Invoice ID", "Final Status"]]


def kpi4_determine_ariba_approved_date(data):
    relevant_data = data[
        ["Invoice ID", "Approved Date - INVREC", "App Date - INVPAY", "Final Status"]
    ].copy()

    relevant_data["Final Approved Date"] = pd.NA

    rec_pay_same_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Approved Date"].isna(),
            ~relevant_data["Approved Date - INVREC"].isna(),
            ~relevant_data["App Date - INVPAY"].isna(),
            relevant_data["Approved Date - INVREC"]
            == relevant_data["App Date - INVPAY"],
        )
    ]
    relevant_data.loc[rec_pay_same_bool, "Final Approved Date"] = relevant_data.loc[
        rec_pay_same_bool, "App Date - INVPAY"
    ]

    only_rec_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Approved Date"].isna(),
            ~relevant_data["Approved Date - INVREC"].isna(),
            relevant_data["App Date - INVPAY"].isna(),
        )
    ]
    relevant_data.loc[only_rec_bool, "Final Approved Date"] = relevant_data.loc[
        only_rec_bool, "Approved Date - INVREC"
    ]

    only_pay_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Approved Date"].isna(),
            relevant_data["Approved Date - INVREC"].isna(),
            ~relevant_data["App Date - INVPAY"].isna(),
        )
    ]
    relevant_data.loc[only_pay_bool, "Final Approved Date"] = relevant_data.loc[
        only_pay_bool, "App Date - INVPAY"
    ]

    rec_good_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Approved Date"].isna(),
            ~relevant_data["Approved Date - INVREC"].isna(),
            ~relevant_data["App Date - INVPAY"].isna(),
            relevant_data["Approved Date - INVREC"]
            != relevant_data["App Date - INVPAY"],
        )
    ]
    relevant_data.loc[rec_good_bool, "Final Approved Date"] = relevant_data.loc[
        rec_good_bool, "Approved Date - INVREC"
    ]

    no_value_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Approved Date"].isna(),
            relevant_data["Approved Date - INVREC"].isna(),
            relevant_data["App Date - INVPAY"].isna(),
        )
    ]
    relevant_data.loc[no_value_bool, "Final Approved Date"] = pd.NA

    # Hard Validation 3.23
    val_3_23_handling = di.import_val_3_23_handling()

    for x in val_3_23_handling["Invoice ID"]:
        relevant_data.loc[relevant_data["Invoice ID"] == x, "Final Approved Date"] = (
            val_3_23_handling.loc[
                val_3_23_handling["Invoice ID"] == x, "Fixed Approved Date"
            ]
        ).squeeze()

    val_3_23_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Approved Date"].isna(),
            relevant_data["Final Status"].isin(["Reconciled"]),
        )
    ]
    if relevant_data.loc[val_3_23_bool].shape[0] > 0:
        relevant_data.loc[val_3_23_bool].to_csv("test3.23.csv")

    return relevant_data[["Invoice ID", "Final Approved Date"]]


def kpi4_determine_ariba_supplier_code(data):
    relevant_data = data[
        ["Invoice ID", "Supplier - PREREC", "Supplier - INVREC"]
    ].copy()

    relevant_data["Final Supplier"] = pd.NA

    relevant_data["Supplier - PREREC"] = relevant_data["Supplier - PREREC"].replace(
        "Unclassified", pd.NA
    )
    relevant_data["Supplier - INVREC"] = relevant_data["Supplier - INVREC"].replace(
        "Unclassified", pd.NA
    )

    # Hard Validation 3.24
    val_3_24_bool = [
        all(t)
        for t in zip(
            ~relevant_data["Supplier - PREREC"].isna(),
            ~relevant_data["Supplier - INVREC"].isna(),
            relevant_data["Supplier - PREREC"] != relevant_data["Supplier - INVREC"],
        )
    ]
    if pd.DataFrame(val_3_24_bool).any()[0]:
        relevant_data.loc[val_3_24_bool].to_csv("test3.24.csv")

    same_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Supplier"].isna(),
            ~relevant_data["Supplier - PREREC"].isna(),
            ~relevant_data["Supplier - INVREC"].isna(),
            relevant_data["Supplier - PREREC"] == relevant_data["Supplier - INVREC"],
        )
    ]
    relevant_data.loc[same_bool, "Final Supplier"] = relevant_data.loc[
        same_bool, "Supplier - PREREC"
    ]

    no_value_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Supplier"].isna(),
            relevant_data["Supplier - PREREC"].isna(),
            relevant_data["Supplier - INVREC"].isna(),
        )
    ]
    relevant_data.loc[no_value_bool, "Final Supplier"] = "N/A"

    only_pre_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Supplier"].isna(),
            ~relevant_data["Supplier - PREREC"].isna(),
            relevant_data["Supplier - INVREC"].isna(),
        )
    ]
    relevant_data.loc[only_pre_bool, "Final Supplier"] = relevant_data.loc[
        only_pre_bool, "Supplier - PREREC"
    ]

    only_rec_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Supplier"].isna(),
            relevant_data["Supplier - PREREC"].isna(),
            ~relevant_data["Supplier - INVREC"].isna(),
        )
    ]
    relevant_data.loc[only_rec_bool, "Final Supplier"] = relevant_data.loc[
        only_rec_bool, "Supplier - INVREC"
    ]

    # Hard Validation 3.25
    val_3_25_bool = relevant_data["Final Supplier"].isna()
    if val_3_25_bool.any():
        relevant_data.loc[val_3_25_bool].to_csv("test3.25.csv")

    return relevant_data[["Invoice ID", "Final Supplier"]]


def kpi4_determine_ariba_sub_method(data):
    relevant_data = data[
        ["Invoice ID", "Inv Submission - PREREC", "Invoice Submission Method - INVREC"]
    ].copy()

    relevant_data["Final Sub Method"] = pd.NA
    same_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Sub Method"].isna(),
            ~relevant_data["Inv Submission - PREREC"].isna(),
            ~relevant_data["Invoice Submission Method - INVREC"].isna(),
            relevant_data["Inv Submission - PREREC"]
            == relevant_data["Invoice Submission Method - INVREC"],
        )
    ]
    relevant_data.loc[same_bool, "Final Sub Method"] = relevant_data.loc[
        same_bool, "Inv Submission - PREREC"
    ]

    only_prerec_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Sub Method"].isna(),
            ~relevant_data["Inv Submission - PREREC"].isna(),
            relevant_data["Invoice Submission Method - INVREC"].isna(),
        )
    ]
    relevant_data.loc[only_prerec_bool, "Final Sub Method"] = relevant_data.loc[
        only_prerec_bool, "Inv Submission - PREREC"
    ]

    only_rec_bool = [
        all(t)
        for t in zip(
            relevant_data["Final Sub Method"].isna(),
            relevant_data["Inv Submission - PREREC"].isna(),
            ~relevant_data["Invoice Submission Method - INVREC"].isna(),
        )
    ]
    relevant_data.loc[only_rec_bool, "Final Sub Method"] = relevant_data.loc[
        only_rec_bool, "Invoice Submission Method - INVREC"
    ]

    relevant_data = relevant_data.merge(
        data[["Invoice ID", "Final Supplier"]], how="left", on="Invoice ID"
    )

    # Hard Validation 3.26
    val_3_26_handling = di.import_val_3_26_handling()

    relevant_data = relevant_data.merge(
        val_3_26_handling, how="left", on="Final Supplier"
    )

    correct_method_bool = [
        all(t)
        for t in zip(
            ~relevant_data["Fixed Method"].isna(),
            relevant_data["Final Sub Method"].isna(),
        )
    ]
    relevant_data.loc[correct_method_bool, "Final Sub Method"] = relevant_data.loc[
        correct_method_bool, "Fixed Method"
    ]
    relevant_data = relevant_data.drop("Fixed Method", axis=1)

    val_3_26_bool = relevant_data["Final Sub Method"].isna()
    if val_3_26_bool.any():
        relevant_data.loc[val_3_26_bool].to_csv("test3.26.csv")

    return relevant_data[["Invoice ID", "Final Sub Method"]]


def kpi4_create_ariba_master():
    data = pd.DataFrame(
        pd.concat(
            [
                kpi4_raw_invpay_data["Invoice ID"],
                kpi4_raw_prerec_data["Invoice ID"],
                kpi4_raw_invrec_data["Invoice ID"],
            ]
        ).drop_duplicates()
    )

    data["In PREREC?"] = data["Invoice ID"].isin(kpi4_raw_prerec_data["Invoice ID"])
    data["In INVPAY?"] = data["Invoice ID"].isin(kpi4_raw_invpay_data["Invoice ID"])
    data["In INVREC?"] = data["Invoice ID"].isin(kpi4_raw_invrec_data["Invoice ID"])

    # Assumption 3.38
    drop_invpay_bool = [
        all(t)
        for t in zip(
            data["In INVPAY?"],
            data["In PREREC?"].isin([False]),
            data["In INVREC?"].isin([False]),
        )
    ]
    data["Relevant1?"] = pd.NA
    data.loc[drop_invpay_bool, "Relevant1?"] = False
    data = data.loc[~data["Relevant1?"].isin([False])].drop("Relevant1?", axis=1)

    # Pull in PREREC Info
    data = data.merge(kpi4_determine_ariba_prerec_type(), how="left", on="Invoice ID")

    # Pull in INVREC info
    data = data.merge(kpi4_determine_ariba_invrec_type(), how="left", on="Invoice ID")

    # Pull in INVPAY info
    data = data.merge(kpi4_raw_invpay_data, how="left", on="Invoice ID")
    data = data.drop("sum(Adjustment Amount)", axis=1)

    # Determine Company
    data = data.merge(kpi4_determine_ariba_company(data), how="left", on="Invoice ID")

    # Determine Final Date Submitted
    kpi4_determine_ariba_prerec_type()["Date Created - PREREC"]

    data = data.merge(
        kpi4_determine_ariba_submit_date(data), how="left", on="Invoice ID"
    )

    # Determine Final Status
    data = data.merge(
        kpi4_determine_ariba_inv_status(data), how="left", on="Invoice ID"
    )

    # Determine Final Approved
    data = data.merge(
        kpi4_determine_ariba_approved_date(data), how="left", on="Invoice ID"
    )

    # Determine Supplier Code
    data = data.merge(
        kpi4_determine_ariba_supplier_code(data), how="left", on="Invoice ID"
    )

    # Determine Final Submission Method
    data = data.merge(
        kpi4_determine_ariba_sub_method(data), how="left", on="Invoice ID"
    )

    # Determine Relevant Entries
    data["Ariba Relevant?"] = data["Final Status"].isin(["Reconciled"])

    return data


kpi4_master_ariba_data = kpi4_create_ariba_master()

ahpre_data = di.import_ahpre_data()
ahinv_data = di.import_ahinv_data()
appre_data = di.import_appre_data()
apinv_data = di.import_apinv_data()


def kpi4_update_ariba_submitted_date(data):
    rel_data = pd.DataFrame(
        pd.concat(
            [ahpre_data["Approvable ID"], ahinv_data["Approvable ID"]]
        ).drop_duplicates()
    )

    rel_data = rel_data.merge(ahpre_data, how="left", on="Approvable ID")
    rel_data = rel_data.merge(ahinv_data, how="left", on="Approvable ID")

    sub_date_table = (
        pd.concat(
            [
                rel_data[["Approvable ID", "Assigned Date - AHPRE"]],
                rel_data[["Approvable ID", "Assign Date - AHINV"]].rename(
                    columns={"Assign Date - AHINV": "Assigned Date - AHPRE"}
                ),
            ]
        )
        .dropna()
        .drop_duplicates()
    )
    sub_date_table = (
        sub_date_table.sort_values("Assigned Date - AHPRE", ascending=True)
        .groupby("Approvable ID")
        .first()
    )

    data = data.merge(
        sub_date_table, how="left", left_on="Invoice ID", right_index=True
    )

    earlier_date_bool = [
        all(t)
        for t in zip(
            ~data["Assigned Date - AHPRE"].isna(),
            data["Assigned Date - AHPRE"] < data["Final Submit Date"],
        )
    ]
    data.loc[earlier_date_bool, "Final Submit Date"] = data.loc[
        earlier_date_bool, "Assigned Date - AHPRE"
    ]

    data = data.drop("Assigned Date - AHPRE", axis=1)

    return data


kpi4_master_ariba_data = kpi4_update_ariba_submitted_date(kpi4_master_ariba_data)


def kpi4_update_ariba_approved_date(data):
    rel_data = pd.DataFrame(
        pd.concat(
            [
                ahpre_data["Approvable ID"],
                ahinv_data["Approvable ID"],
                appre_data["Approvable ID"],
                apinv_data["Approvable ID"],
            ]
        ).drop_duplicates()
    )

    rel_data = rel_data.merge(ahpre_data, how="left", on="Approvable ID")
    rel_data = rel_data.merge(ahinv_data, how="left", on="Approvable ID")
    rel_data = rel_data.merge(appre_data, how="left", on="Approvable ID")
    rel_data = rel_data.merge(apinv_data, how="left", on="Approvable ID")

    app_date_table = (
        pd.concat(
            [
                rel_data[["Approvable ID", "Action Date - AHPRE"]],
                rel_data[["Approvable ID", "Action Date - AHINV"]].rename(
                    columns={"Action Date - AHINV": "Action Date - AHPRE"}
                ),
                rel_data[["Approvable ID", "Action Date - APPRE"]].rename(
                    columns={"Action Date - APPRE": "Action Date - AHPRE"}
                ),
                rel_data[["Approvable ID", "Action Date - APINV"]].rename(
                    columns={"Action Date - APINV": "Action Date - AHPRE"}
                ),
            ]
        )
        .dropna()
        .drop_duplicates()
    )

    app_date_table = (
        app_date_table.sort_values("Action Date - AHPRE", ascending=False)
        .groupby("Approvable ID")
        .first()
    )

    data = data.merge(
        app_date_table, how="left", left_on="Invoice ID", right_index=True
    )

    later_date_bool = [
        all(t)
        for t in zip(
            ~data["Action Date - AHPRE"].isna(),
            ~data["Final Approved Date"].isna(),
            data["Action Date - AHPRE"].dt.date
            > pd.to_datetime(
                data["Final Approved Date"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
            ),
        )
    ]
    data.loc[later_date_bool, "Final Approved Date"] = data.loc[
        later_date_bool, "Action Date - AHPRE"
    ]
    data = data.drop("Action Date - AHPRE", axis=1)

    return data


kpi4_master_ariba_data = kpi4_update_ariba_approved_date(kpi4_master_ariba_data)


""" Reconcile Onbase vs Ariba """


def kpi4_add_invoice_num_ariba(data):
    data["Invoice Number"] = data["Invoice ID"].copy()

    return data


kpi4_master_ariba_data = kpi4_add_invoice_num_ariba(kpi4_master_ariba_data)


def kpi4_add_inv_relevance_master(data, ariba):
    ariba_relevant_table = ariba.loc[ariba["Ariba Relevant?"].isin([True]), "Key"]

    # Excel increase by 7 due to upper/lower issue.
    ariba.loc[ariba["Key"].isin(ariba_relevant_table), "Ariba Relevant?"] = True
    data = data.merge(
        ariba[["Key", "Ariba Relevant?"]].drop_duplicates(), how="left", on="Key"
    )

    return data


def kpi4_determine_master_inv_relevance(data):
    data["Final Relevant?"] = pd.NA
    data["Final Relevant?"] = data["Ariba Relevant?"].copy()

    # Hard Validation 4.1
    val_4_1_bool = data["Final Relevant?"].isna()

    if val_4_1_bool.any():
        data.loc[val_4_1_bool].to_csv("test4.1.csv")

    result = data.loc[:, ["Key", "Final Relevant?", "In Ariba?"]].copy()
    return result


def kpi4_add_ariba_approved_date(data):
    prelim_ariba = kpi4_master_ariba_data[
        ["Invoice Number", "Final Supplier", "Final Approved Date", "Ariba Relevant?"]
    ].copy()
    prelim_ariba["Key"] = (
        prelim_ariba["Invoice Number"].astype(str)
        + "-"
        + prelim_ariba["Final Supplier"].astype(str)
    )

    relevant_ariba = prelim_ariba.loc[
        prelim_ariba["Ariba Relevant?"], ["Key", "Final Approved Date"]
    ]
    rel_ariba_approval_table = (
        relevant_ariba.sort_values("Final Approved Date", ascending=False)
        .groupby("Key")
        .first()
    )

    data = data.merge(rel_ariba_approval_table, how="left", on="Key")

    return data


def kpi4_add_1st_create_date(data):
    prelim_ariba = kpi4_master_ariba_data[
        ["Final Submit Date", "Invoice Number", "Final Supplier"]
    ].copy()

    prelim_ariba["Key"] = (
        prelim_ariba["Invoice Number"].astype(str)
        + "-"
        + prelim_ariba["Final Supplier"].astype(str)
    )

    only_ariba_bool = data["In Ariba?"].isin([True])
    only_ariba_list = data.loc[only_ariba_bool, "Key"].copy()

    # Excel size inc by 1 due to upper/lower
    ariba_create_date_table = prelim_ariba.loc[
        prelim_ariba["Key"].isin(only_ariba_list), ["Final Submit Date", "Key"]
    ]

    ariba_create_date_table = (
        ariba_create_date_table.sort_values("Final Submit Date", ascending=True)
        .groupby("Key")
        .first()
    )

    ariba_create_date_table = ariba_create_date_table.rename(
        columns={"Final Submit Date": "Create Date - Ariba"}
    )

    # If only in Ariba, add Ariba create date, otherwise add Onbase create date.
    data = data.merge(ariba_create_date_table, how="left", on="Key")

    data["Final Create Date"] = pd.NA

    use_ariba_bool = [
        all(t)
        for t in zip(
            data["Final Create Date"].isna(),
            data["In Ariba?"].isin([True]),
        )
    ]
    data.loc[use_ariba_bool, "Final Create Date"] = data.loc[
        use_ariba_bool, "Create Date - Ariba"
    ].copy()

    data = data.dropna(subset=["Key"])

    # Hard Validation 4.2
    val_4_2_bool = data["Final Create Date"].isna()
    if val_4_2_bool.any():
        data.loc[val_4_2_bool].to_csv("test4.2.csv")

    # Hard Validation 4.4
    prob_entries_bool = data["Final Create Date"] > data["Final Approved Date"]
    prob_entries = data.loc[prob_entries_bool]
    updated_ariba_create_table = (
        prelim_ariba.loc[
            prelim_ariba["Key"].isin(prob_entries["Key"]), ["Final Submit Date", "Key"]
        ]
        .sort_values("Final Submit Date", ascending=True)
        .groupby("Key")
        .first()
    )

    for x in updated_ariba_create_table.index:
        data.loc[
            data["Key"] == x, "Final Create Date"
        ] = updated_ariba_create_table.loc[x, "Final Submit Date"]

    val_4_4_bool = data["Final Create Date"] > data["Final Approved Date"]
    if val_4_4_bool.any():
        data.loc[val_4_4_bool].to_csv("test4.4.csv")

    return data.drop(["Create Date - Ariba"], axis=1)


def kpi4_calc_ovr_inv_process_time(data):
    data["Final Create Date"] = pd.to_datetime(
        data["Final Create Date"], format="%Y-%m-%d"
    )

    data["Final Processing Time"] = pd.NA
    data["Final Processing Time"] = (
        pd.to_datetime(data["Final Approved Date"], format="%Y-%m-%d %H:%M:%S")
        - data["Final Create Date"]
    ).dt.days

    # Hard Validation 4.3
    val_4_3_bool = [
        all(t)
        for t in zip(
            data["Final Processing Time"].isna(), data["Final Relevant?"].isin([True])
        )
    ]
    if data.loc[val_4_3_bool].shape[0] > 0:
        data.loc[val_4_3_bool].to_csv("test4.3.csv")

    return data


def kpi4_add_filter_criteria(data):
    prelim_ariba = kpi4_master_ariba_data.loc[
        kpi4_master_ariba_data["Ariba Relevant?"],
        [
            "Invoice Number",
            "Final Supplier",
            "Ariba Relevant?",
            "Direct/Indirect - INVREC",
            "Direct/Indirect - PREREC",
            "Final Company",
            "Invoice Source - INVREC",
            "Invoice Source - PREREC",
        ],
    ].copy()

    prelim_ariba["Key"] = (
        prelim_ariba["Invoice Number"].astype(str)
        + "-"
        + prelim_ariba["Final Supplier"].astype(str)
    )

    data = data.merge(prelim_ariba, how="left", on="Key")

    data["Final Transaction Type"] = data["Direct/Indirect - INVREC"].copy()

    invrec_type_bool = data["Final Transaction Type"].isin(["Direct", "Indirect"])
    data.loc[~invrec_type_bool, "Final Transaction Type"] = data.loc[
        ~invrec_type_bool, "Direct/Indirect - PREREC"
    ]

    # Hard Validation 4.5
    val_4_5_handling = di.import_val_4_5_handling()

    data = data.merge(val_4_5_handling, how="left", on="Key")
    missing_type_bool = data["Final Transaction Type"].isna()
    data.loc[missing_type_bool, "Final Transaction Type"] = data.loc[
        missing_type_bool, "Transaction Type"
    ]

    data = data.drop(["Transaction Type"], axis=1)

    val_4_5_bool = [
        all(t)
        for t in zip(data["Final Transaction Type"].isna(), data["Final Relevant?"])
    ]
    if data.loc[val_4_5_bool].shape[0] > 0:
        data.loc[val_4_5_bool].to_csv("test4.5.csv")

    # Add PO/Non-PO/BPO
    data["PO/Non/BPO?"] = data["Invoice Source - INVREC"].copy()

    data["PO/Non/BPO?"] = data["PO/Non/BPO?"].replace("Sales Order", "Non-PO")
    data["PO/Non/BPO?"] = data["PO/Non/BPO?"].replace("Contract", "Blanket PO")

    data.loc[data["PO/Non/BPO?"].isna(), "PO/Non/BPO?"] = data.loc[
        data["PO/Non/BPO?"].isna(), "Invoice Source - PREREC"
    ]

    # Hard Validation 4.6
    val_4_6_bool = [
        all(t) for t in zip(data["PO/Non/BPO?"].isna(), data["Final Relevant?"])
    ]
    if data.loc[val_4_6_bool].shape[0] > 0:
        data.loc[val_4_6_bool].to_csv("test4.6.csv")

    na_bool = [
        all(t) for t in zip(data["PO/Non/BPO?"].isna(), ~data["Final Relevant?"])
    ]
    data.loc[na_bool, "PO/Non/BPO?"] = "N/A"

    data = data.drop(
        [
            "Invoice Source - PREREC",
            "Invoice Source - INVREC",
            "Direct/Indirect - PREREC",
            "Direct/Indirect - INVREC",
        ],
        axis=1,
    )

    return data


def kpi4_create_ovr_inv_master():
    prelim_ariba = kpi4_master_ariba_data[
        ["Invoice Number", "Final Supplier", "Ariba Relevant?"]
    ].copy()

    prelim_ariba["Key"] = (
        prelim_ariba["Invoice Number"].astype(str)
        + "-"
        + prelim_ariba["Final Supplier"].astype(str)
    )

    data = pd.DataFrame(prelim_ariba["Key"].copy(), columns=["Key"])

    data["In Ariba?"] = data["Key"].isin(prelim_ariba["Key"])

    data = kpi4_add_inv_relevance_master(data, prelim_ariba)

    data = kpi4_determine_master_inv_relevance(data)

    data = kpi4_add_ariba_approved_date(data)

    # Note 12 entries different from excel manual, due to upper/lower
    data = kpi4_add_1st_create_date(data)

    data = kpi4_calc_ovr_inv_process_time(data)

    data = kpi4_add_filter_criteria(data)

    return data


kpi4_master_invoice_data = kpi4_create_ovr_inv_master()

""" Update KPI 3 using KPI 4 calculation """
kpi3_master_ovr_invoice_data = kpi3_master_ovr_invoice_data.merge(
    kpi4_master_invoice_data[["Key", "Final Create Date"]], how="left", on="Key"
)

""" Calculate KPI Trends """


def create_kpi1_trend_data():
    kpi1_relevant_bool = [
        all(t)
        for t in zip(
            kpi1_sl_data["Relevant?"],
            kpi1_sl_data["Company Code"].isin(relevant_company_codes),
        )
    ]
    kpi1_trend_data = kpi1_sl_data.loc[
        kpi1_relevant_bool,
        ["Company Code", "Posting Date", "Transaction Type", "Amount (CoCode Crcy)"],
    ]

    kpi1_trend_table = pd.pivot_table(
        kpi1_trend_data,
        index=[pd.Grouper(freq="ME", key="Posting Date"), "Company Code"],
        columns="Transaction Type",
        values="Amount (CoCode Crcy)",
        aggfunc="count",
    ).reset_index()

    for group, values in company_code_groupings.items():
        relevant_data = kpi1_trend_data.loc[
            kpi1_trend_data["Company Code"].isin(values)
        ]
        if relevant_data.shape[0] == 0:
            continue
        sub_table = pd.pivot_table(
            kpi1_trend_data.loc[kpi1_trend_data["Company Code"].isin(values)],
            index=pd.Grouper(freq="ME", key="Posting Date"),
            columns="Transaction Type",
            values="Amount (CoCode Crcy)",
            aggfunc="count",
        ).reset_index()
        sub_table["Company Code"] = group

        kpi1_trend_table = pd.concat([kpi1_trend_table, sub_table])

    kpi1_trend_table["Target"] = 0.50

    kpi1_trend_table["% Transactions Non-PO"] = kpi1_trend_table["Non-PO"] / (
        kpi1_trend_table["Non-PO"] + kpi1_trend_table["PO"]
    )

    return kpi1_trend_table.to_csv("KPI 1 Trend.csv", index=False)


def create_kpi2_trend_data():
    # We ignore the entries with unclassified company code
    kpi2_relevant_bool = [
        all(t)
        for t in zip(
            kpi2_master_pr_list["Final Company Code"].isin(relevant_company_codes),
            kpi2_master_pr_list["Final Relevant?"],
        )
    ]
    kpi2_trend_data = kpi2_master_pr_list.loc[
        kpi2_relevant_bool,
        ["Final Approved Date", "Final Company Code", "Turnaround (Days)"],
    ]

    kpi2_trend_table = pd.pivot_table(
        kpi2_trend_data,
        index=[pd.Grouper(freq="ME", key="Final Approved Date"), "Final Company Code"],
        values="Turnaround (Days)",
        aggfunc="mean",
    ).reset_index()

    for group, values in company_code_groupings.items():
        sub_table = pd.pivot_table(
            kpi2_trend_data.loc[kpi2_trend_data["Final Company Code"].isin(values)],
            index=pd.Grouper(freq="ME", key="Final Approved Date"),
            values="Turnaround (Days)",
            aggfunc="mean",
        ).reset_index()
        sub_table["Final Company Code"] = group

        kpi2_trend_table = pd.concat([kpi2_trend_table, sub_table])

    kpi2_trend_table["Target"] = 2

    return kpi2_trend_table.to_csv("KPI 2 Trend.csv", index=False)


def create_kpi3_trend_data():
    kpi3_relevant_bool = [
        all(t)
        for t in zip(
            kpi3_master_ovr_invoice_data["Final Company Code"].isin(
                relevant_company_codes
            ),
            kpi3_master_ovr_invoice_data["Final 1st Match"].isin([True, False]),
        )
    ]

    kpi3_trend_data = kpi3_master_ovr_invoice_data.loc[
        kpi3_relevant_bool,
        ["Final Create Date", "Final 1st Match", "Final Company Code", "Key"],
    ]

    kpi3_trend_table = pd.pivot_table(
        kpi3_trend_data,
        index=[pd.Grouper(freq="ME", key="Final Create Date"), "Final Company Code"],
        columns="Final 1st Match",
        values="Key",
        aggfunc="count",
    ).reset_index()

    for group, values in company_code_groupings.items():
        sub_table = pd.pivot_table(
            kpi3_trend_data.loc[kpi3_trend_data["Final Company Code"].isin(values)],
            index=pd.Grouper(freq="ME", key="Final Create Date"),
            columns="Final 1st Match",
            values="Final Company Code",
            aggfunc="count",
        ).reset_index()
        sub_table["Final Company Code"] = group

        kpi3_trend_table = pd.concat([kpi3_trend_table, sub_table])

    kpi3_trend_table["Target"] = 0.80

    kpi3_trend_table = kpi3_trend_table.fillna(0)
    kpi3_trend_table["1st Time Match?"] = kpi3_trend_table[True] / (
        kpi3_trend_table[True] + kpi3_trend_table[False]
    )

    return kpi3_trend_table.to_csv("KPI 3 Trend.csv", index=False)


def create_kpi4_trend_data():
    kpi4_relevant_bool = [
        all(t)
        for t in zip(
            kpi4_master_invoice_data["Final Relevant?"],
            kpi4_master_invoice_data["Final Company"].isin(relevant_company_codes),
        )
    ]

    kpi4_trend_data = kpi4_master_invoice_data.loc[
        kpi4_relevant_bool,
        ["Final Approved Date", "Final Processing Time", "Final Company"],
    ]
    kpi4_trend_data["Final Approved Date"] = pd.to_datetime(
        kpi4_trend_data["Final Approved Date"], format="%Y-%m-%d %H:%M:%S"
    )

    kpi4_trend_table = pd.pivot_table(
        kpi4_trend_data,
        index=[pd.Grouper(freq="ME", key="Final Approved Date"), "Final Company"],
        values="Final Processing Time",
        aggfunc="mean",
    ).reset_index()

    for group, values in company_code_groupings.items():
        sub_table = pd.pivot_table(
            kpi4_trend_data.loc[kpi4_trend_data["Final Company"].isin(values)],
            index=pd.Grouper(freq="ME", key="Final Approved Date"),
            values="Final Processing Time",
            aggfunc="mean",
        ).reset_index()
        sub_table["Final Company"] = group

        kpi4_trend_table = pd.concat([kpi4_trend_table, sub_table])

    kpi4_trend_table["Target"] = 7

    # Overall, Indirect vs Direct, PO vs Non-PO vs BPO
    return kpi4_trend_table.to_csv("KPI 4 Trend.csv", index=False)


create_kpi1_trend_data()
create_kpi2_trend_data()
create_kpi3_trend_data()
create_kpi4_trend_data()

kpi1_sl_data.to_csv("KPI 1 Results.csv")
kpi2_master_pr_list.to_csv("KPI 2 Results.csv")
kpi3_master_ovr_invoice_data.to_csv("KPI 3 Results.csv")
kpi4_master_invoice_data.to_csv("KPI 4 Results.csv")
