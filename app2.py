from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("optimal_loads", host="0.0.0.0", port=8080, stateless_http=True)

@mcp.tool()
def optimal_loads(end_lat: float, end_lon:float, end_time: str, start_lat: float, start_lon:float, start_time: str) -> list:

    """
    Gets Optimal Schedule of truck loads from given start and end locations, dates, and times.
    
    Args:
        end_lat : Ending location's latitude
        end_lon : Ending location's longitude
        end_time : Ending location's date and time
        start_lat : Start location's latitude
        start_lon : Start location's longitude
        start_time : Start location's datee and time
    Returns:
        List of all loads that exist in the optimal schedule in a dictionary, each load is provided as its unique identifier, revenue, and arrival date and time, along with total revenue for the entire schedule.
    """

    #xfwd = os.getenv("X-FWD")
    #xauth = os.getenv("X-AUTH")
    #authorization = os.getenv("AUTHORIZATION")

    url = "https://cloud-tunnel.endpoints.wgs-ptv-tools.cloud.goog"

    headers = {
        "X-FWD": "http://evalinno-agentic-ltchat-cmp-preview.dev.lkw-walter.com/evalinno-agentic-ltchat-cmp-preview/api/maximize_revenue",
        "X-AUTH": "wT6vNTkzKXH8E7jOfA5ay4cHGwoJPhOc2XS7UyhVWnQ",
        "Authorization": "Basic YWdlbnRpY19sdGNoYXRfZHM6dkFDMEExdnBLUDlxQldQc0tDWWRCYjQ3",
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "end_lat": end_lat,
        "end_lon": end_lon,
        "end_time": end_time,
        "start_lat": start_lat,
        "start_lon": start_lon,
        "start_time": start_time
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.ok:
        #print(response.json())
        all_loads =  response.json()
        orders_summary = []
        total_revenue = all_loads["total_revenue"]
        for order in all_loads["schedule"]:
            summary = {
                "position_number": order["postion_number"],
                "pickup_address": order["pickup_adr"],
                "pickup_window": f'FROM {order["pickup_rta_from"]} TO {order["pickup_rta_to"]}',
                "delivery_address": order["delivery_adr"],
                "delivery_window": f'FROM {order["delivery_rta_from"]} TO {order["delivery_rta_to"]}',
                "revenue": order["revenue"]
            }
            orders_summary.append(summary)
        orders_summary.append({"total_revenue": total_revenue})
        return orders_summary
        #return response.json()
    else:
        print("Request failed:", response.status_code, response.text)

@mcp.tool()
def direct_loads(date: str, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> list:
    """
    Gets direct loads of trucks from given start and end locations, and starting date.
    
    Args:
        date : Starting date
        start_lat : Start location's latitude
        start_lon : Start location's longitude
        end_lat : Ending location's latitude
        end_lon : Ending location's longitude
            
    Returns:
        List top 5 available direct loads in a list, each load is provided as its unique identifier, revenue, pickup-address, delivery-address, pickup time window, and delivery time window.
    """

    url = "https://cloud-tunnel.endpoints.wgs-ptv-tools.cloud.goog"

    headers = {
        "X-FWD": "http://evalinno-agentic-ltchat-cmp-preview.dev.lkw-walter.com/evalinno-agentic-ltchat-cmp-preview/api/direct_search",
        "X-AUTH": "wT6vNTkzKXH8E7jOfA5ay4cHGwoJPhOc2XS7UyhVWnQ",
        "Authorization": "Basic YWdlbnRpY19sdGNoYXRfZHM6dkFDMEExdnBLUDlxQldQc0tDWWRCYjQ3",
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "date": date,
        "end_lat": end_lat,
        "end_lon": end_lon,
        "start_lat": start_lat,
        "start_lon": start_lon
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.ok:
        all_loads =  response.json()
        orders_summary = []
        for order in all_loads["orders"]:
            summary = {
                "position_number": order["postion_number"],
                "pickup_address": order["pickup_adr"],
                "pickup_window": f'FROM {order["pickup_rta_from"]} TO {order["pickup_rta_to"]}',
                "delivery_address": order["delivery_adr"],
                "delivery_window": f'FROM {order["delivery_rta_from"]} TO {order["delivery_rta_to"]}',
                "revenue": order["revenue"]
            }
            orders_summary.append(summary)
        return orders_summary
    else:
        print("Request failed:", response.status_code, response.text)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")