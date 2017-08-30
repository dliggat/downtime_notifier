import boto3
import glob
import os
import yaml
import boto3

client = boto3.client('ssm')



def configuration(filename='config.yaml'):
    """Load configuration from config file."""

    config = {}
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', filename)), 'r') as f:
        config = yaml.load(f)
        print(config)

    new_config = {}
    for (k,v) in config.iteritems():
        key = k
        value = os.path.expandvars(v)
        if k.startswith('parameterstore_'):
            key = k.split('parameterstore_')[-1]
            value = client.get_parameter(Name=value, WithDecryption=True)['Parameter']['Value']
        new_config[key] = value

    return new_config


