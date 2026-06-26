import pdfplumber

files = [
    (r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\raw\Palm Oil data\Overview_of_Industry_2017.pdf", 2017),
    (r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\raw\Palm Oil data\Overview_of_Industry_2018.pdf", 2018),
    (r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\raw\Palm Oil data\Overview_of_Industry_2019.pdf", 2019),
    (r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\raw\Palm Oil data\Overview_of_Industry_2020.pdf", 2020),
]

# Print all text from pages 5-6 (the summary tables)
for fpath, year in files:
    print(f"\n=== {year} FULL TABLE PAGES ===")
    with pdfplumber.open(fpath) as pdf:
        for i in [4, 5]:  # pages 5 and 6 (0-indexed)
            page = pdf.pages[i]
            text = page.extract_text()
            if text:
                print(f"--- Page {i+1} ---")
                print(text)
            # Also try extracting tables
            tables = page.extract_tables()
            if tables:
                for t_idx, table in enumerate(tables):
                    print(f"  TABLE {t_idx}:")
                    for row in table:
                        print(f"    {row}")
