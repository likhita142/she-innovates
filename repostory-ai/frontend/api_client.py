import requests

API_URL="http://127.0.0.1:8000/generate"


def generate_story(repo):

    response=requests.post(

        API_URL,

        json={"repo":repo}

    )

    return response.json()