# Paragon Property Management System (PAMS)

A multi-role property management desktop application built with Python and Flet.
Developed as part of the Software Development Group Project (SDGP) at UWE Bristol.

---

## Roles

| Role | Capabilities |
|------|-------------|
| **Administrator** | Broadcast notifications, manage staff accounts, manage apartments & leases |
| **Front Desk Staff** | Approve tenants, assign apartments, manage parcels & maintenance requests |
| **Tenant** | View lease, submit maintenance requests, make payments, view notifications |
| **Maintenance Staff** | View and resolve assigned work orders |
| **Finance Manager** | Manage invoices, run monthly billing, generate VAT reports |
| **Manager** | View occupancy & financial analytics across all branch locations |

---

## Prerequisites

- Python 3.10 or higher
- MySQL Server 9.0 or higher
- pip

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Lahiru-Malshan/Systems-Developemt-Group-Project_25
cd Systems-Developemt-Group-Project
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the database

Import the provided SQL dump into MySQL:

```bash
mysql -u root -p -e "CREATE DATABASE paragon_db;"
mysql -u root -p paragon_db < Database/paragon_db.sql
```

Or use MySQL Workbench:
- **Server → Data Import → Import from Self-Contained File**
- Select `Database/paragon_db.sql`, target schema: `paragon_db`

### 4. Configure environment variables

Copy the example env file and fill in your MySQL credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=paragon_db
DEFAULT_STAFF_LOCATION_ID=1
```

---

## Run the app

```bash
python src/main.py
```

Or using the Flet CLI:

```bash
flet run src/main.py
```

---

## Login credentials

### Staff accounts
Staff accounts are created by the Administrator inside the system.

| Field | Format |
|-------|--------|
| Username | NI number (lowercase, alphanumeric only) |
| Password | `Paragon@` + last 4 characters of NI number |

**Example:** NI = `AB123456C` → username: `ab123456c`, password: `Paragon@456C`

### Tenant accounts
Tenants register themselves from the login screen.
Accounts start as **Inactive** and must be approved by Front Desk before login is allowed.

---

## Project structure

```
SDGP_Project/
├── src/
│   ├── main.py                      Entry point
│   ├── db.py                        All database queries
│   ├── login.py                     Authentication logic
│   ├── register.py                  Tenant registration
│   ├── pwhash.py                    Password hashing (bcrypt)
│   ├── backend/
│   │   ├── FrontDesk/frontdesk.py   Front Desk backend
│   │   ├── Maintance/               Maintenance backend
│   │   └── Tenant/tenant.py         Tenant backend
│   ├── logic/
│   │   ├── notifications.py         Notification system
│   │   └── search.py                Search/filter engine
│   └── ui/
│       ├── Administrator/           Admin dashboards
│       ├── Finance/                 Finance dashboards
│       ├── FrontDesk/               Front Desk dashboards
│       ├── Maintenance/             Maintenance dashboards
│       ├── Manager/                 Manager dashboards
│       ├── Tenant/                  Tenant dashboards
│       ├── base_dashboard.py        Shared base UI class
│       ├── login_dashboard.py       Login screen
│       └── register_dashboard.py    Registration screen
├── Database/
│   ├── paragon_db.sql               MySQL database dump
│   └── ER Diagram.pdf               Entity-relationship diagram
├── .env.example                     Environment variable template
├── requirements.txt                 Python dependencies
└── SETUP.txt                        Full setup guide
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `flet` | 0.80.5 | Desktop UI framework |
| `flet-charts` | 0.80.5 | Charts and graphs |
| `mysql-connector-python` | 9.6.0 | MySQL database connection |
| `bcrypt` | 5.0.0 | Password hashing |
| `python-dotenv` | 1.2.2 | Environment variable loading |

---

## Notes

- The `.env` file is ignored by git and must be created locally before running.
- If `.env` was accidentally committed, remove it from tracking with:
  ```bash
  git rm --cached .env
  ```
- Do not include the `build/` folder or any virtual environment in the submission ZIP.
