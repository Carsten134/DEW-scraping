import sys
import pandas as pd
import json
import os
from scraper.x import XScraper
from loaders.XLoader import XDataLoader
"""
This file is the entrypoint for a new docker container
and therefore the highest level of abstraction for this programm.
"""


RUN_JSON_X_DIR = "./project/scraper/run-configs/"

def main(social_media:str, run_config:str, download_dir:str, data_dir:str, data_name:str) -> None:
  """
  Main function for scraping meant for a describe the high level behaviour.

  Parameters:
    social_media(str): What social media to scrape, possible values are "X" | "Spiegel"
    run_config(str): Name of the run config
    download_dir(str): Specifies the absolute download path (where the raw zeeschuimer files are saved)
    data_dir(str): Specifies the absolute path to where you want the csvs to be saved to
    data_name(str): Name of the csv
  """
  if social_media == "Spiegel":
    # start and run spiegel scraper agent
    print("spiegel scraper is not implemented yet")

  elif social_media == "X":
    with open(RUN_JSON_X_DIR + run_config + ".json") as f:
      run_json = json.load(f)
    
    # run scraping
    x = XScraper(run_json)
    x.run()

    # process and save data
    loader = XDataLoader(download_dir)
    loader.process_raw_data()
    loader.save_to_csv(data_dir + "/"+ data_name + ".csv")
  
  else:
    raise RuntimeError(f"Passed mode {social_media} does not belong to any agent. Make sure to use one of 'X'| 'Spiegel'")
    
if __name__ == "__main__":
  social_media = input("Kind of social media to scrape['X'| 'Spiegel']")
  run_config = input("Name of run config:")
  download_dir = input("Absolute download path of host machine:")
  data_dir = input("Absolute path to folder, data is saved:")
  data_name = input("Name of the csv:")
  main(social_media, run_config, download_dir, data_dir, data_name)
