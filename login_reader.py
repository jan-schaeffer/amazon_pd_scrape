import csv
import os
path = os.getcwd()


def get_logins(username_number):
    with open(f"{path}/csv_in/logins.csv") as csvin:
        logins = csv.reader(csvin)

        for row in logins:
            username = row[0].strip()
            read_number = int(username.split('_')[1])

            if username_number != read_number:
                continue
            elif username_number == read_number:
                amz_user = (f"{username}@uni-potsdam.de")
                imap_pass = row[1].strip()
                amz_pass = row[2].strip()
                imap_user = username
                break

    logins = {"amz_user": amz_user, "amz_pass": amz_pass,
              "imap_user": imap_user, "imap_pass": imap_pass}

    return logins
