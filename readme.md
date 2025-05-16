# Azure Text Summariser
This project involves the design of a serverless text summariser deployed on Microsoft Azure, generating abstarct summaries of users' inputted sentences/paragraphs.

## Components
- This project contains 2 functions, of which the second function is event-triggered with a SQL Trigger.
- The first functions stores users inputted sentence into a virtual database in Azure.
- Once a new entry is detected in the virtual database table, this triggers the second summarising function created with Azure Synapse Analytics, generating an abstract summary of the sentence and storing into an adjacent column of the original sentence within the same table. 

## Before running the code please ensure that you have these included:
1. Azure Subscription.
2. An Azure SQL Database - you would need to establish an ODBC connection string
3. Azure AI Services package - you would need a LANGUAGE_KEY and LANGUAGE_ENDPOINT.
4. Azure-functions configured on Visual Studio Code.

## RUNNING THE CODE ON VISUAL STUDIO CODE:
- To run the code on Visual Studio Code, navigate to the left side of the taskbar to locate 'Azure'.
- Press the F5 button to start running the function.
- Head to your browser or postman, paste the url of the function ("http://localhost:7071/api/submit_text?text=[YOUR_TEXT]") and select GET.
- Login to your Azure SQL Database created and there should be a table called 'TextDatabase' with 2 columns: 'original_text' and 'summarised_text'.
  -original_text: contains the text inputted.
  -summarised_text: contains the generated summary after processing the text. 

## RUNNING THE CODE ON AZURE:
- Ensure that you have deployed this project into Azure with entering F1 and selecting 'Azure Functions: Deploy to Azure...'
- Press the F5 button to start running the function locally.
- Navigate to the Function App and open the Functions tab
- Navigate to the submit_text function, type 'text' as the NAME and any string of text as the VALUE.

## CHECK THE DATABASE:
-After running the first function, make sure to check your database table to check the 'original_text' and 'summarised_text' columns in the TextDatabase table."# Azure-Serverless-Text-Summariser" 
