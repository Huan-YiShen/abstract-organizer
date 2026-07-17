from data_struct import assign_session
from json_handler import load_json, parse_json
from createpdf import create_formatted_pdf
if __name__ == "__main__":
    data = load_json("./mock_data/mock.json")
    output_filename = "poster_abstracts.pdf"
    data_list = parse_json(data)
    assign_session(data_list)
    
    print("total entries recorded", len(data_list))

    create_formatted_pdf(output_filename, data_list)
    print("PDF successfully generated with a unified format on all pages!")