# heliot
Heliot CDSS Pipeline

## Introduction

To setup the Heliot data pipeline, you must procede as follows:

1. Install Python 3.10, if not already installed.
2. Clone the repository: `git clone https://github.com/gadevito/heliot.git`
3. Navigate to the cloned repository directory: `cd /path/to/heliot`
4. Navigate to the pipeline directory: `cd /heliot_pipeline`
5. Install poetry: `pip install poetry`
6. Create a new virtual environment with Python 3.10: `poetry env use python3.10`
7. Activate the virtual environment: `poetry shell`
8. Install app dependencies: `poetry install`
9. Set the required environment variables:

   ```
        export OPENAI_API_KEY=<your_openai_api_key>
        export FARMADATI_ACCESS_KEY=<your_farmadati_api_key>
   ```

### Downloading leaflets
To download leaflets you must have a FARMADATI_ACCESS_KEY and you should run the download_lf script: `poetry run python ./data_pipeline/download_lf.py`.
The script will download le html version of the leaflets in the ./documents directory.

### Extracting a drug subset
To create a drug subset, perform the drug_subset script: : `poetry run python ./data_pipeline/drug_subset.py`. The script will create the drugs_subset.xslx dataset.

### Leaflet processing
In order to extract the leaflet information related to the drug subset, you must run the leaflet_preproc script: `poetry run python ./data_pipeline/leaflet_preproc.py`. It will take a while. Remember that the script exploits GPT-4, so you must have a valid OPENAI API KEY.

### Datasets
In the main folder (`heliot_pipeline`) there are the following datasets:
1. drugs.xslx, the full drug dataset
2. drugs_subset.xslx, the subset of drugs used for the experiment
3. leaflet_info.csv, the processed leaflet info for the drugs_subset dataset
4. ingredients_synonyms.csv, the active ingredients and excipients synonyms for the drugs_subset dataset, extracted from PubChem.
