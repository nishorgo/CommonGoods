import os
from datetime import datetime, timezone, timedelta

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .models import Business, ProductShop, Product


def access_sheets(spreadsheet_id):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES,
                redirect_uri='http://localhost:8000/auth_callback'
            )
            credentials = flow.run_local_server(port=8000)

        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    return credentials


def sort_sheet_data(spreadsheet_id):
    credentials = access_sheets(spreadsheet_id)

    try:
        service = build("sheets", "v4", credentials=credentials)
        sheets = service.spreadsheets()

        grid_range = {
            "sheetId": 0,
            "startRowIndex": 1,
            "endRowIndex": 1000,
            "startColumnIndex": 0,
            "endColumnIndex": 8
        }

        # Create a request to sort the data based on the first column (column A)
        sort_request = {
            "sortRange": {
                "range": grid_range,
                "sortSpecs": [
                    {
                        "dimensionIndex": 0,  # Index of the column to sort (0-based)
                        "sortOrder": "ASCENDING"  # or "DESCENDING"
                    }
                ]
            }
        }

        # Execute the batch update request
        batch_update_request = {"requests": [sort_request]}
        response = sheets.batchUpdate(spreadsheetId=spreadsheet_id, body=batch_update_request).execute()

        print("Sheet sorted:", response)

    except HttpError as error:
        print(error)


def sync_data_with_sheet(shop_id, spreadsheet_id):
    credentials = access_sheets(spreadsheet_id)

    # Fetch data from the Django model
    shop = Business.objects.get(id=shop_id)
    product_shops = ProductShop.objects.filter(shop=shop).order_by('product__name')

    # Fetch data from the Google Sheet
    sheet_data = get_data_from_sheet(spreadsheet_id, credentials)

    # Compare timestamps and update the Django model or the Google Sheet accordingly
    for row_index, sheet_row in enumerate(sheet_data):
        # Assuming the first column in the sheet has the unique identifier (e.g., product ID)
        product = sheet_row[0]
        sheet_updated_at = sheet_row[-1]  # Assuming the last column has the updated_at timestamp

        if product_shops.filter(product__name=product).exists():
            print('YES')

        # Get the corresponding Django model instance
            model_instance = product_shops.get(product__name=product)

            sheet_updated_at_utc = datetime.strptime(sheet_updated_at, "%m/%d/%Y %H:%M:%S").replace(tzinfo=timezone.utc)

            # Add 6 hours to the datetime
            adjusted_model_time = model_instance.updated_at + timedelta(hours=6)


            # Compare timestamps
            if adjusted_model_time > sheet_updated_at_utc:

                # Update the Google Sheet with data from the Django model
                update_data_in_sheet(spreadsheet_id, row_index, model_instance, credentials)
                print(f"{product} updated on sheets")

            else:
                # Update the Django model with data from the Google Sheet
                update_django_model(model_instance, sheet_row)
                print(f"{product} updated on web")

        else:
            product_instance, created = Product.objects.get_or_create(name=product)

            model_instance = ProductShop.objects.create(
                product=product_instance,
                shop=shop,
                weight=int(sheet_row[2]),
                quantity=sheet_row[3],
                expiration_date=sheet_row[4] if sheet_row[4] else None,
                retail_price=sheet_row[5],
                platform_price=sheet_row[6],
            )

            print(f"{product_instance} created")



def get_data_from_sheet(spreadsheet_id, credentials):
    service = build("sheets", "v4", credentials=credentials)
    sheets = service.spreadsheets()

    result = sheets.values().get(spreadsheetId=spreadsheet_id, range="Sheet1!A2:H1000").execute()
    values = result.get("values", [])

    return values


def update_data_in_sheet(spreadsheet_id, row_index, model_instance, credentials):
    service = build("sheets", "v4", credentials=credentials)

    # Prepare the updated row data
    updated_row_data = [
        model_instance.weight,
        model_instance.quantity,
        model_instance.expiration_date.strftime("%Y-%m-%d") if model_instance.expiration_date else None,
        float(model_instance.retail_price),
        float(model_instance.platform_price),
        model_instance.updated_at.strftime("%m/%d/%Y %H:%M:%S") if model_instance.updated_at else None
    ]

    # Update the Google Sheet with the updated row data
    range_to_update = f'Sheet1!C{row_index + 2}:H{row_index + 2}'
    update_body = {"values": [updated_row_data]}

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_to_update,
        body=update_body,
        valueInputOption="RAW"
    ).execute()


def update_django_model(model_instance, sheet_row):
    model_instance.weight = sheet_row[2]
    model_instance.quantity = sheet_row[3]
    model_instance.expiration_date = sheet_row[4] if model_instance.expiration_date else None
    model_instance.retail_price = sheet_row[5]
    model_instance.platform_price = sheet_row[6]

    # Save the changes to the Django model
    model_instance.save()