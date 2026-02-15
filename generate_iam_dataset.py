import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

# ----------------------------
# Constants
# ----------------------------

ASSETS = [
    ("srv-pingfed-01", "10.24.66.14", "Secure Access"),
    ("srv-pingfed-02", "10.24.66.15", "Secure Access"),
    ("idm-sail-01", "10.24.88.18", "Identity Engineering"),
    ("idm-sail-02", "10.24.88.19", "Identity Engineering"),
    ("dir-sync-01", "10.24.90.11", "Directory Management"),
    ("plainid-app-01", "10.24.77.20", "Authorization Team"),
    ("login.auth0.com", "172.19.45.201", "Secure Access"),
    ("mfa-gateway-01", "10.24.66.20", "Secure Access")
]

IAM_THEMES = [
    "MFA push not received",
    "PingID authentication timeout",
    "SailPoint aggregation failure",
    "Directory sync delay",
    "Auth0 login error 401",
    "PlainID authorization denied",
    "High CPU on server",
    "High memory consumption",
    "LDAP connection failure",
    "Provisioning workflow stuck"
]

USERS = [
    "john.doe@company.com",
    "jane.smith@company.com",
    "rita.kapoor@company.com",
    "alex.jones@company.com",
    "mark.brown@company.com",
    "david.lee@company.com"
]

PRIORITIES = [1, 2, 3, 4]
SEVERITIES = ["Critical", "High", "Medium", "Low"]
STATUSES = ["Open", "Resolved", "Closed", "In Progress"]

start_date = datetime(2025, 2, 1)

rows = []

for i in range(1, 221):

    asset_name, ip, group = random.choice(ASSETS)
    theme = random.choice(IAM_THEMES)
    user = random.choice(USERS)

    opened = start_date + timedelta(hours=random.randint(0, 720))
    resolved = opened + timedelta(hours=random.randint(1, 6))
    closed = resolved + timedelta(minutes=random.randint(10, 45))

    description = f"""
    Incident involving {theme}.
    Affected asset: {asset_name}.
    Source IP: {ip}.
    User reported: {user}.
    URL https://{asset_name}/auth returned errors intermittently.
    """

    rows.append({
        "Incident ID": f"INC{100000 + i}",
        "Opened At": opened.strftime("%Y-%m-%d %H:%M:%S"),
        "Short Description": theme,
        "Description": description.strip(),
        "Priority": random.choice(PRIORITIES),
        "Severity": random.choice(SEVERITIES),
        "Status": random.choice(STATUSES),
        "Resolved At": resolved.strftime("%Y-%m-%d %H:%M:%S"),
        "Closed At": closed.strftime("%Y-%m-%d %H:%M:%S"),
        "Assigned To": random.choice(["Alice Morgan", "Rahul Desai", "Meera Iyer", "Daniel Shah"]),
        "Assignment Group": group,
        "Resolution Notes": "Service restarted and logs reviewed.",
        "Category": "IAM",
        "Configuration Item": asset_name,
        "Environment": "Production"
    })

df = pd.DataFrame(rows)

df.to_excel("iam_test_dataset_220.xlsx", index=False)

print("Dataset generated: iam_test_dataset_220.xlsx")
