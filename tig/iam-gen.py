import requests
import re
import json
import sys

# -------------------------------------------------
# ARGUMENT PARSING
# -------------------------------------------------
if len(sys.argv) not in (2, 3, 4):
    print("Usage: python iam-gen.py <service> [region] [RequestTag]")
    print("Example: python iam-gen.py ec2 eu-central-1 Env=Dev,Prod,QA")
    sys.exit(1)

SERVICE = sys.argv[1].lower()
REGION = sys.argv[2] if len(sys.argv) >= 3 else None

REQUEST_TAG_KEY = None
REQUEST_TAG_VALUES = None

if len(sys.argv) == 4:
    tag_part = sys.argv[3]
    if "=" not in tag_part:
        print("❌ Tag format must be Key=Value1,Value2")
        sys.exit(1)
    REQUEST_TAG_KEY, values = tag_part.split("=", 1)
    REQUEST_TAG_VALUES = values.split(",")

print(f"🔹 Service: {SERVICE}")
if REGION:
    print(f"🔹 Region restriction: {REGION}")
if REQUEST_TAG_KEY:
    print(f"🔹 RequestTag: {REQUEST_TAG_KEY} = {REQUEST_TAG_VALUES}")

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
OWNER = "opentofu"
REPO = "terraform-provider-aws"
BRANCH = "main"

BASE_DIR = f"internal/service/{SERVICE}"
TREE_API = f"https://api.github.com/repos/{OWNER}/{REPO}/git/trees/{BRANCH}?recursive=1"
RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}"
SERVICE_REF_JSON = f"https://servicereference.us-east-1.amazonaws.com/v1/{SERVICE}/{SERVICE}.json"

HEADERS = {"Accept": "application/vnd.github.v3+json"}

# -------------------------------------------------
# FETCH & VALIDATE GITHUB TREE
# -------------------------------------------------
print("🔹 Fetching GitHub repo tree...")
tree_resp = requests.get(TREE_API, headers=HEADERS)
if tree_resp.status_code != 200:
    print("❌ Unable to fetch GitHub tree")
    sys.exit(1)

tree = tree_resp.json()["tree"]

go_files = [
    item["path"]
    for item in tree
    if item["type"] == "blob"
    and item["path"].startswith(BASE_DIR)
    and item["path"].endswith(".go")
    and not item["path"].endswith("_test.go")
]

if not go_files:
    print(f"❌ No Go files found for service '{SERVICE}'")
    sys.exit(1)

print(f"   Go files found: {len(go_files)}")

# -------------------------------------------------
# FETCH & VALIDATE SERVICE REFERENCE
# -------------------------------------------------
print("🔹 Fetching service reference JSON...")
service_resp = requests.get(SERVICE_REF_JSON)
if service_resp.status_code != 200:
    print(f"❌ Service reference not found for '{SERVICE}'")
    sys.exit(1)

service_data = service_resp.json()
if "Actions" not in service_data:
    print("❌ Malformed service reference JSON")
    sys.exit(1)

json_actions = {a["Name"] for a in service_data["Actions"] if "Name" in a}
print(f"   Service reference actions: {len(json_actions)}")

# -------------------------------------------------
# EXTRACT INPUT STRUCTS FROM GO
# -------------------------------------------------
pattern_assign = re.compile(
    r'input\s*:=\s*&?\s*' + re.escape(SERVICE) + r'\.([A-Za-z0-9_]+Input)'
)
pattern_var = re.compile(
    r'var\s+input\s+' + re.escape(SERVICE) + r'\.([A-Za-z0-9_]+Input)'
)

go_functions = set()

print("🔹 Scanning Go files...")
for i, path in enumerate(go_files, 1):
    print(f"   [{i}/{len(go_files)}] {path}")
    raw = requests.get(f"{RAW_BASE}/{path}").text
    matches = pattern_assign.findall(raw) + pattern_var.findall(raw)
    for m in matches:
        go_functions.add(m[:-5])  # strip Input

# -------------------------------------------------
# INTERSECTION
# -------------------------------------------------
common = sorted(go_functions & json_actions)

if not common:
    print("❌ No common functions found")
    sys.exit(1)

print(f"   Common functions: {len(common)}")

# -------------------------------------------------
# READ / WRITE SPLIT
# -------------------------------------------------
READ_PREFIXES = ("Describe", "Get", "List", "Search")

read_ops = []
write_ops = []

for op in common:
    if op.startswith(READ_PREFIXES):
        read_ops.append(op)
    else:
        write_ops.append(op)

# -------------------------------------------------
# EC2 WRITE SPLIT
# -------------------------------------------------
write_server_ops = []
write_network_ops = []

if SERVICE == "ec2":
    SERVER_KEYWORDS = (
        "Instance", "Instances", "Image", "Ami", "Volume",
        "Snapshot", "LaunchTemplate", "Placement", "KeyPair",
        "CapacityReservation", "Host", "Fleet", "Spot"
    )

    for op in write_ops:
        if any(k in op for k in SERVER_KEYWORDS):
            write_server_ops.append(op)
        else:
            write_network_ops.append(op)
else:
    write_network_ops = write_ops

# -------------------------------------------------
# POLICY GENERATOR
# -------------------------------------------------
def write_policy(filename, actions):
    statement = {
        "Effect": "Allow",
        "Action": sorted(f"{SERVICE}:{a}" for a in actions),
        "Resource": "*"
    }

    conditions = {}

    if REGION:
        conditions.setdefault("StringEquals", {})
        conditions["StringEquals"]["aws:RequestedRegion"] = REGION

    if REQUEST_TAG_KEY:
        conditions.setdefault("StringEquals", {})
        conditions["StringEquals"][f"aws:RequestTag/{REQUEST_TAG_KEY}"] = REQUEST_TAG_VALUES

    if conditions:
        statement["Condition"] = conditions

    policy = {
        "Version": "2012-10-17",
        "Statement": [statement]
    }

    with open(filename, "w") as f:
        json.dump(policy, f, indent=4)

    print(f"✅ Wrote {filename} ({len(actions)} actions)")

# -------------------------------------------------
# WRITE POLICIES
# -------------------------------------------------
write_policy(f"{SERVICE}-read.json", read_ops)

if SERVICE == "ec2":
    write_policy(f"{SERVICE}-write-server.json", write_server_ops)
    write_policy(f"{SERVICE}-write-network.json", write_network_ops)
else:
    write_policy(f"{SERVICE}-write.json", write_network_ops)

