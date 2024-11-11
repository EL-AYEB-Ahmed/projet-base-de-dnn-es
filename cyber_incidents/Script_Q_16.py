import requests

#ATTENTION: bien lancer app.py dans un terminal dédié avant de lancer cette fonction

# Define the URL for the GET request
url = "http://127.0.0.1:5000/agents/"

try:
    # Make the GET request
    response = requests.get(url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Print the JSON response if available
        print("Response JSON:", response.json())
    else:
        # Print an error message if the request was not successful
        print("Error: Received response code", response.status_code)

except requests.exceptions.RequestException as e:
    # Print any exceptions that occur during the request
    print("An error occurred:", e)

    