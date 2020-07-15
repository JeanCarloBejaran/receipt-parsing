import boto3
import pandas as pd
from DateParser import DateParser
import time

class Receipt(DateParser):
    """A Receipt Class that reads a receipt image, sends it to AWS Textract
    and parses out the required data for DGII report 606"""

    def __init__(self, s3_filename: str):
        self.s3BucketName = "receipt-parsing-mvp"
        self.filename = s3_filename
    
    def scan_file(self):
        """Call Amazon Textract to get text & data from file"""
        # Amazon Textract client
        # The Textract client has a .detect_document_text method
        # and an .analyze_document method for JPG and PNG
        # and asynchronous version of the above for PDFs
        textract = boto3.client('textract')

        filetype = self.filename.split(".")[-1]
        # If file is PDF
        if filetype == "pdf":
            start_job_response = textract.start_document_analysis(
                DocumentLocation = {
                    "S3Object": {
                        'Bucket': self.s3BucketName,
                        'Name': self.filename
                    }
                },
                FeatureTypes = ["TABLES"],
            )
            job_completed = False
            while job_completed == False:
                time.sleep(10)
                response = textract.get_document_analysis(
                    JobId=start_job_response["JobId"],
                    MaxResults=10
                )
                if response["JobStatus"] != 'IN_PROGRESS':
                    job_completed = True

        # If file is JPG or PNG
        else:
            response = textract.detect_document_text(
                Document={
                    'S3Object': {
                        'Bucket': self.s3BucketName,
                        'Name': self.filename
                    }
                },
                # FeatureTypes=["FORMS", "TABLES"]
            )

        print(response)
        self.blocks = response["Blocks"]
        self.df = pd.DataFrame(self.blocks)

        print(str(self.df.loc[self.df["BlockType"] == "LINE"].shape[0]) + " Lines")
        print(str(self.df.loc[self.df["BlockType"] == "WORD"].shape[0]) + " Words")
        print(str(self.df.loc[self.df["BlockType"] == "KEY_VALUE_SET"].shape[0]) + " Key Value Sets")
        print(self.df.info())

    def parse_data(self):
        self.date = self.parse_date("LINE")
        return self.date
        # rncs = get_rnc("LINE")
        # ncf = get_ncf("LINE")
        # total = get_total("LINE")