# Organizational-Dashboard-Example
 Global Dashboard Example

 This project is to showcare a nearly complete ETL process that takes raw data from multiple source systems (SAP S4 Hana, SAP Ariba, Onbase), cleanses the data, and publishes formatted data ready to be loaded into Power BI. The corresponding Power BI dashboard is also included.

 In this case, it takes 28 files (totalling 298 MB) and applies the necessary business logic to cleanse the data.  All data has been randomized from its original state.  The following lsit of assumptions & validations were put into place to ensure that the data was cleansed appropriately.

    Assumptions
    1.1)  From 7/1/20 - 3/31/22 there's an amount difference of ~$500K between SL & EKBE. Acceptable since overall spend
        of RE types in both files is ~$1B.
    1.2)  Due to BKPF entries being able to span multiple PO #s, any ZH entry types from TPR and supplier is IC1100 is
        auto classified as irrelevant even though mtype is relevant.
    1.3)  Any entries identified by validation 1.6, we assume as direct, if other line items are raw material related,
        otherwise assume indirect.
    1.4)  Any MVI RE Journal Postings, but not in EKBE, assume are non-po.  AP incorrectly posted under RE instead of ZG.
    2.1)  If a PR has all of it's approvals deleted in APR, then it is irrelevant (legacy conversion or customer admin
        deleted)
    2.2)  If a PR is missing from both APR/AHR but in PR or PO & punchout indicator is true, then it was a catalog below
        approval limit.
    2.3)  If a PR is missing from both APR/AHR, is in PR or PO, punchout indicator is false, & supplier is practical tool,
        assume it was a catalog entry.
    2.4)  If a PR is missing from both APR/AHR, is in PR or PO, punchout indicator is false, & supplier is not practical
        tools, assume it is legacy conversion where approval flow deleted.
    2.5)  If a PR has an active approver, then it's irrelevant because we don't care about submitted PRs.
    2.6)  If a PR contains a denial and does not contain any active approvals, then it is a denied PR that was not
        submitted.  Therefore, irrelevant.
    2.7)  If a PR has is both punchout relevant/irrelevant, then it is relevant because there will be an approval flow.
    2.8)  If a PR is in both AHR/APR and not in both PR/PO, then it was a withdrawn or denied PR.
    2.9)  If a PR is in the PO file, then there is a corresponding PO and is relevant.
    2.10) If a PR is in the PR file, and has an EP #, then it is relevant.
    2.11) Approved Date = Unclassified in APR/AHR can be safely ignored because they are due to
        deletions/withdrawls/denials.
    2.12) If PR Approved Date = AHR Approved = APR Approved != PO Ordered, we go with the three because majority is timing
        issue. Some are because extreme delay in system sending approved PO.
    2.13) Only 30 entries where AHR approved date was wrong, so we can live with only AHR entries.
    2.14) Any only AHR entries where missing approved date, assume did not result in successful PO.
    2.15) Submit Date = Unclassified in APR can be safely ignored because they are due to deletions.
    2.16) If entry in AHR has unclassified approved date, but has populated submit date, assume same as 2.14 that no PO
        was successfully created. So we ignore those entries.
    2.17) Assume that for multiple submitted PRs, non-denied, non-catalog PRs, the submit date is latest assigned to buyer.
    2.18) Assume that for multiple submitted PRs, non-denied, catalog PRs, the submit date is latest assigned to supervisor.
    2.19) Assume that for multiple submitted PRs, denied, non-catalog PRs, the submit date is latest assigned to buyer.
    2.20) Assume that for multiple submitted PRs, denied, catalog PRs, the submit date is latest assigned to supervisor
        (too few examples of resubmit for approvals for us to worry about)
    2.21) Assume that if blank Final Submit Date, then it was because it was denied and never resubmitted or was
        originally submitted as a non-catalog, but resubmitted as a catalog.
    2.22) Assume that if there is no approval date in the AHR file after the last denial, then no PO was generated.
    3.1)  Assume that if an entry is only in AH - PRE, then it's a ghost entry & isn't relevant.
    3.2)  Assume that if an entry is only in AH - PRE & APP-PRE, then it's a ghost entry & isn't relevant.
    3.3)  Assume that if an entry is only in APP - PRE, then it's either a ghost entry or non-po that's not relevant.
    3.4)  Assume that any Source Document = Sales Order is non-po related & thus irrelevant.
    3.5)  Any invoice tied to a contract or BPO, despite a source of Purchase Order is not really a PO based invoice.
        Few examples.
    3.6)  Any invoice that has an Invoice Source = Purchase Order, but is not tied to a PO or Contract, was denied and
        should be ignored. (84 entries) They never made it passed the prereconciled stage.
    3.7)  Any entry in Rej-INV was rejected and was not 1st time matched.
    3.8)  Any relevant entry not in INVEXC but in AHINV has people added in the approval flow, not 1st time matched.
    3.9)  Any relevant entry not in INVEXC but in AHPRE was mainly validation errors, not 1st time matched.
    3.10) Any relevant entry not in INVEXC but in APPINV was mainly validation errors, not 1st time matched.
    3.11) Any relevant entry not in INVEXC but in APPPRE had people added to approval flow, not 1st time matched.
    3.12) Any relevant entry only in PREREC, had CC to Invoice/Loaded/Rejected, not 1st time matched (4 entries).
    3.13) Any relevant entry only in INVPAY & PREREC, assume had exceptions, not 1st time matched (4 entries).
    3.14) Any relevant entry in INVEXC, assume had exceptions, not 1st time matched.
    3.15) Any relevant entry only in INVPAY & INVPRO, then it didn't have exceptions, 1st time matched.
    3.16) Any relevant entry only in INVPAY, INVPRO, PREREC & after all fail conditions passed, then assume 1st matched.
    3.17) Any relevant entry only in INVPRO, PREREC & after all prior fail conditions passed, then assume 1st time matched
        (14 entries) Seem to be timing issue in payfile.
    3.18) If Company Code = Purchasing Company = Purchasing Unit, but != Purchasing Org, then pick Company Code.
    3.19) If only Company Code & Purchasing Unit populated and are equal, then pick company code.
    3.20) If only company code populated, then pick that as value.
    3.21) If all company code columns are pouplated & CC = PU & PC = PO, but CC != CC, then pick CC.  Looks like error
        was made at time of invoice submission in selecting the correct code.  We pick the one used at posting.
    3.22) If a doc handle has mutliple entries for invoice types, the correct type is the one with the greater doc id.
    3.23) If a doc handle is missing a inv, then we pick the latest inv form.
    3.24) If a doc handle has greater than 1 cXML/inv/form assumed to fail 1st match.
    3.25) If a doc handle has 0 inv then assumed to fail 1st match.
    3.26) If a doc handle has 1 inv/cXML but 0 form, then assume failed. (48 entries)
    3.27) If a doc handle has 1 inv, but 0 form/cXML, then assume failed. (66 entries)
    3.28) If a document is in Workflow Activity - Adhoc, then it and the corresponding docs do not pass 1st time match.
    3.29) If a document is in Workflow Activity - Trans in a queue other than uploaded to Ariba, then it and the
        corresponding docs fail 1st time match.
    3.30) For doc handles with only a cXML, we automatically classify as irrelevant since we don't know if it's PO related.
    3.31) For Ariba invoices where Company Code is blank, but PU = PO = PC, then pick PC.
    3.32) For Ariba invoices, if only PU populated, then pick that value.
    3.33) If INVPRO has a populated company code, then use it. It should be what was used at the IR level.
    3.34) If an Invoice-Supplier Ariba Key has multiple values for Final Match? Then auto fail.
    3.35) If an Invoice-Supplier Ariba Key has multiple source docs, then auto fail.
    3.36) If an Invoice-Supplier Onbase Key has multiple match values, then auto fail.
    3.37) We use the document date (when form was created, "hit initial"), instead of doc import date (imported into onbase)
        There are entries where blank doc import dates.  For populated values, avg 1.75 day difference.
    3.38) If Ariba invoice is only in Invpay and not in PREREC or INVREC, then it's a duplicate from pay.
    3.39) Impossible to know Ariba Company code if not pouplated either PREREC, INVREC, INVPAY. Assume NA
    3.40) If an Onbase invoice key has multiple entries, but none are successfully uploaded, but has a false,
        default to False.
    3.41) If an Onbase invoice key has multiple entries, but none are successful or unsuccessful, default to TBD.
    3.42) For Ariba invoices, if only the PC/PO ID/PU ID are populated with a company code, then pick the PC value.
    3.43) If an invoice was rejected, and then somehow put into reconciled again.  Assume it's a 0 value and reject it.

    Validations
    1.1)  Check that all EKBE entries have a corresponding company code.
    1.2)  Check that there are 0 EKBE entries with a previously unaccounted for company code.
    1.3)  Check that there are 0 EKBE entries where a new material type was used.
    1.4)  Check that there are 0 EKBE entries where there is a material populated, but no type.
    1.5)  Check that there are 0 EKBE entries not classified as relevant or not.
    1.6)  Check that there are 0 EKBE mat docs that contain both irrelevant/relevant entries.
    1.7)  Check that there are 0 EKBE mat docs that contain multiple date postings.
    1.8)  Check that there are 0 relevant EKBE mat docs that contain mult vendors.
    1.9)  Check that there are 0 entries in SL that have not been accounted for.
    1.10) Check that there are 0 entries in EKBE that do not have a material group description
    1.11) Check that there are 0 SL Journal Entries that have not been encountered before.
    2.1)  Check that there are 0 entries where Relevant 7 (both punchout) has a True value, but Relevant 8
        (withdrawn/denied) has a false value.
    2.2)  Check that there are 0 entries in PO file with multiple Ordered Dates.
    2.3)  Check that there are 0 entries in the APR file with multiple Approved Dates (excluding Unclassified).
    2.4)  Check that there are 0 entries in the AHR file with multiple Approved Dates (excluding Unclassified).
    2.5)  Check that there are 0 relevant entries where we couldn't figure out the appropriate Approved Date source.
    2.6)  Check that there are 0 entries in the Master PR list that has not been flagged for relevancy.
    2.7)  Check that there are 0 entries in the Master PR list that is relevant and doesn't have an approved date.
    2.8)  Check that there are 0 entries in the APR file with multiple submitted dates (excluding unclassified).
    2.9)  Check that there are 0 entries in the AHR file with multiple submitted dates (excluding unclassified).
    2.10) Check that there are 0 non-catalog, non-denied, multiple submission entries in the AHR file without a submitted
        date.
    2.11) Check that there are 0 catalog, non-denied, multiple submission entries in the AHR file without a submitted
        date.
    2.12) Check that there are 0 non-catalog, denied, multiple submission entries in the AHR file without a submitted
        date.
    2.13) Check that there are 0 catalog, denied, multiple submission entries in the AHR file without a submitted
        date.
    2.14) Check that 0 relevant entries do not have a calculated turnaround time.
    2.15) Check for any negative calculated turnaround times, we decide if they are relevant or not.
    3.1)  Check that there are 0 entries in master ariba invoice list that have not been reviewed for relevancy & doesn't
        have an invoice source populated.
    3.2)  Check that there are 0 entries in master ariba invoice list that have not been reviewed for relevancy
    3.3)  Check that there are 0 entries in PREREC that have been classified as both direct/indirect.
    3.4)  Check that there are 0 entries in INVPAY that have been classified as both direct/indirect.
    3.5)  Check that there are 0 relevant entries in Master Ariba Inv List that does not have a invoice type classification.
    3.6)  Check that there are 0 relevant entries in Master Ariba Inv list that does not have a populated match value.
    3.7)  Check that there are 0 relevant entries in Master Ariba Inv List that doesn't have a supplier name.
    3.8)  Check that there are 0 relevant entries in Master Ariba Inv List that doesn't have a submission method.
    3.9)  Check that there are 0 new Workflow Exception Types.
    3.10) Check that there are 0 relevant entries in Master Ariba that doesn't have a company code.
    3.11) Check that there are 0 entries in Master Ariba file that have multiple Source Docs.
    3.12) Check that there are 0 Onbase entries with blank company codes.
    3.13) Check that there are 0 Overall Invoice entries with blank company code.
    3.14) Check that there are 0 PREREC invoices that haven't been classified.
    3.15) Check that there are 0 new IC vendors in PREREC.
    3.16) Check that there are 0 PREREC invoices with multiple direct/indirect
    3.17) Check that there are 0 INVREC invoices that haven't been classified.
    3.18) Check that there are 0 new IC vendors in INVREC
    3.19) Check that there are 0 Ariba invoices with multiple direct/indirect classifications.
    3.20) Check that there are 0 Ariba invoices with undetermined company code.
    3.21) Check that there are 0 Ariba invoices with undetermined Submit Date.
    3.22) Check that there are 0 Ariba invoices with undetermined invoice status.
    3.23) Check that there are 0 Ariba invoices with undetermined Approved Date
    3.24) Check that there are 0 Ariba invoices with multiple suppliers
    3.25) Check that there are 0 Ariba invoices with undetermined supplier.
    3.26) Check that there are 0 Ariba invoices with no submission method.
    4.1)  Check that there are 0 invoices that haven't been classified as relevant.
    4.2)  Check that there are 0 invoices that don't have a final create date.
    4.3)  Check that there are 0 relevant invoices that don't have a calculated processing time.
    4.4)  Check that all create dates are before the approve dates
    4.5)  Check that there are 0 relevant invoices without a direct/indirect classification.
    4.6)  Check that there are 0 relevant invoices without a PO/Non/BPO classification.