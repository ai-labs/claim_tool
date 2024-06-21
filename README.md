
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

 ![screen 1](https://github.com/ai-labs/claim_tool/blob/master/media/s1.png?raw=true)
 ![screen 2](https://github.com/ai-labs/claim_tool/blob/master/media/s2.png?raw=true)

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
- **Edit Capabilities**: The list includes functionalities for editing the claims. [NOT IMPLEMENTED YET IN UI, SUPPORTED ON API/DATA LAYERS]

### Integration with Business Systems
- **Data Access Class**: The point of integration is the class responsible for data access.
- **Re-implementation**: This class can be re-implemented to store data in various systems, interacting via API.
- **Flexible Integration**: With correct re-implementation, the system can integrate with SAP, Salesforce, and other business systems.

## Sequence of Actions and Integration Capabilities

1. **User submits a claim via the form and uploads files.**
2. **System processes the form data and sends it to the ChatGPT API for enrichment.**
3. **ChatGPT API enriches the data, adding additional columns.**
4. **Enriched data is returned in JSON format and stored in the database.**
5. **Users can view and edit the list of claims on a separate tab.**
6. **For integration with enterprise systems:**
   - **Re-implement the data access class to interact with the target system via API.**
   - **Ensure the class handles data storage and retrieval according to the system's specifications (e.g., SAP, Salesforce, others).**

## Architecture Diagram

```plaintext
                        +--------------------------------------+
                        |              User                    |
                        |--------------------------------------|
                        | - Submits Claim Form                 |
                        | - Uploads Files                      |
                        +-----------------|--------------------+
                                          |
                                          v
+------------------------------------------v-----------------------------------------+
|                               Claim Management System                              |
|------------------------------------------|-----------------------------------------|
|                                          |                                         |
|                                          v                                         |
|              +---------------------------v----------------------------+            |
|              |             Form Data Processor                        |            |
|              |-------------------------------------------------------|            |
|              | - Receives Form Data and Files                        |            |
|              | - Sends Data to ChatGPT API for Enrichment            |            |
|              +---------------------------|----------------------------+            |
|                                          |                                         |
|                                          v                                         |
|              +---------------------------v----------------------------+            |
|              |               ChatGPT API Integration                  |            |
|              |-------------------------------------------------------|            |
|              | - Enriches Claim Data                                 |            |
|              | - Adds Additional Columns                             |            |
|              +---------------------------|----------------------------+            |
|                                          |                                         |
|                                          v                                         |
|              +---------------------------v----------------------------+            |
|              |              Enriched Data Storage                     |            |
|              |-------------------------------------------------------|            |
|              | - Stores Enriched Data in Database                    |            |
|              +---------------------------|----------------------------+            |
|                                          |                                         |
|                                          v                                         |
|              +---------------------------v----------------------------+            |
|              |             Claims List Viewer/Editor                  |            |
|              |-------------------------------------------------------|            |
|              | - Displays Complete List of Claims                    |            |
|              | - Provides Editing Capabilities                       |            |
|              +---------------------------|----------------------------+            |
|                                          |                                         |
|                                          v                                         |
|              +---------------------------v----------------------------+            |
|              |         Data Access Layer (DAL) Implementation        |            |
|              |-------------------------------------------------------|            |
|              | - Abstracts Data Storage and Retrieval Processes      |            |
|              | - Enables Integration with Backend Systems            |            |
|              |       +-------------------+   +-------------------+   |            |
|              |       |     SAP S/4HANA   |   |   Salesforce      |   |            |
|              |       +-------------------+   +-------------------+   |            |
|              |       +-------------------+   +-------------------+   |            |
|              |       |     SAP ECC       |   |   Oracle ERP      |   |            |
|              |       +-------------------+   +-------------------+   |            |
|              |       +-------------------+   +-------------------+   |            |
|              |       |  SAP Business One |   |    Microsoft      |   |            |
|              |       +-------------------+   |    Dynamics 365   |   |            |
|              |                               +-------------------+   |            |
|              +-------------------------------------------------------+            |
+------------------------------------------------------------------------------------+
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
   pip install -r requirements/common.txt
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

## Data Access Layer (DAL) and Architecture

### Abstract Data Access Layer
To facilitate integration with various business systems, a Data Access Layer (DAL) will be implemented. This layer abstracts the data storage and retrieval processes, allowing seamless interaction with various backend systems.

### Integration Steps
1. **Define Interface**: Create a common interface for data access operations (CRUD).
2. **Implement Integration**: Develop a class implementing the interface for each target system.
3. **Configure API Interaction**: Ensure the class interacts with the target system's APIs for data operations.

### Recommended Systems for Integration
1. **SAP S/4HANA**: Leverage SAP S/4HANA's API for enterprise resource planning.
2. **SAP ECC**: Use SAP ERP Central Component (ECC) for traditional ERP functionalities.
3. **SAP Business One**: Utilize SAP Business One for small and medium-sized enterprises.
4. **Salesforce**: Integrate with Salesforce for customer relationship management.
5. **Oracle ERP**: Use Oracle ERP for comprehensive enterprise resource planning.
6. **Microsoft Dynamics 365**: Utilize Microsoft Dynamics 365 for flexible business applications.

By implementing these steps, the system will be able to integrate with various business systems, providing flexibility and scalability.

## Main Classes

### Claim
Represents a claim made by a customer.

#### Fields:
- `id`: Unique identifier
- `type`: Type of the claim
- `quantity`: Quantity of the item
- `uom`: Unit of Measure
- `amount`: Claim amount
- `description`: Description of the claim
- `document_number`: Related document number
- `document_refs`: References to uploaded documents

### Document
Represents a document associated with a claim.

#### Fields:
- `id`: Unique identifier
- `file_name`: Name of the file
- `file_path`: Path to the file
- `upload_date`: Date of upload
- `claim_id`: Associated claim ID

### Data Access Layer (DAL)
Abstracts the data storage and retrieval processes.

#### Methods:
- `create(data)`: Create a new record in the database.
- `read(query)`: Read records from the database based on the query.
- `update(id, data)`: Update a record in the database.
- `delete(id)`: Delete a record from the database.

## JSON Structures

### Claim JSON Structure
```json
{
  "id": "12345",
  "type": "RETURN",
  "quantity": 10,
  "uom": "PC",
  "amount": 100.00,
  "description": "Damaged goods",
  "document_number": "900001",
  "document_refs": ["image_10001.jpg"]
}
```

### Document JSON Structure
```json
{
  "id": "67890",
  "file_name": "invoice_2000002.pdf",
  "file_path": "/uploads/invoice_2000002.pdf",
  "upload_date": "2023-06-08",
  "claim_id": "12345"
}
```
# Claim Management System - Swagger API Documentation (see /docs endpoint for life view)

This section provides a detailed overview of the API endpoints available for the Claim Management System, including the expected request and response structures. This documentation aims to facilitate integration with various systems and streamline the process of handling customer claims.

## Overview

The Claim Management System offers the following key functionalities through its API:
- Fetching claims
- Submitting new claims
- Updating existing claims
- Submitting documents for claims

### Base URL
The base URL for accessing the API endpoints is: `http://{IP/DOMAIN NAME}:8000`

## Endpoints

### Fetch Claims
- **Endpoint**: `GET /claims`
- **Description**: Fetch all claims.
- **Response**: A list of claims with their details.

#### Example Response:
```json
[
  {
    "status": "PENDING",
    "document": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "documents": [
      "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    ],
    "customer": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "date": "2024-06-20",
    "type": "RETURN",
    "description": "string",
    "material": 0,
    "quantity": 0,
    "unit": "string",
    "amount": 0,
    "ID": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "created": "2024-06-20",
    "updated": "2024-06-20",
    "result": {
      "status": "APPROVED",
      "reason": "CLAIM_AMOUNT_BELOW_THRESHOLD",
      "relevant": true,
      "summary": "string",
      "description": "string",
      "department": "string",
      "damage": {
        "factor": 1,
        "description": "string"
      }
    }
  }
]
```

### Submit Claim
- **Endpoint**: `POST /claims`
- **Description**: Submit a new claim.
- **Request Body**:
```json
{
  "status": "OPEN",
  "document": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "documents": [
    "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  ],
  "customer": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "date": "2024-06-20",
  "type": "RETURN",
  "description": "string",
  "material": 0,
  "quantity": 0,
  "unit": "string",
  "amount": 0
}
```

### Update Claim
- **Endpoint**: `PATCH /claims/{claim}`
- **Description**: Update an existing claim.
- **Path Parameter**:
  - `claim`: UUID of the claim to be updated.
- **Request Body**:
```json
{
  "status": "PENDING",
  "document": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "documents": [
    "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  ],
  "customer": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "date": "2024-06-20",
  "type": "RETURN",
  "description": "string",
  "material": 0,
  "quantity": 0,
  "unit": "string",
  "amount": 0,
  "ID": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "created": "2024-06-20",
  "updated": "2024-06-20"
}
```

### Submit Document
- **Endpoint**: `POST /documents/{claim}`
- **Description**: Submit documents for a claim.
- **Path Parameter**:
  - `claim`: UUID of the claim.
- **Request Body**: `multipart/form-data`
  - `documents`: Array of documents.

# TODO:

This is a basic implementation in progress. For now some parts is still under development:

* claim delete is not implemented yet
* full PDF/DOC support is still in progress
* Integetion level is just an existing interface, need to be implemented
* Enhance UI, bring editing info into UI
