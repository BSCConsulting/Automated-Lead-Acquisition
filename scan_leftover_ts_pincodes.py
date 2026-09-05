import harvester

# Gather all PIN codes currently registered for Telangana in TOWN_PINCODE_DB
current_ts_pins = set()
for key, info in harvester.TOWN_PINCODE_DB.items():
    if info.get("state") == "Telangana":
        pincode = info.get("pincode")
        if pincode:
            current_ts_pins.add(pincode)
        for p in info.get("pincodes", []):
            current_ts_pins.add(p)

print(f"Total Telangana PIN codes currently in TOWN_PINCODE_DB: {len(current_ts_pins)}")

LEFTOVER_TS_PINCODES = {
    "1. Hyderabad District": [
        {"pincode": "500006", "area": "Asifnagar / Mallepally, Hyderabad", "type": "Sub Post Office"},
        {"pincode": "500008", "area": "Karwan / Golconda Fort, Hyderabad", "type": "Sub Post Office"},
        {"pincode": "500014", "area": "Jamai Osmania / Vidyanagar, Hyderabad", "type": "Sub Post Office"},
        {"pincode": "500015", "area": "Trimulgherry / Secunderabad Cantonment", "type": "Sub Post Office"},
        {"pincode": "500017", "area": "Habsiguda / NGRI, Hyderabad", "type": "Sub Post Office"},
        {"pincode": "500023", "area": "Moghalpura / Old City, Hyderabad", "type": "Sub Post Office"},
        {"pincode": "500024", "area": "Lalaguda / North Lallaguda, Secunderabad", "type": "Sub Post Office"},
        {"pincode": "500025", "area": "Bolarum / Secunderabad Cantonment", "type": "Sub Post Office"},
        {"pincode": "500026", "area": "Sanjeevareddy Nagar East / BK Guda", "type": "Sub Post Office"},
        {"pincode": "500027", "area": "Gowliguda / Bank Street, Hyderabad", "type": "Sub Post Office"},
        {"pincode": "500035", "area": "Kothapet / Saroornagar Border", "type": "Sub Post Office"},
        {"pincode": "500036", "area": "Saidabad / Malakpet Colony", "type": "Sub Post Office"},
        {"pincode": "500044", "area": "Nallakunta / Barkatpura, Hyderabad", "type": "Sub Post Office"},
        {"pincode": "500045", "area": "Yousufguda / Jubilee Hills Checkpost Zone", "type": "Sub Post Office"},
        {"pincode": "500053", "area": "Falaknuma / Engine Bowli, Hyderabad", "type": "Sub Post Office"},
        {"pincode": "500063", "area": "Tolichowki / Kakatiya Nagar, Hyderabad", "type": "Sub Post Office"},
        {"pincode": "500068", "area": "Nagole / Bandlaguda, Hyderabad", "type": "Sub Post Office"},
        {"pincode": "500080", "area": "Film Nagar / Jubilee Hills Phase 3", "type": "Sub Post Office"},
        {"pincode": "500096", "area": "Borabanda / Site-3, Hyderabad", "type": "Sub Post Office"}
    ],
    "2. Medchal-Malkajgiri District": [
        {"pincode": "500011", "area": "Lothkunta / Alwal Military Hub", "type": "Sub Post Office"},
        {"pincode": "500042", "area": "Balanagar Industrial Estate", "type": "Sub Post Office"},
        {"pincode": "500047", "area": "Malkajgiri Main Town", "type": "Sub Post Office"},
        {"pincode": "500051", "area": "Cherlapally Industrial Park", "type": "Sub Post Office"},
        {"pincode": "500054", "area": "IDA Jeedimetla, Quthbullapur", "type": "Sub Post Office"},
        {"pincode": "500055", "area": "Gajularamaram / Quthbullapur Suburb", "type": "Sub Post Office"},
        {"pincode": "500067", "area": "Suraram / Malla Reddy Hospital Zone", "type": "Sub Post Office"},
        {"pincode": "500076", "area": "ECIL / Kushaiguda Industrial Zone", "type": "Sub Post Office"},
        {"pincode": "500083", "area": "Shapur Nagar, Jeedimetla", "type": "Sub Post Office"},
        {"pincode": "500090", "area": "Pragathi Nagar / Bachupally Road", "type": "Sub Post Office"},
        {"pincode": "500097", "area": "Chengicherla / Boduppal North", "type": "Sub Post Office"},
        {"pincode": "501401", "area": "Medchal Collectorate Zone", "type": "Head Post Office"},
        {"pincode": "501403", "area": "Gundlapochampally, Medchal", "type": "Sub Post Office"}
    ],
    "3. Rangareddy District": [
        {"pincode": "500019", "area": "Chandanagar / Serilingampally Hub", "type": "Sub Post Office"},
        {"pincode": "500030", "area": "Hyderguda / Attapur Commercial Hub", "type": "Sub Post Office"},
        {"pincode": "500050", "area": "Deepthisrinagar / Miyapur East", "type": "Sub Post Office"},
        {"pincode": "500075", "area": "Gandipet / Ocean Park Zone", "type": "Sub Post Office"},
        {"pincode": "500086", "area": "Sun City / Bandlaguda Jagir", "type": "Sub Post Office"},
        {"pincode": "500089", "area": "Puppalaguda / Financial District Access", "type": "Sub Post Office"},
        {"pincode": "500093", "area": "Kismatpur / Abhyudaya Nagar", "type": "Sub Post Office"},
        {"pincode": "501218", "area": "GMR Hyderabad Airport Complex, Shamshabad", "type": "Sub Post Office"},
        {"pincode": "501503", "area": "Chevella Main Town", "type": "Sub Post Office"},
        {"pincode": "501504", "area": "CBIT Campus, Moinabad", "type": "Sub Post Office"},
        {"pincode": "501510", "area": "Manchal Rural, Ibrahimpatnam", "type": "Branch Post Office"},
        {"pincode": "509216", "area": "Farooqnagar RS, Shadnagar", "type": "Sub Post Office"},
        {"pincode": "509228", "area": "Kothur Industrial SEZ", "type": "Sub Post Office"}
    ],
    "4. Hanamkonda (Warangal Urban) District": [
        {"pincode": "506001", "area": "Chowrastha / Hanamkonda Head Office", "type": "Head Post Office"},
        {"pincode": "506004", "area": "Kakatiya University Campus, Hanamkonda", "type": "Sub Post Office"},
        {"pincode": "506009", "area": "Naimnagar / Waddepally, Hanamkonda", "type": "Sub Post Office"},
        {"pincode": "506015", "area": "Hasanparthy Suburb", "type": "Branch Post Office"},
        {"pincode": "505471", "area": "Veenavanka Border, Bheemadevarapally", "type": "Branch Post Office"}
    ],
    "5. Warangal District": [
        {"pincode": "506002", "area": "Warangal Grain Market / Mandi", "type": "Sub Post Office"},
        {"pincode": "506007", "area": "Warangal Fort / Mattewada", "type": "Sub Post Office"},
        {"pincode": "506013", "area": "MGM Hospital Zone, Warangal", "type": "Sub Post Office"},
        {"pincode": "506132", "area": "Narsampet RTC Bustand Zone", "type": "Sub Post Office"},
        {"pincode": "506164", "area": "Parkal Commercial Center", "type": "Sub Post Office"},
        {"pincode": "506330", "area": "Kakatiya Mega Textile Park, Geesugonda", "type": "Sub Post Office"}
    ],
    "6. Khammam District": [
        {"pincode": "507002", "area": "Wyra Road, Khammam", "type": "Sub Post Office"},
        {"pincode": "507003", "area": "Khammam Trunk Road Commercial Hub", "type": "Sub Post Office"},
        {"pincode": "507115", "area": "Sathupally RTC Bustand Zone", "type": "Sub Post Office"},
        {"pincode": "507160", "area": "Nelakondapalli Heritage Center", "type": "Sub Post Office"},
        {"pincode": "507165", "area": "Wyra Reservoir Zone", "type": "Sub Post Office"},
        {"pincode": "507203", "area": "Madhira Railway Station Zone", "type": "Sub Post Office"},
        {"pincode": "507206", "area": "Bonakal RS", "type": "Branch Post Office"},
        {"pincode": "507208", "area": "Penuballi Rural", "type": "Branch Post Office"}
    ],
    "7. Bhadradri Kothagudem District": [
        {"pincode": "507101", "area": "Singareni Collieries HQs, Kothagudem", "type": "Head Post Office"},
        {"pincode": "507111", "area": "Bhadrachalam Temple Complex", "type": "Sub Post Office"},
        {"pincode": "507114", "area": "Burgampahad ITC Paperboards Factory", "type": "Sub Post Office"},
        {"pincode": "507115", "area": "KTPS Power Plant, Palvancha", "type": "Sub Post Office"},
        {"pincode": "507116", "area": "Heavy Water Plant, Aswapuram", "type": "Sub Post Office"},
        {"pincode": "507117", "area": "Manuguru Coal Washery Zone", "type": "Sub Post Office"},
        {"pincode": "507123", "area": "Yellandu Coal Belt", "type": "Sub Post Office"}
    ],
    "8. Karimnagar District": [
        {"pincode": "505001", "area": "Tower Circle, Karimnagar", "type": "Head Post Office"},
        {"pincode": "505002", "area": "Collectorate Complex, Karimnagar", "type": "Sub Post Office"},
        {"pincode": "505468", "area": "Huzurabad RTC Bus Stand", "type": "Sub Post Office"},
        {"pincode": "505505", "area": "Manakondur Rural", "type": "Branch Post Office"},
        {"pincode": "505527", "area": "Lower Manair Dam Tourism Zone, Thimmapur", "type": "Sub Post Office"}
    ],
    "9. Peddapalli District": [
        {"pincode": "505208", "area": "NTPC Ramagundam Power Station", "type": "Sub Post Office"},
        {"pincode": "505209", "area": "Godavarikhani Main Town", "type": "Sub Post Office"},
        {"pincode": "505215", "area": "FCIL Fertilizer City, Ramagundam", "type": "Sub Post Office"},
        {"pincode": "505172", "area": "Peddapalli RS Zone", "type": "Sub Post Office"},
        {"pincode": "505184", "area": "Manthani Heritage Town", "type": "Sub Post Office"}
    ],
    "10. Jagtial District": [
        {"pincode": "505327", "area": "Jagtial Collectorate & Fort Zone", "type": "Head Post Office"},
        {"pincode": "505326", "area": "Korutla Weavers Colony", "type": "Sub Post Office"},
        {"pincode": "505325", "area": "Metpally Gulf Junction", "type": "Sub Post Office"},
        {"pincode": "505425", "area": "Dharmapuri Godavari River Ghats", "type": "Sub Post Office"}
    ],
    "11. Rajanna Sircilla District": [
        {"pincode": "505301", "area": "Textile Park, Sircilla", "type": "Sub Post Office"},
        {"pincode": "505302", "area": "Vemulawada Temple Complex", "type": "Sub Post Office"},
        {"pincode": "505305", "area": "Yellareddypet Main Road", "type": "Sub Post Office"}
    ],
    "12. Nizamabad District": [
        {"pincode": "503001", "area": "Nizamabad Head Office / Fort", "type": "Head Post Office"},
        {"pincode": "503002", "area": "Khaleelwadi Commercial Belt, Nizamabad", "type": "Sub Post Office"},
        {"pincode": "503003", "area": "Phulong / Armoor Road, Nizamabad", "type": "Sub Post Office"},
        {"pincode": "503185", "area": "Bodhan Sugar Factory Area", "type": "Sub Post Office"},
        {"pincode": "503224", "area": "Armoor Perkit Junction", "type": "Sub Post Office"},
        {"pincode": "503175", "area": "Telangana University Campus, Dichpally", "type": "Sub Post Office"}
    ],
    "13. Kamareddy District": [
        {"pincode": "503111", "area": "Kamareddy Station Road", "type": "Head Post Office"},
        {"pincode": "503187", "area": "Banswada RTC Complex", "type": "Sub Post Office"},
        {"pincode": "503122", "area": "Yellareddy Forest Zone", "type": "Sub Post Office"},
        {"pincode": "503123", "area": "Domakonda Fort Complex", "type": "Sub Post Office"}
    ],
    "14. Adilabad District": [
        {"pincode": "504001", "area": "Adilabad Cotton Market Yard", "type": "Head Post Office"},
        {"pincode": "504002", "area": "Mavala Industrial Zone, Adilabad", "type": "Sub Post Office"},
        {"pincode": "504311", "area": "Utnoor ITDA Agency Complex", "type": "Sub Post Office"}
    ],
    "15. Mancherial District": [
        {"pincode": "504208", "area": "Mancherial IB Chowrasta", "type": "Head Post Office"},
        {"pincode": "504251", "area": "Bellampalle Mining Officers Colony", "type": "Sub Post Office"},
        {"pincode": "504231", "area": "Mandamarri Coal Belt", "type": "Sub Post Office"},
        {"pincode": "504216", "area": "Singareni Thermal Power Plant, Jaipur", "type": "Sub Post Office"}
    ],
    "16. Nirmal District": [
        {"pincode": "504106", "area": "Nirmal Toy Colony / Fort", "type": "Head Post Office"},
        {"pincode": "504103", "area": "Bhainsa Cotton Market", "type": "Sub Post Office"},
        {"pincode": "504101", "area": "Basar Saraswati Temple Complex", "type": "Sub Post Office"},
        {"pincode": "504203", "area": "Khanapur Kadem Dam Zone", "type": "Sub Post Office"}
    ],
    "17. Kumuram Bheem Asifabad District": [
        {"pincode": "504293", "area": "Asifabad District HQs Complex", "type": "Head Post Office"},
        {"pincode": "504296", "area": "Sirpur Paper Mills (SPM), Kagaznagar", "type": "Sub Post Office"},
        {"pincode": "504299", "area": "Sirpur-T Railway Station", "type": "Sub Post Office"}
    ],
    "18. Nalgonda District": [
        {"pincode": "508001", "area": "Nalgonda Clock Tower", "type": "Head Post Office"},
        {"pincode": "508002", "area": "NG College Campus, Nalgonda", "type": "Sub Post Office"},
        {"pincode": "508207", "area": "Miryalaguda Rice Mill Industrial SEZ", "type": "Sub Post Office"},
        {"pincode": "508202", "area": "Nagarjuna Sagar Dam Hydro Project", "type": "Sub Post Office"},
        {"pincode": "508248", "area": "Devarakonda Fort Zone", "type": "Sub Post Office"}
    ],
    "19. Suryapet District": [
        {"pincode": "508213", "area": "Suryapet Hi-Tech Busstand Zone", "type": "Head Post Office"},
        {"pincode": "508206", "area": "Kodad Highway Junction", "type": "Sub Post Office"},
        {"pincode": "508204", "area": "Huzurnagar Cement Industrial Belt", "type": "Sub Post Office"}
    ],
    "20. Yadadri Bhuvanagiri District": [
        {"pincode": "508116", "area": "Bhongir Fort & RS Zone", "type": "Head Post Office"},
        {"pincode": "508115", "area": "Yadadri Temple Hill Top Complex", "type": "Sub Post Office"},
        {"pincode": "508252", "area": "Choutuppal Pharma Industrial SEZ", "type": "Sub Post Office"},
        {"pincode": "508284", "area": "Pochampally Handloom Weavers Park", "type": "Sub Post Office"}
    ],
    "21. Mahabubnagar District": [
        {"pincode": "509001", "area": "Mahabubnagar Clock Tower", "type": "Head Post Office"},
        {"pincode": "509002", "area": "New Town, Mahabubnagar", "type": "Sub Post Office"},
        {"pincode": "509301", "area": "Jadcherla ITI Industrial Park", "type": "Sub Post Office"}
    ],
    "22. Nagarkurnool District": [
        {"pincode": "509209", "area": "Nagarkurnool Collectorate Zone", "type": "Head Post Office"},
        {"pincode": "509375", "area": "Achampet Forest Agency Hub", "type": "Sub Post Office"},
        {"pincode": "509324", "area": "Kalwakurthy RTC Complex", "type": "Sub Post Office"},
        {"pincode": "509102", "area": "Kollapur Palace Zone", "type": "Sub Post Office"}
    ],
    "23. Wanaparthy District": [
        {"pincode": "509103", "area": "Wanaparthy Palace & College Zone", "type": "Head Post Office"},
        {"pincode": "509104", "area": "Pebbair NH-44 Market", "type": "Sub Post Office"},
        {"pincode": "509381", "area": "Kothakota Highway Junction", "type": "Sub Post Office"}
    ],
    "24. Jogulamba Gadwal District": [
        {"pincode": "509125", "area": "Gadwal Fort & Saree Weavers Zone", "type": "Head Post Office"},
        {"pincode": "509152", "area": "Alampur Jogulamba Temple Complex", "type": "Sub Post Office"}
    ],
    "25. Narayanpet District": [
        {"pincode": "509210", "area": "Narayanpet Saree & Commercial Hub", "type": "Head Post Office"},
        {"pincode": "509339", "area": "Kosgi Commercial Market", "type": "Sub Post Office"},
        {"pincode": "509208", "area": "Makthal Highway Junction", "type": "Sub Post Office"}
    ],
    "26. Siddipet District": [
        {"pincode": "502103", "area": "Siddipet Collectorate & IT Tower Zone", "type": "Head Post Office"},
        {"pincode": "502278", "area": "Gajwel Education Hub", "type": "Sub Post Office"},
        {"pincode": "502108", "area": "Dubbak Weavers Zone", "type": "Sub Post Office"},
        {"pincode": "505467", "area": "Husnabad Commercial Center", "type": "Sub Post Office"}
    ],
    "27. Medak District": [
        {"pincode": "502110", "area": "Medak Cathedral & Church Zone", "type": "Head Post Office"},
        {"pincode": "502313", "area": "Narsapur Forest & Industrial Zone", "type": "Sub Post Office"},
        {"pincode": "502334", "area": "Toopran NH-44 Industrial Park", "type": "Sub Post Office"}
    ],
    "28. Sangareddy District": [
        {"pincode": "502001", "area": "Sangareddy District HQs", "type": "Head Post Office"},
        {"pincode": "502032", "area": "Ameenpur Municipal Corporation", "type": "Sub Post Office"},
        {"pincode": "502220", "area": "Zaheerabad NIMZ Industrial Zone", "type": "Sub Post Office"},
        {"pincode": "502285", "area": "IIT Hyderabad Campus, Kandi", "type": "Sub Post Office"},
        {"pincode": "502319", "area": "Patancheru Industrial Estate", "type": "Sub Post Office"},
        {"pincode": "502325", "area": "Bollaram IDA Zone", "type": "Sub Post Office"}
    ],
    "29. Vikarabad District": [
        {"pincode": "501101", "area": "Vikarabad Railway & Ananthagiri Zone", "type": "Head Post Office"},
        {"pincode": "501141", "area": "Tandur Tandur Stone & Cement Hub", "type": "Sub Post Office"},
        {"pincode": "501501", "area": "Pargi Commercial Junction", "type": "Sub Post Office"}
    ],
    "30. Jangaon District": [
        {"pincode": "506167", "area": "Jangaon RTC Complex & Railway Station", "type": "Head Post Office"},
        {"pincode": "506144", "area": "Station Ghanpur Junction", "type": "Sub Post Office"},
        {"pincode": "506252", "area": "Palakurthi Heritage Center", "type": "Sub Post Office"}
    ],
    "31. Jayashankar Bhupalpally District": [
        {"pincode": "506169", "area": "Bhupalpally Coal Mines Complex", "type": "Head Post Office"},
        {"pincode": "506504", "area": "Kaleshwaram Godavari Lift Irrigation Site", "type": "Sub Post Office"}
    ],
    "32. Mulugu District": [
        {"pincode": "506343", "area": "Mulugu District Collectorate Zone", "type": "Head Post Office"},
        {"pincode": "506165", "area": "Eturnagaram Tribal Agency Complex", "type": "Sub Post Office"},
        {"pincode": "506344", "area": "Laknavaram Tourism Zone, Govindaraopet", "type": "Sub Post Office"}
    ],
    "33. Mahabubabad District": [
        {"pincode": "506101", "area": "Mahabubabad Railway Junction", "type": "Head Post Office"},
        {"pincode": "506381", "area": "Dornakal Railway Junction", "type": "Sub Post Office"},
        {"pincode": "506163", "area": "Thorrur Commercial Hub", "type": "Sub Post Office"}
    ]
}

total_leftover_ts_pins = sum(len(pins) for pins in LEFTOVER_TS_PINCODES.values())
print(f"Total Leftover TS Postal PIN Codes & Sub-Office Hubs Identified: {total_leftover_ts_pins}")
