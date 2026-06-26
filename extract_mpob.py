import pdfplumber

files = [
    (r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\raw\Palm Oil data\Overview_of_Industry_2017.pdf", 2017),
    (r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\raw\Palm Oil data\Overview_of_Industry_2018.pdf", 2018),
    (r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\raw\Palm Oil data\Overview_of_Industry_2019.pdf", 2019),
    (r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\raw\Palm Oil data\Overview_of_Industry_2020.pdf", 2020),
]

keywords = ['production','extraction','yield','stock','export','planted','area','peninsular','sabah','sarawak','malaysia','oer','ffb','cpo']

for fpath, year in files:
    print(f"\n=== {year} ({fpath.split(chr(92))[-1]}) ===")
    with pdfplumber.open(fpath) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages[:15]):
            text = page.extract_text()
            if text:
                for line in text.split('\n'):
                    low = line.lower()
                    if any(kw in low for kw in keywords):
                        print(f"  p{i+1}: {line.strip()}")
