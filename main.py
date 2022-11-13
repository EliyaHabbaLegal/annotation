# # read df
# import pandas as pd
#
# df = pd.read_csv(r'all_results_with_origin_sen_clean.csv')
#
# # loop over the df
# for index, row in df.iterrows():
#     sentence = row['origin_sentence']


import requests


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/spreadsheets/d/16GTfGGgAfsrgtxN9dRmDU-ZFwy0Wmu7G9OPR3Ue7-u0/edit?usp=share_link"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)
    print(type(response))
    # save_response_content(response, destination)