# Medical referral prioritisation streamlining system

## Overview
This project is a FastAPI-AI-based medical referral prioritisation streamlining system that uses AI models to analyze medical cases for the streamlining of referral prioritisation.

## Features
- Registration and authentication of users
- Submission and processing of referrals
- AI-powered referral, referral prioritization and referral prioritisation streamlining(LLaMA, Phi-4, etc.)
- Database persistence (SQLAlchemy)
- Containerisation using Docker for deployment
- Web-based user interface

## Setup

1. **Clone the repository**
2. **Install the dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure API key in environment variables**
   - Identify the .env.example file in the directory and edit out .example from the file name or rename .env.example to .env
   - Obtain and insert your API key/Token to replace GROQ_API_KEY(to test this you would uncomment the complementary aspects of the code accordingly) or GITHUB_TOKEN. I used the Github token which provided a system accuracy of 91.67% utilising the Microsoft Phi-4 model:
     ```eg.
     GROQ_API_KEY=your_groq_api_key
     GITHUB_TOKEN=your_github_token
     SECRET_KEY=your_secret_key
     ```
4. **Run the application locally using**
   ```bash
   uvicorn app:app --reload
   ```
## To see just app without going the Docker route, you can run just the app.py file and access the web interface using `http://localhost:8000`, if you wish to use port 8000 be sure nothing is running on the port or the local host address for your PC or the IP address of your PC or open from the hosting port via Docker desktop.

## Docker Deployment
## Run 1. or 2. below
1. **Docker Compose**
Builds and starts all the services
   ```bash
   docker compose up --build
   ```

2. **Using the Deployment script(deploy.sh)**
   This as well builds and starts all the services
   i. Open the directory in powershell terminal, Git Bash or WSL terminal. 
   ii. Run:
      ```./deploy.sh
   ````
   If on Windows, you can as well use:  
   ```bash ./deploy.sh
   ````
    after opening cloned directory in PowerShell terminal.


## Usage
- Access the web interface using `http://localhost:8000`
- Register/login as a user
- Submit referrals and view the prioritization results

## License
MIT License

# Thank you
