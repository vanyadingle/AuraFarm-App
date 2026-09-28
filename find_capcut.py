import os
import glob

localappdata = os.environ.get("LOCALAPPDATA", "")
appdata = os.environ.get("APPDATA", "")
userprofile = os.environ.get("USERPROFILE", "")

check_dirs = [
    os.path.join(localappdata, "CapCut"),
    os.path.join(localappdata, "CapCut", "User Data", "Projects", "com.lveditor.draft"),
    os.path.join(userprofile, "Videos", "CapCut"),
    os.path.join(userprofile, "Movies", "CapCut"),
    os.path.join(os.environ.get("ProgramFiles", ""), "CapCut"),
    os.path.join(os.environ.get("ProgramFiles(x86)", ""), "CapCut"),
]

for d in check_dirs:
    exists = os.path.exists(d)
    print(f"[{'FOUND' if exists else 'NOT FOUND'}] {d}")
    if exists:
        try:
            items = os.listdir(d)
            print(f"   Contents ({len(items)}): {items[:5]}")
        except Exception as e:
            print(f"   Error reading: {e}")

# Search for draft_content.json anywhere in localappdata/CapCut
if os.path.exists(os.path.join(localappdata, "CapCut")):
    print("\nSearching for CapCut drafts in LocalAppData...")
    drafts = glob.glob(os.path.join(localappdata, "CapCut", "**", "draft_content.json"), recursive=True)
    print(f"Found {len(drafts)} drafts:")
    for df in drafts[:5]:
        print(" -", df)
