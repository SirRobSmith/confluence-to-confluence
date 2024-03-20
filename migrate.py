""" This tool has been created to faclitate the 'live migration' of confluence
sites, with a particular focus on supporting source systemw which are at a low
version  """

import os
from datetime import datetime
from pathlib import Path
from os import listdir
from os.path import isfile, join
from atlassian import Confluence

# Variables to govern how the tool works with the source system
SOURCE_SPACE_KEY          = "DM"
SOURCE_SERVER             = os.environ['SOURCE_SERVER']
SOURCE_USER               = os.environ['SOURCE_USER']
SOURCE_PASS               = os.environ['SOURCE_PASS']

# Variables to govern how the tool works with the destination system
DESTINATION_SPACE_KEY     = "DE"
DESTINATION_ROOT_PAGE     = ""
DESTINATION_SERVER        = os.environ['DESTINATION_SERVER']
DESTINATION_USER          = os.environ['DESTINATION_USER']
DESTINATION_PASS          = os.environ['DESTINATION_PASS']

# Other runtime-y stuff
LOG_LOCATION            = "migrate.log"
NOW                     = datetime.now()
readable_date           = NOW.strftime("%m/%d/%Y, %H:%M:%S")

# Connect to the confluence source and destination servers
source_confluence = Confluence(
    url = SOURCE_SERVER,
    username=SOURCE_USER,
    password=SOURCE_PASS)

destination_confluence = Confluence(
    url = DESTINATION_SERVER,
    username=DESTINATION_USER,
    password=DESTINATION_PASS,
    )

def log_progress(log_message):
    """
    Log a message to a file
    :param log_message: the message to log
    """
    with open(f'{LOG_LOCATION}', "a", encoding="utf-8") as f:
        f.write(str(readable_date)+" | "+log_message+"\r\n")
        f.close()

def find_homepage(site_key):
    """
    Locates the root folder for a given site key
    :param site_key: the site key to search
    """
    page_ids = []
    # Get all of the pages using the pagination of the API
    for i in range(20):

        api_start_point = i * 100
        pages = source_confluence.get_all_pages_from_space(site_key, start=api_start_point, limit=100, status=None, expand="ancestors", content_type='page')

        # Did we find a page without an ancestor?
        for page in pages:
            if len(page['ancestors']) == 0:
                page_ids.append(page['id'])

    return page_ids

# Downloads attachments from the source system
def download_attachments(page_id):
    """
    Downloads all attachments for a give page_id. Storing them in a local /cache/ folder
    :param page_id: the page id 
    """
    Path(f"cache/{page_id}/").mkdir(parents=True, exist_ok=True)
    source_confluence.download_attachments_from_page(page_id, path=f"cache/{page_id}/")
    log_progress("----- Attachments for this page downloaded")

# Uploads attachments to the destination system
def upload_attachments(source_page_id, destination_page_id):
    """
    Uploads attachments to the source confluence server
    :param source_page_id: the page id from the source server
    :param destination_page_id: the page id of the destination server
    """
    directory = f"cache/{source_page_id}/"
    for file in listdir(directory):

        if(isfile(join(directory, file))):
            
            destination_confluence.attach_file(f"cache/{source_page_id}/{file}", name=None, content_type=None, page_id=destination_page_id, title=None, space=None, comment=None)
            log_progress(f"----- Attachment name {file} uploaded")

def migrate_page(source_site, destination_site, start_page, parent):
    """
    The primary function which encapsulates the migration of pages
    :param source_site: the site key we're migrating from (source system)
    :param destination_site: the site key we're migrating to (destination system)
    :param parent: Largely used when the function is called by itself
    """
    log_progress(f"--- Migrate page started for ({source_site}) moving to ({destination_site}); starting with parent page ({start_page}); This page is a child of ({parent})")
    
    # Get data for the page
    page_data = source_confluence.get_page_by_id(start_page, expand="body.storage,children.page", status=None, version=None)

    # Does the page already exist in our destination? We can check by title.
    page_exists_status = destination_confluence.page_exists(destination_site, page_data['title'], type="page")

    if(page_exists_status is True):

        log_progress("---- This page already exists in the destination system")

        # It may be useful to have the meta data for this page in case it happens to have children
        destination_page_data = destination_confluence.get_page_by_title(destination_site, page_data['title'], start=None, limit=None)
        destination_parent = destination_page_data['id']

    else:

        log_progress("---- This page doesn't exist in the destination system; migration starting")

        # Create the page in the destination system
        try:
            created_page = destination_confluence.create_page(destination_site, page_data['title'], page_data['body']['storage']['value'], parent_id=parent, type='page', representation='storage', editor='v2', full_width=False)

        except:
            log_progress("---- Page Creation Failed")

        else:

            # Download the attachments for the page
            download_attachments(start_page)

            # Upload the attachments for the page
            upload_attachments(start_page, created_page['id'])

         
    
    # With the page migrated we can look for children
    children = source_confluence.get_page_child_by_type(start_page, type='page', start=None, limit=None, expand=None)

    for child in children:

        log_progress(f"----- This page has children, processing child ({child['id']})")
        if 'destination_parent' in locals():

            # Catering for when the parent of this child (i.e. this invocation) already existed and we know the parent under which the child should be nested
            migrate_page(source_site, destination_site, child['id'], destination_parent)
        else:

            # Catering for when the parent of this change (I.e this invocation) doesn't exist
            migrate_page(source_site, destination_site, child['id'], created_page['id'])


# Let's go and look for pages in our source system.
if __name__ == "__main__":
    
    log_progress("Tool Executed Manually")

    log_progress(f"- Starting work on ({SOURCE_SPACE_KEY})")

    # Get a list of ancestorless homepages
    site_homepages = find_homepage(SOURCE_SPACE_KEY)

    # Work on each, they should all be placed in the destination site out in sites
    for site_homepage in site_homepages:

        log_progress(f"-- Parent page found with pageId {site_homepage}")

        # Start the migration from this page
        migrate_page(SOURCE_SPACE_KEY,  DESTINATION_SPACE_KEY, site_homepage, DESTINATION_ROOT_PAGE)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   