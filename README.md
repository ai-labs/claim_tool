
# Claim Management System

## Introduction

This project aims to create a comprehensive Claim Management System that facilitates efficient handling and processing of customer claims. The system integrates AI-driven data enrichment, flexible data storage solutions, and seamless integration capabilities with enterprise systems like SAP, Salesforce, and various databases or data warehouses.

## Concept

### Claim Submission Form
- **User Interaction**: The user is presented with a form to input claim details:
  - Claim Type
  - Quantity
  - Unit of Measure (UOM)
  - Amount
  - Description
  - Document Number (upload file)
  - Document Refs (upload file)
- **File Upload**: Users can upload files with the claim information.
- **Data Submission**: Upon clicking the "Submit" button, the data is processed.

### Data Enrichment
- **API Integration**: The system sends a request to the ChatGPT API to enrich the claim data.
- **Enhanced Data**: Additional columns are added to the claim data based on the enrichment process:
  - Material Number
  - Status (suggested)
  - Reason
  - Relevant
  - Summary (of the document)
  - Description (info from images)
  - Department
  - Damage Factor
  - Damage Description
- **Data Storage**: The enriched data is returned in JSON format and stored in the database.

### Claims List
- **View Claims**: Users can view a complete list of all claims.
- **Edit Capabilities**: The list includes functionalities for editing the claims.

### Integration with SAP Systems
- **Data Access Class**: The point of integration is the class responsible for data access.
- **Re-implementation**: This class can be re-implemented to store data in SAP systems, interacting via API.
- **Flexible Integration**: With correct re-implementation, the system can integrate with SAP, Salesforce, any database, or data warehouse.

## Sequence of Actions and Integration Capabilities

1. **User submits a claim via the form and uploads files.**
2. **System processes the form data and sends it to the ChatGPT API for enrichment.**
3. **ChatGPT API enriches the data, adding additional columns.**
4. **Enriched data is returned in JSON format and stored in the database.**
5. **Users can view and edit the list of claims on a separate tab.**
6. **For integration with enterprise systems:**
   - **Re-implement the data access class to interact with the target system via API.**
   - **Ensure the class handles data storage and retrieval according to the system's specifications (e.g., SAP, Salesforce).**

## Architecture Diagram

```plaintext
User
  |
  |---> Submits Claim (Form Input + File Uploads)
        |
        |---> System (Processes Submission)
                |
                |---> ChatGPT API (Data Enrichment)
                        |
                        |---> Enriched Data (JSON)
                                |
                                |---> Database (Stores Enriched Data)
                                        |
                                        |---> Claims List (View/Edit Claims)
                                                |
                                                |---> Integration (Re-implement Data Access Class)
                                                        |
                                                        |---> Target System (e.g., SAP, Salesforce, Database)
```

## Getting Started

To get started with this project:

1. **Clone the repository**:
   ```bash
   git clone git@github.com:ai-labs/claim_tool.git
   cd claim_tool
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Set up API keys**:
   - Configure the ChatGPT API key in your environment settings.

5. **Implement Data Access Class for Integration**:
   - Modify the data access class to interact with your target system (SAP, Salesforce, etc.).

6. **Enjoy the streamlined claim management process**.
