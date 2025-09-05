from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("optimal_schedule", host="0.0.0.0", port=8080, stateless_http=True)

@mcp.tool()
def optimal_loads(end_lat: float, end_lon:float, end_time: str, start_lat: float, start_lon:float, start_time: str) -> dict:

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
        List of all loads that exist in the optimal schedule in a dictionary, each load is provided as its unique identifier, revenue, and arrival date and time.
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
        return response.json()
    else:
        print("Request failed:", response.status_code, response.text)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")