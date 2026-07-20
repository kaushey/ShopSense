# ShopSense

 > ## Installation
 clone this repository 

- open in any text editor 
-  `cd SohopSense`
> ## 1. Web application

### a. backend
1. `cd backend`

2. create a virtual environment
- `python -m venv env`

for linux / MacOS
- `source env/bin/activate`
for windows
- `.\env\Scripts\activate`

- `pip install -r requirements.txt`
3. make a .env file in /backend
> ### Database Configuration

This project utilizes a PostgreSQL database. Below are the necessary credentials and configuration details provided by Render:

- *Database Host*: dbhost
- *Database Username*: dbusername
- *Database Password*: dbpassword
- *Database Name*: dbname

### AWS Configuration

The project also requires AWS credentials for accessing various AWS services. Below are the necessary details provided by the AWS website:

- *AWS Access Key*: your_aws_access_key
- *AWS Secret Key*: your_aws_secret_key
- *S3 Bucket Name*: your_bucket_name
- *Region*: your_aws_region

### Google Cloud Configuration

The project also requires Google Cloud credentials for accessing Google Cloud services. Below are the necessary details provided by the Google Cloud Console:

- *Google Cloud Client ID*: your_google_cloud_client_id
- *Google Cloud Client Secret*: your_google_cloud_client_secret

- add all these keys into .env file.



4. `uvicorn main:app --reload`


### b. frontend
- `cd frontend`
- `npm install`
- `npm start`


### Home page
![Home](/frontend/public/home.png)
### Text Search
![Text Search](/frontend/public/text.png)
### Image Search
![Image Search](/frontend/public/image.png)
### Video Search
![Video Search](/frontend/public/video.png)

