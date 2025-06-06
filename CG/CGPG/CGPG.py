# import the JSON utility package
import json

# import the AWS SDK (for Python the package name is boto3)
import boto3
# import two packages to help us with dates and date formatting
from time import gmtime, strftime

# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')
# use the DynamoDB object to select our table
table = dynamodb.Table('SPGTable')
# store the current time in a human readable format in a variable
now = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

# define the handler function that the Lambda service will use an entry point
def lambda_handler(event, context):

# extract the words from the Lambda service's event object
    words = str(event['firstword']).lower() + str(event['lastword']).lower()

    dict = {
        "a": "@",
        "b": "6",
        "e": "3",
        "g": "9",
        "i": "1",
        "l": "1",
        "o": "0",
        "q": "9",
        "s": "5",
        "t": "7",
    }
    
    # Convert word to a list to modify individual characters
    word_list = list(words)
    
    # Set place variable as 1 before itterating to replace every 3rd letter with uppercase
    place = 1
    
    # Use a range the length of words_list to iterate over indices
    for i in range(len(word_list)):
        
        # Check if the character is in the dictionary
        if (word_list[i]).lower() in dict:
            # Replace the character with its corresponding value
            word_list[i] = dict[word_list[i]]
    
        # Check if the character is a letter and if it is the 3rd character
        if word_list[i].isalpha() == True and place % 3 == 0:
            # Replace the letter with its uppercase value
            word_list[i] = (word_list[i]).upper()
        # Check if the character is a letter and if it is not the 3rd letter
        elif word_list[i].isalpha() == True and place % 3 != 0:
            # Replace the letter with its lowercase value
            word_list[i] = (word_list[i]).lower()
        # Move through the list by increasing the place variable
        place += 1
    
    
    # Join the list back into a string
    wordGenerated = ''.join(word_list)
    
# write result and time to the DynamoDB table using the object we instantiated and save response in a variable
    response = table.put_item(
        Item={
            'Time':now,
            'Log':'Password generated'
            })

# return a properly formatted JSON object
    return {
    'statusCode': 200,
    'body': json.dumps(wordGenerated)
    }