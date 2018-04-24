import requests

apiAddress = "https://antistorm.eu/ajaxPaths.php?lastTimestamp=0&type=radar"
apiResponse = requests.get(apiAddress)
content = apiResponse.content

chunks = content.split("<br>")

print chunks[1]
