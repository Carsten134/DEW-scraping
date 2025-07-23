## Configuring the X Scraper with a JSON File
This part of the repository is responsible for configuring the scrapers behaviour.

### `user`
Configures the used user credentials for authenticating to X.

Example for the user:
```
"user": {
  "name": "your_user_name",
  "mail": "youremail@mail.net",
  "password": "yourpassword"
}
```


### `searchTerms`
Keywords the scraper should search for. For example, this code snipplet searches for holyday:
```
"searchTerms": ["birthday", "holyday", "eastern"]

# Output:
"birthday", "holyday", "eastern"
```
If two lists are provided, the scraper will search for each combination of the two lists.
In this example we can further narrow down the search, by providing a sentiment:
```
"searchTerms":[
  ["birthday", "holyday", "eastern"]
  ["worst", "best"]
]
# Output:
"brithday AND worst", "brithday AND best",  ...
```

### `additionalQuery`
X gives us the ability to narrow down our search via queries. The specification of `additionalQuery` will thus be appended to each resolved search term. Continuing our first example from `searchTerms`, the new search requests would resolve as follows (allowing only english posts):
```
"searchTerms": ["birthday", "holyday", "eastern"],
"addtionalQuery": "lang:en"

# Output:
"birthday lang:en", "holyday lang:en", "eastern lang:en"
```

### `timeBins`
X also allows us to filter posts for specific times. If you want to extract posts from a specific time frame, you can use the `timeBins` option (using the ISO 8601 Format `"YYYY-MM-DD"`):
```
# filter yearly since 2022
"timeBins": ["2022-01-01", "2023-01-01", "2024-01-01", "2025-01-01"]
```
The scraper will now do a search for each time bin. So posts for the years 2022 up to 2024 for each year.