# Book sorter, takes in a book's isbn, gets data about the book from google books API, stores the book data in a google sheet 
import re
import requests
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def isIsbn(isbn):
    # Checks the validity of the input isbn by matching the regular expression and then by evaluating the checksum algorithm
    isbn_regex = re.compile("^(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]$")

    if isbn_regex.search(isbn):
        # Remove non ISBN digits, then split into a list
        chars = list(re.sub("[- ]|^ISBN(?:-1[03])?:?", "", isbn))
        # Remove the final ISBN digit from `chars`, and assign it to `last`
        last = chars.pop()
    
        if len(chars) == 9:
            # Compute the ISBN-10 check digit
            val = sum((x + 2) * int(y) for x,y in enumerate(reversed(chars)))
            check = 11 - (val % 11)
            if check == 10:
                check = "X"
            elif check == 11:
                check = "0"
        else:
            # Compute the ISBN-13 check digit
            val = sum((x % 2 * 2 + 1) * int(y) for x,y in enumerate(chars))
            check = 10 - (val % 10)
            if check == 10:
                check = "0"

        if (str(check) == last):
            print("Valid ISBN")
            return True
        else:
            print("Invalid ISBN check digit")
    else:
        print("Invalid ISBN")
    return False


def insertBook(base_url, sheet, isbn):
    response = requests.get(base_url+isbn)
    parsed = response.json()
    title = parsed["items"][0]["volumeInfo"]["title"]
    author = parsed["items"][0]["volumeInfo"]["authors"][0]
    publisher = parsed["items"][0]["volumeInfo"]["publisher"] if "publisher" in parsed["items"][0]["volumeInfo"] else ""
    published_date = parsed["items"][0]["volumeInfo"]["publishedDate"] if "publishedDate" in parsed["items"][0]["volumeInfo"] else ""
    page_count = parsed["items"][0]["volumeInfo"]["pageCount"] if "pageCount" in parsed["items"][0]["volumeInfo"] else ""
    book_info = [title, author, publisher, published_date, page_count, isbn]
    sheet.append_row(book_info)
    print("Inserted new book! Isbn: ", isbn, " Book data: ", book_info)

def main():

    base_url = "https://www.googleapis.com/books/v1/volumes?q=isbn:"

    scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
            ]

    credentials = ServiceAccountCredentials.from_json_keyfile_name('booksorter-358814-9c55cc04276b.json', scopes)

    file = gspread.authorize(credentials)
    sheet = file.open('Libri')
    sheet = sheet.sheet1

    with open("isbn.txt") as fp:
        for isbn in fp:
            if (isIsbn(isbn.strip())):
                insertBook(base_url, sheet, isbn.strip())
            else:
                print(isbn, " non è un isbn valido!")


if __name__ == "__main__":
    main()
