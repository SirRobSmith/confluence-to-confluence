# confluence-to-confluence
A small script to migrate raw page storage and attachment data between confluence instances. Useful for legacy source systems where official migration tools provide no support.

# Usage
Should you feel motivated to use this tool, the folllowing setup is required. 

1. Install Python3
2. Clone this repo
3. cd /your-local-folder
4. Create a Python virtual environment (python3 -m venv .venv)
5. Run '. ./venv/bin/activate'
6. run 'pip install atlassian-python-api'
7. Export Variables for the following values
7.1 SOURCE_SERVER : Your source confluence site. e.g. http://1.1.1.1:8080
7.2 SOURCE_USER : Your basic-auth username
7.3 SOURCE_PASS : Your basic-auth password / api key
7.4 SOURCE_SPACE_KEY : The space-key for the site you wish to migrate
7.5 DESTINATION_SERVER : Your destination confluence site. e.g. https://2.2.2.2:8080
7.6 DESUNATION_ROOT_PAGE : The page which will act as a parent for all migrated pages. e.g. 12345678
7.7. DESTINATION_SPACE_KEY : The space-key for your destination site. 
7.8. DESTINATION_USER : Your basic auth username for the destination site
7.9 DESTINATION_PASS : Your basic auth password / api key
8. With these environment variables defined, you may run the code with 'python3 migrate.py' 
9. Log files are emited, by default to 'migrate.log'