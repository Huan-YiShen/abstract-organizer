class Authors():
    def __init__(self, given_name, family_name, email, affiliation):
        self.given_name = given_name
        self.family_name = family_name
        self.email = email
        self.affiliation = affiliation

class Paper():
    def __init__(
            self, pid, title, abstract, 
            first_author_name, first_author_email, paper_authors, 
            topics, paper_contacts, snum= 0):
        self.pid = pid
        self.title = title
        self.abstract = abstract
        self.first_author_name = first_author_name
        self.first_author_email = first_author_email
        self.authors = paper_authors
        self.topics = topics
        self.contacts = paper_contacts
        self.snum = snum

   
def assign_session(data_list):
    midpoint = int(len(data_list)/2) + 1
    print(f"first {midpoint} entries will be in session 1, {len(data_list) - midpoint} entries in session 2")
    for idx, data in enumerate(data_list):    
        session_number = 1 if idx < midpoint else 2
        data.snum = session_number
