import csv
import json
from data_struct import Paper, Authors

def load_json(json_filepath):
    # Read from file
    with open(json_filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def parse_json(data):  
    data_list = []  
    counter = 0
    for item in data:
        pid = item.get("pid", "")
        # skip entries
        if pid == 61:
            continue
        if pid == 218:
            continue

        title = item.get("title", "")
        abstract = item.get("abstract", "")
        topics = ", ".join(item.get("topics", [""]))

        # Extract author's details if the list is not empty
        first_author_name = ""
        first_author_email = ""
        authors = item.get("authors", [])
        contacts = item.get("contacts", [])

        paper_authors = []
        if authors:
            for author in authors:
                given_name = author.get("given_name", "").strip()
                family_name = author.get("family_name", "").strip()
                email = author.get("email", "").strip()
                affiliation = author.get("affiliation", "").strip()
                paper_authors.append(Authors(given_name, family_name, email, affiliation))

            # get first author details
            first_author = authors[0]
            given_name = first_author.get("given_name", "").strip()
            family_name = first_author.get("family_name", "").strip()
            
            # Combine given and family name, ensuring we don't have stray spaces
            first_author_name = f"{given_name} {family_name}".strip()
            first_author_email = first_author.get("email", "").strip()
        
        paper_contacts = []
        if contacts:
            for contact in contacts:
                given_name = contact.get("given_name", "").strip()
                family_name = contact.get("family_name", "").strip()
                email = contact.get("email", "").strip()
                affiliation = contact.get("affiliation", "").strip()
                paper_contacts.append(Authors(given_name, family_name, email, affiliation))

        data_list.append(Paper(pid, title, abstract, first_author_name, first_author_email, paper_authors, topics, paper_contacts))
        counter += 1
    print("total entries in JSON file is", counter)
    return data_list


def store_to_csv(data_list, output_filename="output.csv"):

    headers = [
        "pid", 
        "title",
        "first author", 
        "first author email", 
        "session number"]

    with open(output_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()

        pid = -1
        first_author_name = ""
        first_author_email = ""
        title = ""
        snum = 0
        for data in data_list:
            pid = data.pid
            title = data.title
            first_author_name = data.first_author_name
            first_author_email = data.first_author_email
            snum = data.snum

            # Write row to CSV
            writer.writerow({
                "pid": pid,
                "title": title,
                "first author": first_author_name,
                "first author email": first_author_email,
                "session number": snum,
            })
