import sys
sys.path.insert(0,'/opt')
import json

import boto3
import slackweb
import os
import random
import string
from zipfile import ZipFile

import os
grupo = os.environ['GROUP']

s3 = boto3.client('s3',)

def randomString(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def createFolderTmp():
    path = "/tmp/"+ randomString()

    try:
        os.mkdir(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
        return None
    else:
        print ("Successfully created the directory %s " % path) 
        return path
def readFromS3andWriteUnzipedLocal(bucketName,bucketKey,path):
    with open(path+'/obj', 'wb') as f:
        s3.download_fileobj(bucketName, bucketKey, f)

    with ZipFile(path+'/obj', 'r') as zipObj:
       zipObj.extractall(path)  
       
def returnInformationDeploy(path):
    data = {}
    with open(path+'/githash', 'r') as file:
        data["githash"] = file.read().replace('\n', '')
    with open(path+'/imagedefinitions.json', 'r') as file:
        data["imagedefinitions"] = json.loads(file.read().replace('\n', '').replace('[','').replace(']',''))
    
    return data
    
def messageToSlack(data):
    return "O grupo " + str(grupo) + " acabou de disponibilizar a imagem " + data['imagedefinitions']['name'] + " que vem do commit " + data['githash']
   

def hello(event, context):
    print(str(event))
    print(str(context))
    
    bucketName = event['Records'][0]['s3']['bucket']['name']
    bucketKey = event['Records'][0]['s3']['object']['key']
    
    print("Bucket name:" + bucketName)
    print("Bucket key:" + bucketKey)
    
    path=createFolderTmp()
    readFromS3andWriteUnzipedLocal(bucketName, bucketKey,path)
    data = returnInformationDeploy(path)
    message = messageToSlack(data)
    
    
    slack = slackweb.Slack(url='https://hooks.slack.com/services/TUQ4LAR34/BV4FNN8NQ/JyYkKDkloDQtzcYZQxyVffR')
    slack.notify(text=message, channel="#integration-cicd",username="serverless bot", icon_emoji=":squirrel: :shitpit:")

    

