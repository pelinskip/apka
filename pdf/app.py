import boto3, json, time
from mail import send_email
from uuid import uuid4
from creator import create

s3 = boto3.resource('s3')

bucket_name = '167885'
bucket_address = 'https://s3.eu-central-1.amazonaws.com/167885'

def upload_s3(source_file, filename):
  destination_filename = "albums/%s/%s" % (uuid4().hex, filename)
  bucket = s3.Bucket(bucket_name)
  bucket.put_object(Key=destination_filename, Body=source_file, ACL='public-read')

  return destination_filename

sqs = boto3.resource('sqs')
albumRequests = sqs.get_queue_by_name(QueueName='pelinski-album')

while True:
  for albumRequest in albumRequests.receive_messages():
    print('start consuming')
    albumData = json.loads(albumRequest.body)
    pdf = create(albumData)
    dest = upload_s3(pdf.getvalue(), 'album.pdf')
    send_email(albumData['sent_to'], 'Your album', 'download here: %s/%s' % (bucket_address, dest))
    albumRequest.delete()
    print('consumed [X]')
  time.sleep(1)
