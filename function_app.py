import azure.functions as func
import logging
import os
import json
import pyodbc
import time
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="submit_text")
def submit_text(req: func.HttpRequest) -> func.HttpResponse:
    start_time = time.time() #Records start time of this function

    #Retrieves the user input of text
    text_input = req.params.get('text')  # Gets the text from query string
    logging.info(f"Text input: {text_input}")
    
    if not text_input:
        try:
            req_body = req.get_json()  
            text_input = req_body.get('text')  
        except ValueError:
            pass  

    # Returns error message if no text found in the query string or request body
    if not text_input:
        return func.HttpResponse(
            "Please pass a text input in the query string or in the request body.",
            status_code=400
        )
    connection_string = os.environ["CONNECTION_STRING"]

    try:
        # Establish connection to the Azure database
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Creates a table if there isn't any
        cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TextDatabase' AND xtype='U')
        BEGIN
            CREATE TABLE dbo.TextDatabase (
                Id INT IDENTITY(1,1) PRIMARY KEY,  
                original_text NVARCHAR(MAX)           
            )
        END
        ''')

        #Inserts the text into the database
        cursor.execute('''
        INSERT INTO dbo.TextDatabase (original_text)
        VALUES (?)
        ''', text_input)

        #Commit the transaction and close the connection
        conn.commit()
        cursor.close()
        conn.close()
        
        end_time = time.time()
        execution_time= end_time - start_time
        logging.info(f"Execution time: {execution_time} seconds") #Records the execution time of this function

        # Return a success message indicating the text has been inserted into the database
        return func.HttpResponse(f"Text successfully inserted into the TextDatabase table.", status_code=200)

    except Exception as e:
        logging.error(f"Error occurred while inserting data: {str(e)}")
        return func.HttpResponse(f"Failed to insert data into the database: {str(e)}", status_code=500)

# Referred to this example for setting up the SQL Trigger: https://github.com/Azure/azure-functions-sql-extension/tree/main/samples/samples-python-v2    
@app.function_name(name="process_text")
@app.sql_trigger(arg_name="newText", table_name="TextDatabase", connection_string_setting="CONNECTION_STRING_2", data_type=func.DataType.STRING)
def process_text(newText: str) -> None:
    logging.info("SQL Triggered: Processing new text...: %s", newText)
    start_time = time.time() # Records the start time of this function

    try:
        # Converts the JSON string to a Python object
        newText_obj = json.loads(newText)
        original_text = newText_obj[0]["Item"]["original_text"]  # Access the original_text 
        logging.info(f"Original text extracted: {original_text}")

        #Initialize the Azure AI Text Analytics client
        key = os.environ["LANGUAGE_KEY"]
        endpoint = os.environ["LANGUAGE_ENDPOINT"]
        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )
        logging.info("Azure Text Analytics client initialized.")
        #Referred to this website on learning how to implement the text summariser feature: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_extract_summary.py
        #Begin the abstract summarization process
        poller = text_analytics_client.begin_abstract_summary([original_text])
        new_document_results = poller.result()
        logging.info("Text summarization completed.")

        summarised_text = ""

        for result in new_document_results:
            logging.info(f"Processing result: {original_text}")
            if result.summaries:
                summarised_text = result.summaries[0].text
                logging.info(f"Summarised text: {summarised_text}")
            else:
                logging.error("No summarised text found.")
                return

        #Update the summarised text back to the database
        connection_string = os.environ["CONNECTION_STRING"]
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        logging.info("Connected to the database.")

        try:
            logging.info(f"Original text from db: {original_text}")
            logging.info(f"Summarised text: {summarised_text}")
            
            cursor.execute('''
                UPDATE dbo.TextDatabase
                SET summarised_text = ?
                WHERE original_text = ?
            ''', summarised_text, original_text)  #Displays original_text for comparison
            logging.info(f"Database updated with summarised text: {summarised_text}")

            #Commit the transaction and close the connection
            conn.commit()
            logging.info("Transaction committed.")
            cursor.close()
            conn.close()
        except pyodbc.Error as e:
            logging.error(f"Error occurred while updating the database: {str(e)}")

        logging.info(f"Text summarised: {summarised_text}")
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f"Execution time: {execution_time} seconds") #Records the execution time of this function

    except Exception as e:
        logging.error(f"Error occurred while processing text: {str(e)}")
