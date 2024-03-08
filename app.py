import requests
api_key = "AIzaSyDm3NkpUP7s2-9eIctdLS2OZzcYKWnVvXc"
api_url = "https://sheets.googleapis.com/v4/spreadsheets/1SMhSsePT-WJPna2oq5NnE2zyIVSOZycV9kEgkWHcNfs/values/Sheet1!A1:D5?key=" + api_key
response = requests.get(api_url)
print (response)
print('JSON:', response.json())
