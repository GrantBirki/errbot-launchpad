# A set of helper classes for interacting with DynamoDB in AWS
# In this file you will see class definitions for DB table models and a class with common CRUD methods

import os
from lib.common.utilities import Util
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    NumberAttribute,
    UnicodeSetAttribute,
    UTCDateTimeAttribute,
)
from pynamodb.exceptions import DoesNotExist

import boto3

session = boto3.Session(
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name="us-west-2",
)

dynamo = session.resource("dynamodb")

util = Util()


class ExampleTable(Model):
    """
    An example DynamoDB table model for interacting with it via the Dynamo class below
    """
    class Meta:
        table_name = "example"
        region = "us-west-2"
        aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
        aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]

    country = UnicodeAttribute(hash_key=True)
    username = UnicodeAttribute(range_key=True)
    favorite_food = UnicodeAttribute()


class Dynamo:
    """
    A helper class for using CRUD (create, read, update, delete) actions on AWS DynamoDB tables
    """
    def write(self, object):
        """
        Write a new (and replace) a database record
        """
        try:
            iso_timestamp = util.iso_timestamp()
            setattr(object, "created_at", iso_timestamp)
            setattr(object, "updated_at", iso_timestamp)
            object.save()
            return True
        except:
            return False

    def update(self, table: object, record: object, fields_to_update: list):
        """
        Input an existing database upject and update it in place

        Example [records_to_update]:
        [SomeTable.hello_world.set("i am a message")]
        """
        try:

            # Update the timestamp

            fields_to_update.append(table.updated_at.set(util.iso_timestamp()))

            record.update(actions=fields_to_update)
            return True
        except DoesNotExist:
            return None
        except:
            return False

    def get(self, object, partition_key, sort_key):
        """
        Get an existing database object
        Note: Useful for passing this object into the update method
        """
        try:
            result = object.get(partition_key, sort_key)
            return result
        except DoesNotExist:
            return None
        except:
            return False

    def delete(self, object):
        """
        Deletes a database object

        Note: You need to run a get() and pass the object in to use this method
        """
        try:
            object.delete()
            return True
        except:
            return False

    def scan(self, table_name, **kwargs):
        """
        A scan means to get ALL records in a table

        NOTE: Anytime you are filtering by a specific equivalency attribute such as id, name
        or date equal to ... etc., you should consider using a query not scan

        kwargs are any parameters you want to pass to the scan operation
        """
        try:
            dbTable = dynamo.Table(table_name)
            response = dbTable.scan(**kwargs)
            if kwargs.get("Select") == "COUNT":
                return response.get("Count")
            data = response.get("Items")
            while "LastEvaluatedKey" in response:
                response = kwargs.get("table").scan(
                    ExclusiveStartKey=response["LastEvaluatedKey"], **kwargs
                )
                data.extend(response["Items"])
            return data
        except:
            False

# Example usage:

# These imports are assuming that you are in some new plugin directory writing code for a new chatop function

#from lib.common.utilities import Util
#from lib.database.dynamo import Dynamo, ExampleTable

# dynamo = Dynamo()
# util = Util()

# Write a record to the ExampleTable in DynamoDB assuming the table exists
# dynamo.write(
#     ExampleTable(
#         country="usa",
#         username="skywalker",
#         updated_at=util.iso_timestamp(),
#     )
# )
