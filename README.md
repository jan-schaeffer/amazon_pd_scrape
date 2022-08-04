# Amazon PD Scrape
A Python script to scrape the Amazon Parent Dashboard. Uses Selenium to navigate pages. 

## Features

- Reads login data from  a .csv file
- Uses this data to login to the Amazon Parent Dashboard
- Handles various types of error messages
- Deals with Captchas using TwoCaptcha API
- Deals with OTP authentification by logging into a mail-service, retrieving the OTP and entering it
- Deals with having to verify login by clicking on a link in an Email
- Upon succesfull login it scrapes the Parent Dashboard for the books read on a date and the reading minutes and writes this to .csv
- Writes a log and backup file in case the script fails

## Amazon Parent Dashboard
<img width="778" alt="Amazon Parent Dashboard" src="https://user-images.githubusercontent.com/78418209/182835807-438275e6-ff64-4d4d-a20c-89c63ec6ca31.png">

## Captcha
<img width="451" alt="Captcha" src="https://user-images.githubusercontent.com/78418209/182836882-d5c832f0-c57a-463d-b97a-1aecb5ba599b.png">

## Captcha Retry
<img width="416" alt="Captcha Retry" src="https://user-images.githubusercontent.com/78418209/182836915-ec3bc09e-7886-42c8-a4f5-9ee3075f1210.png">

## Verify Email
<img width="439" alt="Verify Email" src="https://user-images.githubusercontent.com/78418209/182836933-e54fff8a-f487-47bb-9b75-656862f225ac.png">

## Email Link
<img width="588" alt="Email Link" src="https://user-images.githubusercontent.com/78418209/182836984-9cd6bb41-2b8a-479a-9a10-e8d0c73351fe.png">

## Allow Access
<img width="462" alt="Allow Access" src="https://user-images.githubusercontent.com/78418209/182837015-1be1fa94-2a8b-44da-affb-0717ee5c4b48.png">