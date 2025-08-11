import gspread
from google.oauth2.service_account import Credentials


def google_sheets_shifter():
    # Define the scope
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    # Path to your service account key file
    SERVICE_ACCOUNT_FILE = './shifters-468417-7117f0112d41.json'
    
    # Authenticate and create the client
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    
    # Open the Google Sheet by its URL or name
    spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/18LbkOaBOX9KMU5LqoOwqFkyng-jszlWi4w70taBZOqY/edit?usp=sharing')
    # Alternatively, use: client.open('Your Spreadsheet Name')
    
    # Select the first worksheet
    worksheet = spreadsheet.get_worksheet(0)
    
    # Get all values from the worksheet
    data = worksheet.get_all_values()
    
    shifters = {}
    for row in data:
        if "Monday" in row[0]:
            shifters[1] = [row[1],row[2]]
            #shifters[row[0]] = ";".join(["", row[1],row[2], ""])
        if "Tuesday" in row[0]:                               
            shifters[2] = [row[1],row[2]]
            #shifters[row[0]] = ";".join(["", row[1],row[2], ""])
        if "Wednesday" in row[0]:                             
            shifters[3] = [row[1],row[2]]
            #shifters[row[0]] = ";".join(["", row[1],row[2], ""])
        if "Thursday" in row[0]:                              
            shifters[4] = [row[1],row[2]]
            #shifters[row[0]] = ";".join(["", row[1],row[2], ""])
        if "Friday" in row[0]:                                
            shifters[5] = [row[1],row[2]]
            #shifters[row[0]] = ";".join(["", row[1],row[2], ""])
        if "Satursday" in row[0]:                             
            shifters[6] = [row[1],row[2]]
            #shifters[row[0]] = ";".join(["", row[1],row[2], ""])
        if "Sunday" in row[0]:                                
            shifters[7] = [row[1],row[2]]
            #shifters[row[0]] = ";".join(["", row[1],row[2], ""])
    # Print the data
    #for row in data:
    #    print(row)
    return shifters
    
if __name__ == "__main__":
    shifters = google_sheets_shifter()
    print (shifters)
