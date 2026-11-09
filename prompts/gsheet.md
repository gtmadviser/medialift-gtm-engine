# Google Sheet: turn a list into a tracker the team actually works

A list in a CSV dies. A shared sheet with a status column gets worked. Use this after any skill that produces a list: the network shortlist, accounts, partners, leads.

## What a good tracker has

- **One row per person or organisation**, the columns from the source list, and these five added: `status`, `owner`, `next_step`, `last_contact`, `notes`.
- **Status values:** to contact, contacted, replied, meeting, pilot, won, not now. Nothing else, so it can be counted.
- **One owner per row.** A name, not "team".
- **A summary tab** with a count per status. That is the pipeline.

## Path A: the agent has Google access

If a Google Drive or Google Sheets connector, or the `gws` or `gcloud` CLI, is available in this session:

1. Ask the founder for the list to use (default: `output/network_shortlist.csv`) and the sheet name.
2. Create the spreadsheet in **their** Drive with a tab `Tracker` (the rows, header frozen, filter on, `status` as a dropdown with the seven values) and a tab `Summary` (count per status with `COUNTIF`).
3. Leave it private. Sharing is the founder's decision. Give them the link.

Check that you really have write access before you promise this. If not, use Path B and say so.

## Path B: no Google access (works everywhere, about one minute)

```bash
python3 scripts/sheet_export.py                         # the network shortlist
python3 scripts/sheet_export.py output/accounts.csv     # or any other list
python3 scripts/sheet_export.py --owner Anna            # pre-fill the owner
```

Then tell the founder:
1. Open **https://sheets.new**
2. **File → Import → Upload** and pick the file from `output/sheets/`
3. Choose **Replace spreadsheet**, separator **Detect automatically**
4. Select the `status` column → **Data → Data validation → Dropdown** with the seven values
5. **View → Freeze → 1 row**, then **Data → Create a filter**

Offer this formula block for a `Summary` tab (assumes the tracker tab is called `Tracker` and status is column A):

```
to contact   =COUNTIF(Tracker!A:A,"to contact")
contacted    =COUNTIF(Tracker!A:A,"contacted")
replied      =COUNTIF(Tracker!A:A,"replied")
meeting      =COUNTIF(Tracker!A:A,"meeting")
pilot        =COUNTIF(Tracker!A:A,"pilot")
won          =COUNTIF(Tracker!A:A,"won")
```

## Guardrails

- A sheet with names of real people is personal data. Keep it private or shared with co-founders only, never "anyone with the link".
- The sheet is the working copy from now on. If the founder changes the ICP, regenerate the shortlist, but do not overwrite a sheet that already has status entries. Add new rows instead.
