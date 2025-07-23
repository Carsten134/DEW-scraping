# X and Spiegel Scraper
This repository is part of the project ["Diskurs Energiewende"](https://jonasrieger.github.io/2024/09/03/bmwk.html) and provides code for scraping posts from social media related to the energy transition and social inequality.

## Setup
To run this setup you will need to install the requirements. For this navigate to the project:

On windows run from the root directory
```
python venv -m .venv
.venv\Scripts\activate.bat

cd project
pip install -r requirements.txt
```

Then navigate back to the root directory and run :
```
python project\main.py X | Spiegel
```
Where `X | Spiegel` are the optional social media platforms available for scraping. You can then follow the setup guide. Please note, that you will have to setup a configuration file first. More on this in the next section. 


## Configuring your scraper
The scraping behavior can be configured via a json file. Here is an example for a `run.json`
```
{
  "user": {
    "name": "...",
    "mail": "...",
    "password": "..."
  },
  "searchTerms": [
    "Birthday"
  ],
  "timeBins": [
    "2020-01-01",
    "2021-01-01"
  ],
  "additionalQuery": "lang:de AND -is:quote",
  "scrollsPerSearch": 3,
  "scrollsOffset": 500,
  "secBetweenScrolls": 1,
  "secAfterScrolls": 5,
  "fallbacks": {
    "429": {
      "secWaiting": 30,
      "tries": 2
    }
  },
  "log": {
    "fileName": "test_log"
  }
}
```
Are more detailed guide can be found [here](./project/scraper/run-configs).