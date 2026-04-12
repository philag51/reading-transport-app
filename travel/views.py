import requests as rq
import os
import folium as fl
from django.http import JsonResponse
from django.shortcuts import render
import xml.etree.ElementTree as ET
from datetime import datetime, date, timedelta, timezone
from zoneinfo import ZoneInfo

rb_colors = {
    
    "1": "#000000",
    "2": "#0EBD13",
    "2a": "#0EBD13",
    "3": "#B2991F",
    "4": "#A38142",
    "4a": "#A38142",
    "5": "#007670",
    "6": "#007670",
    "6a": "#007670",
    "9": "#097306",
    "9a": "#097306",
    "9b": "#097306",
    "10": "#d11608",
    "11": "#8c5014",
    "12": "#ff8000",
    "13": "#ff8000",
    "14": "#ff8000",
    "15": "#0095ff",
    "15a": "#0095ff",
    "16": "#0095ff",
    "17": "#3E2B89",
    "18": "#097306",
    "19a": "#ff8000",
    "19b": "#ff8000",
    "19c": "#ff8000",
    "20": "#352f29",
    "21": "#6B1425",
    "22": "#C9097F",
    "23": "#8B429D",
    "24": "#8B429D",
    "25": "#C9097F",
    "25a": "#C9097F",
    "26": "#FFDD00",
    "28": "#02959D",
    "28a": "#02959D",
    "29": "#8B429D",
    "29a": "#8B429D",
    "33": "#0F378A",
    "43": "#1A42AE",
    "50": "#004534",
    "50a": "#004534",
    "300": "#1E3991",
    "500": "#7B0B0B",
    "600": "#004534",
    "650": "#004534",
    "701": "#097306",
    "702": "#097306",

}

rb_brands = {
    "1": "images/Reading Buses Route logos/jetblack.png",
    "2": "images/Reading Buses Route logos/lime.png",
    "2a": "images/Reading Buses Route logos/lime.png",
    "3": "images/Reading Buses Route logos/leopard.png",
    "4": "images/Reading Buses Route logos/lion.png",
    "4a": "images/Reading Buses Route logos/lion.png",
    "5": "images/Reading Buses Route logos/emerald.png",
    "6": "images/Reading Buses Route logos/emerald.png",
    "6a": "images/Reading Buses Route logos/emerald.png",
    "9": "images/Reading Buses Route logos/buzz.png",
    "9a": "images/Reading Buses Route logos/buzz.png",
    "9b": "images/Reading Buses Route logos/buzz.png",
    "11": "images/Reading Buses Route logos/bronze.png",
    "13": "images/Reading Buses Route logos/orange.png",
    "14": "images/Reading Buses Route logos/orange.png",
    "15": "images/Reading Buses Route logos/sky blue.png",
    "15a": "images/Reading Buses Route logos/sky blue.png",
    "16": "images/Reading Buses Route logos/sky blue.png",
    "17": "images/Reading Buses Route logos/purple.png",
    "18": "images/Reading Buses Route logos/buzz.png",
    "19a": "images/Reading Buses Route logos/little oranges.png",
    "19b": "images/Reading Buses Route logos/little oranges.png",
    "19c": "images/Reading Buses Route logos/little oranges.png",
    "20": "images/Reading Buses Route logos/white knight.png",
    "21": "images/Reading Buses Route logos/claret.png",
    "22": "images/Reading Buses Route logos/pink.png",
    "23": "images/Reading Buses Route logos/berry.png",
    "24": "images/Reading Buses Route logos/berry.png",
    "25": "images/Reading Buses Route logos/pink.png",
    "25a": "images/Reading Buses Route logos/pink.png",
    "26": "images/Reading Buses Route logos/yellow.png",
    "28": "images/Reading Buses Route logos/aqua.png",
    "28a": "images/Reading Buses Route logos/aqua.png",
    "29": "images/Reading Buses Route logos/little berries.png",
    "29a": "images/Reading Buses Route logos/little berries.png",
    "33": "images/Reading Buses Route logos/royal blue.png",
    "43": "images/Reading Buses Route logos/azure.png",
    "50": "images/Reading Buses Route logos/greenwave.png",
    "50a": "images/Reading Buses Route logos/greenwave.png",
    "300": "images/Reading Buses Route logos/hospital p&r.png",
    "500": "images/Reading Buses Route logos/wt p&r.png",
    "600": "images/Reading Buses Route logos/mereoak p&r.png",
    "650": "images/Reading Buses Route logos/mereoak p&r.png",
    "701": "images/Reading Buses Route logos/london line.png",
    "702": "images/Reading Buses Route logos/london line.png",
}

