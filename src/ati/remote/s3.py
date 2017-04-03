import boto3
import json

def get_remote_state(state_file : str = 'terraform.tfstate') -> dict:
    """ fetch remote state from s3 and return it as a dictionary

    This function is used to fetch a state file from AWS S3, convert
    and return it as a dictionary.

    Args:
        state_file: The name of the statefile in the bucket
    """
    pass
