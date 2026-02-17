
import requests
import os

headers = {
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0"
}
def download_image(img_url,i):
    data_folder=##DATA FOLDER
    try:
        res=requests.get(img_url,allow_redirects = True,headers=headers)
        img_bytes= requests.get(img_url).content # download bytes for a image
        with open(os.path.join(data_folder,str(i+1)+".png"),"wb") as img_file:
            img_file.write(img_bytes)
    except Exception as e:
        print(e)


for i in range(len(list)):
    download_image(list[i], i)