import requests
import json


def __inmet_data():
    url = "https://apiprevmet3.inmet.gov.br/avisos/ativos"
    page = requests.get(url)

    content = page.content
    return json.loads(content)


def find_alerts_by_city(code):
    data = __inmet_data()
    today_alerts = data["hoje"] + data["futuro"]

    filtered_alerts = [alert for alert in today_alerts if str(code) in alert["geocodes"]]
    alerts_json = set(json.dumps(alert, sort_keys=True) for alert in filtered_alerts)

    return [json.loads(alert_json) for alert_json in alerts_json]
