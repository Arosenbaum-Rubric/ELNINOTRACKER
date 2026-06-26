import json, os

PROC_DIR = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\processed"
path = os.path.join(PROC_DIR, "pipeline_output.json")

assert os.path.exists(path), "pipeline_output.json NOT FOUND"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

print("1. pipeline_output.json: EXISTS and VALID JSON")
print(f"   Top-level keys: {list(data.keys())}")
print()

print("2. First 5 rows of countryProd.civ:")
for row in data["countryProd"]["civ"][:5]:
    print(f"   {row}")
print()

print("3. grindingsTrajectory:")
for row in data["grindingsTrajectory"]:
    print(f"   {row}")
print()

summary = data["step6Summary"]
lines = summary.split("\n")
print("4. step6Summary — header + CIV section (first 40 lines):")
for line in lines[:40]:
    print(f"   {line}")
print(f"   ... ({len(lines)} total lines in step6Summary)")
