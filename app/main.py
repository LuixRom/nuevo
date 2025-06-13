from playwright.sync_api import sync_playwright
import boto3
import uuid

def lambda_handler(event=None, context=None):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://ultimosismo.igp.gob.pe/ultimo-sismo/sismos-reportados", timeout=60000)
        page.wait_for_selector("table")  # Esperar a que cargue la tabla

        rows = page.query_selector_all("tbody tr")[:10]
        data = []

        for i, row in enumerate(rows):
            cells = row.query_selector_all("td")
            data.append({
                "id": str(uuid.uuid4()),
                "#": i+1,
                "reporte": cells[0].inner_text(),
                "referencia": cells[1].inner_text(),
                "fecha_hora": cells[2].inner_text(),
                "magnitud": cells[3].inner_text(),
                "link": "https://ultimosismo.igp.gob.pe/ultimo-sismo/sismos-reportados"
            })

        browser.close()

    # Subir a DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TablaWebScrapping')

    scan = table.scan()
    with table.batch_writer() as batch:
        for item in scan.get("Items", []):
            batch.delete_item(Key={"id": item["id"]})

    for item in data:
        table.put_item(Item=item)

    return {
        "statusCode": 200,
        "body": data
    }
