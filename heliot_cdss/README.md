# heliot
Heliot CDSS


## Introduction

To setup the Heliot data pipeline, you must procede as follows:

1. Install Python 3.10, if not already installed.
2. Clone the repository: `git clone https://github.com/gadevito/heliot.git`
3. Navigate to the cloned repository directory: `cd /path/to/heliot`
4. Navigate to the pipeline directory: `cd /heliot_cdss`
5. Install poetry: `pip install poetry`
6. Create a new virtual environment with Python 3.10: `poetry env use python3.10`
7. Activate the virtual environment: `poetry shell`
8. Install app dependencies: `poetry install`
9. Set the required environment variables:

   ```
        export OPENAI_API_KEY=<your_openai_api_key>
   ```

### Run the API SERVER
In order to run the Heliot API server, you must run the launch script: `poetry run python -m cdss.heliot.api.main`

### Run the Heliot Web Application
To run the Heliot web Application, simply run: `poetry run streamlit run ./cdss/heliot/app/webapp.py`

### Datasets
In the main folder (`heliot_cdss`) there are the following datasets:
1. patients_synthetic.xslx, the synthetic dataset used for the expertiments
2. results_full_synth.xslx, the results produced by the Heliot CDSS analyzing the synthetic dataset 
