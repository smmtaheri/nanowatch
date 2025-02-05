# NanoWatch Automation Tool

This Python script automates attendance requests for the **NanoWatch** system. It allows users to:

- Log in using credentials stored in a configuration file.
- Retrieve their profile information.
- Register single attendance requests.
- Request one-day leave.
- Bulk-generate attendance requests while skipping:
    - Persian weekends (Thursdays & Fridays)
    - Iranian public holidays (based on the Persian calendar)
    - User-defined off days (specified in config.ini)

## 📌 Features

- Login and session management using credentials from config.ini.
- Retrieve user profile.
- Submit a single attendance request.
- Submit a one-day leave request.
- Bulk auto-generate attendance requests for a date range.
- Automatically skip weekends, public holidays, and manually specified off days.

## ⚙️ Installation

### 1️⃣ Install Dependencies

Install required packages using **Poetry**:

    poetry add requests configparser holidays

Alternatively, you can install via pip:

    pip install requests configparser holidays

### 2️⃣ Configure Your Credentials

Before running the script, create a file named `config.ini` in the same directory as the script with the following
content:

    [credentials]
    email = your-email-or-phone
    password = your-password

    [exceptions]
    # Specify off-work days in YYYY-MM-DD format (comma-separated)
    days = 2025-01-20, 2025-01-25

- The script automatically reads the email and password from this file.
- The `[exceptions]` section allows you to exclude specific days from bulk attendance generation.

## 🚀 Usage

After installing dependencies and configuring `config.ini`, you can run the script using **Poetry**:

    poetry run python nanowatch.py

Once the script starts, you will see a menu like this:

    Nanowatch Login
    Your profile: {user details}

    Choose the type of request you want to send:
    1: Register Entrance/Exit (Single Attendance Request)
    2: Request One-Day Leave
    3: Bulk Auto-Generate Attendance Requests for a Date Range (Skip Holidays and Exceptions)
    Enter your choice (1, 2, or 3):

## 📜 Menu Options

Once the script starts, you will see the following menu:

    Nanowatch Login
    Your profile: {user details}

    Choose the type of request you want to send:
    1: Register Entrance/Exit (Single Attendance Request)
    2: Request One-Day Leave
    3: Bulk Auto-Generate Attendance Requests for a Date Range (Skip Holidays and Exceptions)
    Enter your choice (1, 2, or 3):

### 🏷️ Option 1 - Register a Single Attendance Request

- **Description:** Manually enter a specific date and time for an attendance request (either entry or exit).
- **Behavior:** The system will send an attendance request for the exact date and time provided.

Example Input:

    Enter datetime (ISO format, e.g., 2025-01-15T10:00:00+03:30):

---

### 🏷️ Option 2 - Request One-Day Leave

- **Description:** Manually enter a leave start and end date.
- **Behavior:** The system will send a leave request for the specified date range.

Example Input:

    Enter leave start datetime (ISO format, e.g., 2025-02-04T00:00:00+03:30):
    Enter leave end datetime (ISO format, e.g., 2025-02-05T00:00:00+03:30):

---

### 🏷️ Option 3 - Bulk Auto-Generate Attendance Requests

- **Description:** The system will ask for a start and end date and automatically generate two attendance requests per
  working day (one for arrival and one for exit).
- **Exclusions:** Days will be skipped if they are:
    - Persian weekends (Thursdays & Fridays)
    - Public holidays in Iran
    - Manually specified off days listed in config.ini under [exceptions]

Example Input:

    Enter start date (YYYY-MM-DD): 2025-01-01
    Enter end date (YYYY-MM-DD): 2025-01-31

**How Attendance is Generated:**

- **Morning Entrance:** A random time between 09:00 and 10:45 is generated.
- **Afternoon Exit:** A random time at least 9 hours after the morning entrance (but before 20:00) is generated.

Example Output:

    Skipping 2025-01-04 (Friday - Weekend).
    Skipping 2025-01-06 (National Holiday).
    Skipping 2025-01-20 (Exception - Off Work).
    Processing date: 2025-01-07
    Generated morning time (ورود): 2025-01-07T09:30:00+03:30
    Generated afternoon time (خروج): 2025-01-07T19:10:00+03:30
    Morning request result: {API response}
    Afternoon request result: {API response}

## 🏗️ How It Works

1. **Login & Session Management**
    - Reads credentials from config.ini.
    - Authenticates with the NanoWatch API.
    - Stores the session for further requests.

2. **Profile Retrieval**
    - Fetches user profile details after login.

3. **Attendance Request Submission**
    - Option 1: Submit a single attendance request with a manually specified date and time.
    - Option 2: Submit a one-day leave request for a specific date range.
    - Option 3: Bulk auto-generate attendance requests for a range of dates, automatically skipping weekends, public
      holidays, and specified off days.

## 🔥 Example API Responses

**Successful Attendance Request:**

    {
        "success": true,
        "code": 0
    }

**Successful Leave Request:**

    {
        "status": "approved",
        "message": "Leave request submitted successfully."
    }

**Error Example (Invalid Credentials):**

    {
        "success": false,
        "error": "Invalid username or password"
    }

## 📜 License

This project is licensed under the MIT License.

## 📩 Contact

For issues, feature requests, or contributions, please open an issue or contact the maintainer.
