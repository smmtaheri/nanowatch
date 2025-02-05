import configparser
import datetime
import random

import holidays
import requests

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'


class NanoWatchClient:
    def __init__(self, base_url="https://app.nanowatch.org"):
        """
        Initializes the client with a persistent session.
        """
        self.session = requests.Session()  # Persist cookies between requests.
        self.base_url = base_url.rstrip('/')
        self.tenant_id = None  # Will be set after a successful login/profile call.

    def login(self, email, password):
        """
        Logs in to Nanowatch with the provided credentials.
        Raises an exception if the login fails.
        """
        login_url = f"{self.base_url}/account/login"
        login_headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': self.base_url,
            'Referer': f"{self.base_url}/Account?ReturnUrl=%2F",
            'User-Agent': USER_AGENT
        }
        payload = {
            "email": email,
            "password": password
        }
        response = self.session.post(login_url, json=payload, headers=login_headers)
        if response.status_code != 200:
            raise Exception(f"Login failed!\nStatus Code: {response.status_code}\nResponse: {response.text}")

        result = response.json()
        if not result.get("success", False):
            raise Exception("Login unsuccessful: " + str(result))

        print("Logged in successfully!")
        # Get the profile to extract additional data (like tenantId)
        profile = self.get_profile()
        if profile and "tenantId" in profile:
            self.tenant_id = profile["tenantId"]
        return result

    def get_profile(self):
        """
        Retrieves the logged-in user's profile.
        Returns the JSON profile data.
        """
        profile_url = f"{self.base_url}/api/v2/account/GetMyProfile"
        profile_headers = {
            'Accept': 'application/json, text/plain, */*',
            'Referer': f"{self.base_url}/",
            'User-Agent': USER_AGENT
        }
        response = self.session.get(profile_url, headers=profile_headers)
        if response.status_code != 200:
            raise Exception(f"Get profile failed!\nStatus Code: {response.status_code}\nResponse: {response.text}")
        profile_data = response.json()
        print("Profile retrieved successfully!")
        return profile_data

    def update_user_request(self, request_type, start_datetime, end_datetime,
                            sub_type=0, description="", request_type_id=""):
        """
        Sends a user request update.

        :param request_type: Integer indicating the type of request (e.g., 2 for attendance or 0 for leave).
        :param start_datetime: A datetime object or ISO formatted string for the start time.
        :param end_datetime: A datetime object or ISO formatted string for the end time.
        :param sub_type: Integer subtype (e.g., 0 for entrance/exit, 1 for leave).
        :param description: Description string (e.g., "ورود", "خروج", or "مرخصی روزانه").
        :param request_type_id: Optional string for the request type ID (used in leave requests).
        :return: JSON response from the server.
        """
        update_url = f"{self.base_url}/api/v2/userrequest/update"
        update_headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': self.base_url,
            'Referer': f"{self.base_url}/",
            'User-Agent': USER_AGENT
        }
        # Include tenantId in headers if available.
        if self.tenant_id:
            update_headers['tenantid'] = self.tenant_id

        # Convert datetime objects to ISO strings if needed.
        if isinstance(start_datetime, datetime.datetime):
            start_str = start_datetime.isoformat()
        else:
            start_str = start_datetime
        if isinstance(end_datetime, datetime.datetime):
            end_str = end_datetime.isoformat()
        else:
            end_str = end_datetime

        payload = {
            "type": request_type,
            "requestTypeId": request_type_id,
            "startDateOrTime": start_str,
            "endDateOrTime": end_str,
            "subType": sub_type,
            "description": description
        }
        response = self.session.post(update_url, json=payload, headers=update_headers)
        if response.status_code != 200:
            raise Exception(
                f"Update user request failed!\nStatus Code: {response.status_code}\nResponse: {response.text}")
        return response.json()