companies = {
        "RBUS" : "Reading Buses",
        "NADS" : "Newbury & District",
        "RRAR" : "RailAir (First)",
        "CTNY" : "Thames Valley Buses",
        "THTR" : "Thames Travel",
        "CSLB" : "Carousel Buses",
    }

oplogos = {
        "RBUS" : "images/rb-logo.png",
        "NADS" : "images/nd-logo.png",
        "CTNY" : "images/tv-logo.jpg",
        "THTR" : "images/tt-logo.png",
        "CSLB" : "images/cb-logo.png",
        "RRAR" : "images/railair-logo.png",
}

railops = {
    "GW": "images/gwr-logo.png",
    "XC": "images/xc-logo.jpg",
    "XR": "images/el-logo.png",
    "SW": "images/swr-logo.png",
}

API_TOKEN = os.getenv("API_TOKEN")


routes = []

def home(request):
    return render(request, "travel/home.html")

def stop_search(request):
    query = request.GET.get("q", "").lower()

    if not query:
        return JsonResponse([], safe=False)
    
    url = 'https://reading-opendata.r2p.com/api/v1/busstops?api_token=13te0wZEgrDO9qgjYCfmfPzIiBxglyJVO3BpFUj6dIIO1crmeJYE94rS9RkR'
    response = rq.get(url)
    data = response.json()

    seen = set()
    matches = []

    for stop in data:
        desc = stop["description"].strip()

        # Only match user query
        if query in desc.lower():

            # Skip if we've already shown this exact direction/named stop
            if desc in seen:
                continue

            seen.add(desc)

            matches.append({
                "description": desc,
                "location_code": stop["location_code"]
            })

    return JsonResponse(matches[:50], safe=False)


