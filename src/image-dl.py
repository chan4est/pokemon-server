import json
import requests
import os

headers = {
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0"
}
def download_image(img_url,i):
    data_folder="/mnt/d/Users/Chandler/Development/pokemon-server/images/"
    
    try:
        res=requests.get(img_url,allow_redirects = True,headers=headers)
        img_bytes= requests.get(img_url).content # download bytes for a image
        with open(os.path.join(data_folder,str(i)+".png"),"wb") as img_file:
            img_file.write(img_bytes)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    # json_file = "/mnt/d/Users/Chandler/Development/pokemon-server/pokemon.json"
    json_file = "/mnt/d/Users/Chandler/Development/pokemon-server/alt.json"
    key = "image_home"
    with open(json_file, "r") as f:
        data = json.load(f)
        for pokemon in data:
            download_image(pokemon[key], pokemon["form_id"])
            print(pokemon["form"], pokemon["form_id"])