from datetime import date
from datetime import datetime
from datetime import timedelta
import os
import csv
from bs4 import BeautifulSoup

path = os.getcwd()
today = date.today()


def scrape(driver, login_data, kid_name):
    print('scraping')
    username = login_data['imap_user']
    with open(f"{path}/csv_out/{today}_scrape.csv", "a", encoding="UTF-8-SIG", newline="") as scrape_csv:
        scrape_writer = csv.writer(scrape_csv)
        # get all day cards into the programm
        dashboard_soup = BeautifulSoup(driver.page_source, "lxml")
        days = dashboard_soup.find_all("div", class_="activity-day-header pd-margin-bottom pd-margin-top")
        # get time for output
        time_now = datetime.now().time().strftime("%H:%M:%S")
        if len(days) > 0:
            # loop over all days found in order to retrieve books and reading minutes
            for day in days:  # first loop level: days

                # initalize output list
                scrape_csv_line = [username, today, time_now]

                # find date
                date_scraped = day.find("div", class_="activity-day-date").text

                # transform date and append to output list
                date_out = transform_date(today, date_scraped)
                scrape_csv_line.append(date_out)

                # run find_books function, returns list of books read on that date, append to output list
                books_list = find_books(day)
                scrape_csv_line = scrape_csv_line + books_list
                scrape_writer.writerow(scrape_csv_line)

        else:
            scrape_csv_line = [username, today, time_now, 'no activity']
            scrape_writer.writerow(scrape_csv_line)



def find_books(day):
    # first we need to zero in on the books read only on a specific date
    # .parent methods tells BS to use the <div> encompassing the date as well as the
    # books read on that date, thus not reading in all books ("activity-list-item"s)
    # found on the page
    books_soup = day.parent

    # get all book cards from a day
    book_cards = books_soup.find_all("div", class_="activity-list-item")

    # get book titles and reading minutes and save them in a list
    book_list = []
    for book in book_cards:  # second loop level: books
        # get the book title
        book_title = book.find("p", class_="css-lz9wxf")
        book_list.append(book_title.text.replace(';', ','))
        # get the reading minutes
        reading_minutes = book.find("p", class_="css-1iyaudq activity-detail-card-time-label").text.replace("Min.", "")
        # replace reading minutes with 0 if there is no value on the page
        if reading_minutes == "":
            reading_minutes = "0"
        # convert reading hours to minutes if needed
        elif "Std." in reading_minutes:
            reading_minutes = reading_minutes.split('Std.')
            hours = int(reading_minutes[0].strip())
            if reading_minutes[1] != ' ':
                minutes = int(reading_minutes[1].strip())
            else:
                minutes = 0
            reading_minutes = 60*hours + minutes
        # in all other cases, just take the reading minutes from the page
        else:
            reading_minutes = int(reading_minutes)
        book_list.append(reading_minutes)

    return book_list


def transform_date(created, date_scraped):

    weekdays_eng = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekdays_ger = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    months = ["", "Jan.", "Feb.", "März", "Apr.", "Mai", "Juni", "Juli", "Aug.", "Sep.", "Okt.", "Nov.", "Dez."]

    # convert date for today
    if date_scraped == "Heute":
        date_out = created
        date_out = date_out.strftime("%Y-%m-%d")
    # convert date for yesterday
    elif date_scraped == "Gestern":
        date_out = created - timedelta(days=1)
        date_out = date_out.strftime('%Y-%m-%d')
    # convert dates for last couple days (coded as weekdays)
    elif date_scraped in weekdays_ger:
        # translate weekday from German to English (needed for conversion)
        weekday_translated = weekdays_eng[weekdays_ger.index(date_scraped)]
        # get the indices for creation weekday and scraped weekday
        index_date_scraped = weekdays_eng.index(weekday_translated)
        weekday_created = created.strftime("%A")
        index_date_created = weekdays_eng.index(weekday_created)
        # calculate difference in weekdays
        delta_weekdays = index_date_created - index_date_scraped
        # if this is negative (e.g. creation date=monday 18.7., scraped date = wednesday 13.7. -> 1-3 = -2) add 7 
        # (-2 = 7 = 5 which is the actual difference in days between the 13.7. and 18.7.) 
        if delta_weekdays < 0:
            delta_weekdays = delta_weekdays + 7
        # substract the time delta from creation date to get the activity date  (date scraped)
        date_out = created - timedelta(days=delta_weekdays)
        date_out = date_out.strftime('%Y-%m-%d')
    # for all other cases, convert the scraped date (string) to the yyyy-mm-dd scheme
    elif date_scraped.find("202"):
        date_list = date_scraped.split(" ")
        day = date_list[0].strip('.')
        month = date_list[1].strip()
        month = months.index(month)
        year = date_list[2].strip()
        date_out = (f"{year}-{month}-{day}")

    return date_out
