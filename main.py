# Import modules
import scrapeorder
import login_reader
import password_gen
import amz_login
import foldersetup
from datetime import date
import csv
from datetime import datetime
import os

path = os.getcwd()
today = date.today()


def main():
    foldersetup.setup()
    with open(f"{path}/csv_out/{today}_log.csv", "a", encoding="UTF-8", newline="") as log_csv, \
         open(f"{path}/csv_out/{today}_backup.csv", "a", encoding="UTF-8", newline="") as backup_csv, \
         open(f"{path}/csv_out/{today}_newlogins.csv", "a", encoding="UTF-8", newline="") as newlogins_csv:

        log_writer = csv.writer(log_csv)
        backup_writer = csv.writer(backup_csv)
        newlogins_writer = csv.writer(newlogins_csv)

        time_now = datetime.now().time().strftime("%H:%M:%S")
        print(f"Starting: {time_now}")
        # get scrape order
        scrape_list = scrapeorder.random_order()
        #scrape_list = scrapeorder.sorted_order()

        i = 1
        for username_number in scrape_list:
            log = []
            print(f"#{i} codu_{username_number}")

            # get login data
            try:
                login_data = login_reader.get_logins(username_number)
                time_now = datetime.now().time().strftime("%H:%M:%S")
                log.append(time_now)
                log.append(login_data["imap_user"])
            except Exception:
                log.append(f'{username_number}: no login data found')
                continue

            # generate new password if needed later and add to login
            new_pass = password_gen.gen_password()
            login_data["new_pass"] = new_pass

            # backup passwords
            backup = [time_now, login_data['imap_user'], login_data['imap_pass'],
                      login_data['amz_pass'], login_data['new_pass']]

            backup_writer.writerow(backup)

            # log into amazon
            login_data, log = amz_login.login(login_data, log)
            new_logins = [login_data['imap_user'], login_data['imap_pass'],
                          login_data['amz_pass']]

            try:
                new_logins.append(login_data['amz_pass_old'])
            except Exception:
                pass

            newlogins_writer.writerow(new_logins)

            log_writer.writerow(log)
            i = i+1

    time_now = datetime.now().time().strftime("%H:%M:%S")
    print(f"Finished: {time_now}")

if __name__ == "__main__":
    main()