def main():
    # Read credentials and exception dates from config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')
    try:
        email = config.get('credentials', 'email')
        password = config.get('credentials', 'password')
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        print("Error reading credentials from config.ini:", e)
        return

    # Read exception days (if any) from the [exceptions] section.
    exception_dates = []
    if config.has_section('exceptions'):
        exceptions_str = config.get('exceptions', 'days', fallback="")
        if exceptions_str:
            try:
                exception_dates = [
                    datetime.datetime.strptime(day.strip(), "%Y-%m-%d").date()
                    for day in exceptions_str.split(',')
                ]
            except ValueError as e:
                print("Error parsing exception dates:", e)
                return

    print("Nanowatch Login")
    client = NanoWatchClient()

    try:
        client.login(email, password)
        profile = client.get_profile()
        print("Your profile:")
        print(profile)
    except Exception as e:
        print("Error during login or profile fetch:", e)
        return

    # Provide a menu for the type of request.
    print("\nChoose the type of request you want to send:")
    print("1: Register Entrance/Exit (Single Attendance Request)")
    print("2: Request One-Day Leave")
    print("3: Bulk Auto-Generate Attendance Requests for a Date Range (Skip Holidays and Exceptions)")
    choice = input("Enter your choice (1, 2, or 3): ").strip()

    if choice == "1":
        print("\n--- Single Attendance Request ---")
        _date = input("Enter datetime (ISO format, e.g., 2025-01-15T10:00:00+03:30): ").strip()
        try:
            result = client.update_user_request(
                request_type=2,  # Type for attendance request.
                start_datetime=_date,
                end_datetime=_date,
                sub_type=0,
                description='',
                request_type_id=''
            )
            print("\nAttendance request result:")
            print(result)
        except Exception as e:
            print("Error updating attendance request:", e)

    elif choice == "2":
        print("\n--- One-Day Leave Request ---")
        # For leave requests, the parameters are predefined.
        start_input = input("Enter leave start datetime (ISO format, e.g., 2025-02-04T00:00:00+03:30): ").strip()
        end_input = input("Enter leave end datetime (ISO format, e.g., 2025-02-05T00:00:00+03:30): ").strip()
        try:
            result = client.update_user_request(
                request_type=0,  # Type for leave request.
                start_datetime=start_input,
                end_datetime=end_input,
                sub_type=1,
                description="مرخصی روزانه",
                request_type_id="2b9a5981-aff8-ec11-a177-005056955182"
            )
            print("\nLeave request result:")
            print(result)
        except Exception as e:
            print("Error updating leave request:", e)

    elif choice == "3":
        print("\n--- Bulk Auto-Generate Attendance Requests ---")
        start_date_input = input("Enter start date (YYYY-MM-DD): ").strip()
        end_date_input = input("Enter end date (YYYY-MM-DD): ").strip()
        try:
            start_date = datetime.datetime.strptime(start_date_input, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_date_input, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return

        # Create an Iran holidays calendar for all years in the range.
        years = list(range(start_date.year, end_date.year + 1))
        iran_holidays = holidays.Iran(years=years)

        current_date = start_date
        delta = datetime.timedelta(days=1)
        while current_date <= end_date:
            # Skip if the day is a Persian weekend (Thursday=3 or Friday=4),
            # if the day is a holiday, or if it is in the exceptions list.
            if (current_date.weekday() in [3, 4] or
                    current_date in iran_holidays or
                    current_date in exception_dates):
                reason = iran_holidays.get(current_date, "Weekend/Exception")
                if current_date in exception_dates:
                    reason = "Exception (Off Work)"
                print(f"Skipping {current_date} ({reason}).")
                current_date += delta
                continue

            # Generate random morning time between 09:00 and 10:45.
            morning_start = 9 * 60  # 9:00 AM in minutes.
            morning_end = 10 * 60 + 45  # 10:45 AM in minutes.
            rand_morning = random.randint(morning_start, morning_end)
            morning_hour = rand_morning // 60
            morning_minute = rand_morning % 60
            morning_time_str = f"{current_date}T{morning_hour:02d}:{morning_minute:02d}:00+03:30"

            # Calculate the lower bound for afternoon time = morning time + 9 hours.
            afternoon_lower = rand_morning + 540  # 9 hours = 540 minutes.
            afternoon_max = 20 * 60  # 20:00 in minutes.
            if afternoon_lower > afternoon_max:
                print(f"Cannot generate afternoon time for {current_date} because morning time is too late.")
                current_date += delta
                continue

            rand_afternoon = random.randint(afternoon_lower, afternoon_max)
            afternoon_hour = rand_afternoon // 60
            afternoon_minute = rand_afternoon % 60
            afternoon_time_str = f"{current_date}T{afternoon_hour:02d}:{afternoon_minute:02d}:00+03:30"

            print(f"\nProcessing date: {current_date}")
            print(f"Generated morning time (ورود): {morning_time_str}")
            print(f"Generated afternoon time (خروج): {afternoon_time_str}")

            # Send morning (entrance) request.
            try:
                result_morning = client.update_user_request(
                    request_type=2,  # Attendance request.
                    start_datetime=morning_time_str,
                    end_datetime=morning_time_str,
                    sub_type=0,
                    description="ورود",
                    request_type_id=""
                )
                print("Morning request result:", result_morning)
            except Exception as e:
                print(f"Error updating morning request for {current_date}: {e}")

            # Send afternoon (exit) request.
            try:
                result_afternoon = client.update_user_request(
                    request_type=2,  # Attendance request.
                    start_datetime=afternoon_time_str,
                    end_datetime=afternoon_time_str,
                    sub_type=0,
                    description="خروج",
                    request_type_id=""
                )
                print("Afternoon request result:", result_afternoon)
            except Exception as e:
                print(f"Error updating afternoon request for {current_date}: {e}")

            current_date += delta
    else:
        print("Invalid choice. Exiting.")


if __name__ == '__main__':
    main()
