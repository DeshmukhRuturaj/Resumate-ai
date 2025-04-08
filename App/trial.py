import requests

url = "https://jsearch.p.rapidapi.com/company-job-salary"

querystring = {"company":"Amazon","job_title":"software developer","location_type":"ANY","years_of_experience":"ALL"}

headers = {
	"x-rapidapi-key": "f11509220amshacdf4a37eb0525bp13b188jsn95e091e6f6f7",
	"x-rapidapi-host": "jsearch.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())