def buses(request):
    departures = []
    stop_name = None
    error = None

    if request.method == "POST":
        location_code = request.POST.get("location_code")

        if location_code:
            siri_url = (
                f"https://reading-opendata.r2p.com/api/v1/siri-sm?"
                f"api_token={API_TOKEN}&location={location_code}"
            )
            response = rq.get(siri_url, timeout=8)

            if response.status_code != 200:
                error = "Could not fetch live bus data."
            else:
                ns = {'siri': 'http://www.siri.org.uk/siri'}
                root = ET.fromstring(response.content)

                delivery = root.find('.//siri:StopMonitoringDelivery', ns)
                name_elem = delivery.find('siri:MonitoringName', ns) if delivery is not None else None
                stop_name = name_elem.text if name_elem is not None else "Unknown Stop"

                visits = root.findall('.//siri:MonitoredStopVisit', ns)

                now = datetime.now(timezone.utc)
                day_end = now.replace(hour=23, minute=59, second=59, microsecond=0)

                for visit in visits:
                    journey = visit.find('siri:MonitoredVehicleJourney', ns)
                    if journey is None:
                        continue

                    line = journey.find('siri:LineRef', ns)
                    dest = journey.find('siri:DestinationName', ns)
                    call = journey.find('siri:MonitoredCall', ns)
                    operator_code = journey.find('siri:OperatorRef', ns)
                    aimed = call.find('siri:AimedDepartureTime', ns) if call is not None else None

                    if aimed is None or not aimed.text:
                        continue

                    operator_code_text = operator_code.text if operator_code is not None else None
                    operator = companies.get(operator_code_text, "?")
                    logo = oplogos.get(operator_code_text, None)

                    dt = datetime.fromisoformat(aimed.text.replace("Z", "+00:00"))

                    if not (now <= dt <= day_end):
                        continue

                    mins = int((dt - now).total_seconds() // 60)

                    if mins <= 2:
                        mins = "Due"
                    elif mins > 59:
                        mins = dt.strftime("%H:%M")
                    else:
                        mins = f"{mins} min"

                    departures.append({
                        "operator": operator,
                        "logo": logo,
                        "route": line.text if line is not None else "?",
                        "destination": dest.text if dest is not None else "?",
                        "time": dt.strftime("%H:%M"),
                        "mins": mins,
                        "dt": dt,
                    })

            departures.sort(key=lambda x: x["dt"])
            departures = departures[:10]

            if not departures and error is None:
                error = f'No departures from this stop for today'

    for d in departures:
        d.pop("dt", None)

    return render(request, "travel/buses.html", {
        "departures": departures,
        "stop_name": stop_name,
        "error": error,
    })

def tracker(request):
    return render(request, "travel/tracker.html")


def tracker_data(request):
    url = f'https://reading-opendata.r2p.com/api/v1/vehicle-positions?api_token=13te0wZEgrDO9qgjYCfmfPzIiBxglyJVO3BpFUj6dIIO1crmeJYE94rS9RkR'
    try:
        response = rq.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return JsonResponse({"error": "Failed to fetch vehicle positions"}, status=502)

    buses = []
    for bus in data:
        if bus.get("operator") != "RBUS":
            continue

        try:
            route = str(bus.get("service", "")).strip()
            buses.append({
                "brand": rb_brands.get(route, "images/rb-logo-transparent.png"),
                "vehicle": str(bus.get("vehicle", "")),
                "route": route,
                "lat": float(bus["latitude"]),
                "lon": float(bus["longitude"]),
                "seen": bus.get("observed"),
                "color": rb_colors.get(route, "#857e7e"),
            })
        except Exception:
            continue

    return JsonResponse(buses, safe=False)
    

user = os.getenv("user")
password = os.getenv("password")

stations = {
    "RDG": "Reading (Main)",
    "RDW": "Reading West",
    "RGP": "Reading Green Park",
    "TLH": "Tilehurst"
}

tz = ZoneInfo("Europe/London")

def trains(request):
    rails = None
    station_name = None
    error = None

    if request.method == "POST":
        station_code = request.POST.get("station_code")

        if station_code not in stations:
            error = "Invalid station selected."
        else:
            station_name = stations[station_code]
            url = f"https://api.rtt.io/api/v1/json/search/{station_code}"
            response = rq.get(url, auth=(user, password))

            if response.status_code != 200:
                error = "Could not fetch train data."
            else:
                data = response.json()
                rails = []

                services = data.get("services") or []

                for service in services[:10]:
                    service = service or {}
                    loc = service.get("locationDetail") or {}

                    exp_time = loc.get("gbttBookedDeparture")
                    rt_dep = loc.get("realtimeDeparture")

                    destination_list = loc.get("destination") or []
                    if destination_list and destination_list[0]:
                        destination = destination_list[0].get("description", "?")
                    else:
                        destination = "?"

                    if not exp_time or exp_time == "?":
                        continue

                    try:
                        dep_time = datetime.strptime(exp_time, "%H%M").time()
                    except ValueError:
                        continue

                    now = datetime.now(tz)
                    dep_dt = datetime.combine(date.today(), dep_time, tzinfo=tz)

                    if dep_dt < now - timedelta(hours=6):
                        dep_dt += timedelta(days=1)

                    if dep_dt < now:
                        continue

                    if not rt_dep or rt_dep == "?":
                        final_dt = dep_dt
                    else:
                        try:
                            final_dep = datetime.strptime(rt_dep, "%H%M").time()
                            final_dt = datetime.combine(date.today(), final_dep, tzinfo=tz)

                            if final_dt < now - timedelta(hours=6):
                                final_dt += timedelta(days=1)
                        except ValueError:
                            final_dt = dep_dt

                    operator = service.get("atocName", "?")
                    operator_code = service.get("atocCode", "?")
                    logo = railops.get(operator_code)

                    delay = int((final_dt - dep_dt).total_seconds() // 60)
                    if delay <= 0:
                        status = "On time"
                    else:
                        status = f"Delayed by {delay} mins, new departure time is {final_dt.strftime('%H:%M')}"

                    rails.append({
                        "service": service.get("serviceUid", "?"),
                        "operator": operator,
                        "logo": logo,
                        "destination": destination,
                        "time": final_dt.strftime("%H:%M"),
                        "platform": loc.get("platform", "N/A"),
                        "status": status,
                        "dt": final_dt,
                    })

                rails.sort(key=lambda x: x["dt"])
                rails = rails[:10]

                for r in rails:
                    r.pop("dt", None)

    return render(request, "travel/trains.html", {
        "station_name": station_name,
        "trains": rails,
        "error": error,
    })

def about(request):
    return render(request, "travel/about.html")
