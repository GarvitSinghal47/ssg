from azure.storage.blob import BlobServiceClient
# blob_service_client = BlobServiceClient(account_url=f"https://ssgloginstorage.table.core.windows.net/azurestoragetable", credential='Usqgug31Vzwpk5C/Xe0e7nWhHHtkqHzGOIwLIbs7tD8aN+ngS/kO088MHhySFpzD9VZ5RZGKyn6B+AStxOudkw==')

storage_account_key='Usqgug31Vzwpk5C/Xe0e7nWhHHtkqHzGOIwLIbs7tD8aN+ngS/kO088MHhySFpzD9VZ5RZGKyn6B+AStxOudkw=='
storage_account_name='ssgloginstorage'
connection_string='DefaultEndpointsProtocol=https;AccountName=ssgloginstorage;AccountKey=Usqgug31Vzwpk5C/Xe0e7nWhHHtkqHzGOIwLIbs7tD8aN+ngS/kO088MHhySFpzD9VZ5RZGKyn6B+AStxOudkw==;EndpointSuffix=core.windows.net'
container_name='azurecontainer'
blob_service_client =BlobServiceClient.from_connection_string(connection_string)
blob_list=[]


def uploadToBlob(file,date):
    filename = file.filename
    file_stream = file.stream
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=str(date) + "_" + filename)
    blob_client.upload_blob(file_stream.read())
    print(f"Uploaded {filename}")
    

def getBlobData():
    for blobImg in blob_service_client.get_container_client(container=container_name).list_blobs():
        blobname=blobImg.name
        blob_list.append(blobname)
        # blob_list.append(f'https://ssgloginstorage.blob.core.windows.net/{container_name}/{blobImg.name}')
        # https://ssgloginstorage.blob.core.windows.net/azurecontainer/Img1.jpg

getBlobData()
print(f'GOTBLOBURL   ',blob_list)


