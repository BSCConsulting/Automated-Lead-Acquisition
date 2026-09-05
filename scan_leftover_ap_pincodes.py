import harvester

# Gather all PIN codes currently registered for Andhra Pradesh in TOWN_PINCODE_DB
current_ap_pins = set()
for key, info in harvester.TOWN_PINCODE_DB.items():
    if info.get("state") == "Andhra Pradesh":
        pincode = info.get("pincode")
        if pincode:
            current_ap_pins.add(pincode)
        for p in info.get("pincodes", []):
            current_ap_pins.add(p)

print(f"Total AP PIN codes currently in TOWN_PINCODE_DB: {len(current_ap_pins)}")

# Define comprehensive district-by-district PIN code mapping for Andhra Pradesh
# covering additional Sub-Post Offices (S.O.) and Branch Post Offices (B.O.)
LEFTOVER_AP_PINCODES = {
    "1. NTR District": [
        {"pincode": "520003", "area": "Satyanarayanapuram, Vijayawada", "type": "Sub Post Office"},
        {"pincode": "520004", "area": "Gunadala, Vijayawada", "type": "Sub Post Office"},
        {"pincode": "520007", "area": "Labbipet, Vijayawada", "type": "Sub Post Office"},
        {"pincode": "520008", "area": "Patamata, Vijayawada", "type": "Sub Post Office"},
        {"pincode": "520010", "area": "Mogalrajapuram, Vijayawada", "type": "Sub Post Office"},
        {"pincode": "520011", "area": "Auto Nagar, Vijayawada", "type": "Sub Post Office"},
        {"pincode": "520012", "area": "Payakapuram, Vijayawada", "type": "Sub Post Office"},
        {"pincode": "520013", "area": "Kandrika, Vijayawada", "type": "Sub Post Office"},
        {"pincode": "520015", "area": "One Town / Kaleswara Rao Market, Vijayawada", "type": "Sub Post Office"},
        {"pincode": "521183", "area": "Pokkunuru, Chandarlapadu", "type": "Branch Post Office"},
        {"pincode": "521184", "area": "Damuluru, Veerullapadu", "type": "Branch Post Office"},
        {"pincode": "521227", "area": "Chemalapadu, A.Konduru", "type": "Branch Post Office"},
        {"pincode": "521237", "area": "Utukuru, Gampalagudem", "type": "Branch Post Office"}
    ],
    "2. Krishna District": [
        {"p21002": "521002", "pincode": "521002", "area": "Chilakalapudi, Machilipatnam", "type": "Sub Post Office"},
        {"pincode": "521003", "area": "Paraspet, Machilipatnam", "type": "Sub Post Office"},
        {"pincode": "521104", "area": "Kesarapalli, Gannavaram", "type": "Sub Post Office"},
        {"pincode": "521110", "area": "Atkur, Unguturu", "type": "Branch Post Office"},
        {"pincode": "521127", "area": "Kaza, Movva", "type": "Branch Post Office"},
        {"pincode": "521136", "area": "Pedasanagallu, Movva", "type": "Branch Post Office"},
        {"pincode": "521150", "area": "Tarikaturu, Kankipadu", "type": "Branch Post Office"},
        {"pincode": "521162", "area": "Gurazada, Pamidimukkala", "type": "Branch Post Office"},
        {"pincode": "521245", "area": "Meduru, Pamidimukkala", "type": "Branch Post Office"},
        {"pincode": "521325", "area": "Interu, Ghantasala", "type": "Branch Post Office"},
        {"pincode": "521328", "area": "Pedana Rural", "type": "Branch Post Office"},
        {"pincode": "521329", "area": "Kuruthipennu / Kruthivennu Coastal", "type": "Branch Post Office"},
        {"pincode": "521345", "area": "Mallavolu, Guduru", "type": "Branch Post Office"}
    ],
    "3. Visakhapatnam District": [
        {"pincode": "530003", "area": "Waltair RS, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530004", "area": "Industrial Estate, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530007", "area": "Naval Base, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530008", "area": "Gandhigram, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530009", "area": "Naval Dockyard, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530012", "area": "Kancharapalem, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530014", "area": "Akkayyapalem, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530015", "area": "Maddilapalem, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530018", "area": "Siripuram, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530022", "area": "Dwarakanagar, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530024", "area": "Industrial Estate North, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530028", "area": "Simhachalam, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530029", "area": "Gopalapatnam RS, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530032", "area": "Steel Plant Township, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530040", "area": "Vepagunta, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530041", "area": "Sujaathanagar, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530043", "area": "Duvvada SEZ, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530044", "area": "Pedagantyada, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530046", "area": "Chinagantyada, Visakhapatnam", "type": "Sub Post Office"},
        {"pincode": "530047", "area": "PM Palem (Pothinamallayya Palem)", "type": "Sub Post Office"},
        {"pincode": "530053", "area": "Gambheeram, Anandapuram", "type": "Sub Post Office"}
    ],
    "4. Anakapalli District": [
        {"pincode": "531002", "area": "Munagapaka, Anakapalli", "type": "Sub Post Office"},
        {"pincode": "531019", "area": "Lalamkoduru, Rambilli", "type": "Branch Post Office"},
        {"pincode": "531020", "area": "Lalam, Atchutapuram", "type": "Branch Post Office"},
        {"pincode": "531022", "area": "Lalam, Kasimkota", "type": "Branch Post Office"},
        {"pincode": "531034", "area": "Tenugupudi, Devarapalli", "type": "Branch Post Office"},
        {"pincode": "531035", "area": "Lakkavarapukota Border, Anakapalli", "type": "Branch Post Office"},
        {"pincode": "531053", "area": "Kothakota, Rolugunta", "type": "Branch Post Office"},
        {"pincode": "531082", "area": "Dharmavaram, Nakkapalli", "type": "Branch Post Office"},
        {"pincode": "531083", "area": "Upamaka, Nakkapalli", "type": "Branch Post Office"},
        {"pincode": "531113", "area": "Komaravolu, Butchayyapeta", "type": "Branch Post Office"},
        {"pincode": "531115", "area": "Vempadu, S.Rayavaram", "type": "Branch Post Office"},
        {"pincode": "531128", "area": "Gudivada, S.Rayavaram", "type": "Branch Post Office"}
    ],
    "5. Alluri Sitharama Raju (ASR) District": [
        {"pincode": "531025", "area": "Minumuluru, Paderu", "type": "Branch Post Office"},
        {"pincode": "531030", "area": "Vanthala, G.Madugula", "type": "Branch Post Office"},
        {"pincode": "531041", "area": "Jolabaput, Munchingiputtu", "type": "Branch Post Office"},
        {"pincode": "531075", "area": "Tajangi, Chintapalle", "type": "Branch Post Office"},
        {"pincode": "531084", "area": "Downuru, Koyyuru", "type": "Branch Post Office"},
        {"pincode": "531112", "area": "Lammasingi (Lambasingi), Chintapalle", "type": "Sub Post Office"},
        {"pincode": "531150", "area": "Padmapuram, Araku Valley", "type": "Branch Post Office"},
        {"pincode": "533287", "area": "Gokavaram Agency Border, Rampachodavaram", "type": "Branch Post Office"},
        {"pincode": "533289", "area": "Musurumilli, Rampachodavaram", "type": "Branch Post Office"},
        {"pincode": "533437", "area": "Labbarthi, Rajavommangi", "type": "Branch Post Office"}
    ],
    "6. Guntur District": [
        {"pincode": "522003", "area": "Kothapet, Guntur", "type": "Sub Post Office"},
        {"pincode": "522004", "area": "Narasaraopet Road, Guntur", "type": "Sub Post Office"},
        {"pincode": "522005", "area": "Brodipet, Guntur", "type": "Sub Post Office"},
        {"pincode": "522007", "area": "Pattabhipuram, Guntur", "type": "Sub Post Office"},
        {"pincode": "522017", "area": "Gorantla, Guntur", "type": "Sub Post Office"},
        {"pincode": "522018", "area": "Nallapadu, Guntur", "type": "Sub Post Office"},
        {"pincode": "522213", "area": "Vejendla, Chebrolu", "type": "Branch Post Office"},
        {"pincode": "522234", "area": "Pusuluru, Pedanandipadu", "type": "Branch Post Office"},
        {"pincode": "522303", "area": "Angalakuduru, Tenali", "type": "Sub Post Office"},
        {"pincode": "522307", "area": "Duggirala Rural", "type": "Branch Post Office"},
        {"pincode": "522502", "area": "Kunchanapalli, Tadepalle", "type": "Sub Post Office"},
        {"pincode": "522508", "area": "Nowlur, Mangalagiri", "type": "Sub Post Office"},
        {"pincode": "522510", "area": "Narakoduru, Chebrolu", "type": "Branch Post Office"}
    ],
    "7. Bapatla District": [
        {"pincode": "522102", "area": "Bapatla Engineering College", "type": "Sub Post Office"},
        {"pincode": "522113", "area": "Suryalanka, Bapatla", "type": "Branch Post Office"},
        {"pincode": "522257", "area": "Jillellamudi, Bhattiprolu", "type": "Branch Post Office"},
        {"pincode": "522264", "area": "Penumudi, Repalle", "type": "Branch Post Office"},
        {"pincode": "523156", "area": "Ithanagar, Chirala", "type": "Sub Post Office"},
        {"pincode": "523157", "area": "Perala, Chirala", "type": "Sub Post Office"},
        {"pincode": "523166", "area": "Vodarevu, Chirala", "type": "Branch Post Office"},
        {"pincode": "523170", "area": "Swarna, Karamchedu", "type": "Branch Post Office"},
        {"pincode": "523262", "area": "Konanki, Martur", "type": "Branch Post Office"}
    ],
    "8. Palnadu District": [
        {"pincode": "522412", "area": "Madugula, Gurazala", "type": "Branch Post Office"},
        {"pincode": "522416", "area": "Poundla, Dachepalle", "type": "Branch Post Office"},
        {"pincode": "522427", "area": "Nagarjunasagar Right Bank, Macherla", "type": "Sub Post Office"},
        {"pincode": "522437", "area": "Sirigiri Padu, Veldurthi", "type": "Branch Post Office"},
        {"pincode": "522602", "area": "Prakashnagar, Narasaraopet", "type": "Sub Post Office"},
        {"pincode": "522611", "area": "Jonnalagadda, Narasaraopet", "type": "Branch Post Office"},
        {"pincode": "522648", "area": "Nujendla Rural, Vinukonda", "type": "Branch Post Office"}
    ],
    "9. Tirupati District": [
        {"pincode": "517502", "area": "KT Road, Tirupati", "type": "Sub Post Office"},
        {"pincode": "517503", "area": "Tirupati South / Korlagunta", "type": "Sub Post Office"},
        {"pincode": "517504", "area": "SV University, Tirupati", "type": "Sub Post Office"},
        {"pincode": "517505", "area": "SV Medical College, Tirupati", "type": "Sub Post Office"},
        {"pincode": "517507", "area": "Tiruchanur, Tirupati", "type": "Sub Post Office"},
        {"pincode": "517510", "area": "Tirumala Hills, Tirupati", "type": "Sub Post Office"},
        {"pincode": "517540", "area": "Tada Rural / Sri City North", "type": "Sub Post Office"},
        {"pincode": "517582", "area": "Gajulamandyam, Renigunta", "type": "Sub Post Office"},
        {"pincode": "517619", "area": "Thottambedu, Srikalahasti", "type": "Branch Post Office"},
        {"pincode": "517640", "area": "Panagal, Srikalahasti", "type": "Sub Post Office"},
        {"pincode": "524124", "area": "Shar (Sriharikota ISRO Center), Sullurpeta", "type": "Sub Post Office"},
        {"pincode": "524132", "area": "Kovurpalli, Gudur", "type": "Branch Post Office"},
        {"pincode": "524410", "area": "Vakadu Coastal", "type": "Branch Post Office"}
    ],
    "10. Chittoor District": [
        {"pincode": "517002", "area": "Murukambattu, Chittoor", "type": "Sub Post Office"},
        {"pincode": "517004", "area": "Industrial Estate, Chittoor", "type": "Sub Post Office"},
        {"pincode": "517124", "area": "Gudipala, Chittoor", "type": "Branch Post Office"},
        {"pincode": "517127", "area": "Penumuru, Chittoor", "type": "Mandal HQ"},
        {"pincode": "517128", "area": "Mapakshi, Chittoor", "type": "Branch Post Office"},
        {"pincode": "517408", "area": "Nalamaner / Palamaner Rural", "type": "Branch Post Office"},
        {"pincode": "517417", "area": "Peddapanjani, Palamaner", "type": "Mandal HQ"},
        {"pincode": "517420", "area": "Kallupalle, Punganur", "type": "Branch Post Office"},
        {"pincode": "517421", "area": "Chowdepalle, Punganur", "type": "Mandal HQ"},
        {"pincode": "517426", "area": "Rallabaduguru, Kuppam", "type": "Branch Post Office"}
    ],
    "11. Annamayya District": [
        {"pincode": "516101", "area": "Nandalur RS, Rajampet", "type": "Sub Post Office"},
        {"pincode": "516105", "area": "Utukur, Rajampet", "type": "Branch Post Office"},
        {"pincode": "516110", "area": "Tallapaka, Rajampet", "type": "Sub Post Office"},
        {"pincode": "516126", "area": "Penumuru, Pullampeta", "type": "Branch Post Office"},
        {"pincode": "516216", "area": "Devapatla, Rayachoti", "type": "Branch Post Office"},
        {"pincode": "516269", "area": "Masapet, Rayachoti", "type": "Branch Post Office"},
        {"pincode": "517213", "area": "Thamballapalle, Madanapalle", "type": "Mandal HQ"},
        {"pincode": "517319", "area": "Madanapalle Industrial Estate", "type": "Sub Post Office"},
        {"pincode": "517326", "area": "Horsley Hills, Madanapalle", "type": "Sub Post Office"},
        {"pincode": "517352", "area": "Kurabalakota, Madanapalle", "type": "Mandal HQ"},
        {"pincode": "517390", "area": "Peddamandyam, Madanapalle", "type": "Mandal HQ"}
    ],
    "12. YSR Kadapa District": [
        {"pincode": "516002", "area": "Seven Roads Junction, Kadapa", "type": "Sub Post Office"},
        {"pincode": "516004", "area": "Co-operative Colony, Kadapa", "type": "Sub Post Office"},
        {"pincode": "516172", "area": "Devuni Kadapa, Kadapa", "type": "Sub Post Office"},
        {"pincode": "516201", "area": "Utukur, Kadapa", "type": "Sub Post Office"},
        {"pincode": "516267", "area": "Buggaletipalle, CK Dinne", "type": "Branch Post Office"},
        {"pincode": "516309", "area": "RTPP (Rayalaseema Thermal Power Plant), Muddanur", "type": "Sub Post Office"},
        {"pincode": "516360", "area": "Proddatur Bazaar", "type": "Sub Post Office"},
        {"pincode": "516361", "area": "Bollavaram, Proddatur", "type": "Sub Post Office"},
        {"pincode": "516390", "area": "Vempalle Rural", "type": "Branch Post Office"},
        {"pincode": "516434", "area": "Yerraguntla RS", "type": "Sub Post Office"},
        {"pincode": "516439", "area": "Gandikota Fort, Jammalamadugu", "type": "Sub Post Office"}
    ],
    "13. Sri Potti Sriramulu Nellore District": [
        {"pincode": "524002", "area": "Nawabpet, Nellore", "type": "Sub Post Office"},
        {"pincode": "524003", "area": "Stonehousepet, Nellore", "type": "Sub Post Office"},
        {"pincode": "524004", "area": "Venkata Reddynagar, Nellore", "type": "Sub Post Office"},
        {"pincode": "524005", "area": "VRC Center, Nellore", "type": "Sub Post Office"},
        {"pincode": "524102", "area": "Gudur Bazaar", "type": "Sub Post Office"},
        {"pincode": "524202", "area": "Kavali RS", "type": "Sub Post Office"},
        {"pincode": "524203", "area": "Musunuru, Kavali", "type": "Sub Post Office"},
        {"pincode": "524317", "area": "Damaramadugu, Buchireddypalem", "type": "Branch Post Office"},
        {"pincode": "524320", "area": "Jonnavada, Buchireddypalem", "type": "Sub Post Office"},
        {"pincode": "524346", "area": "Podalakuru Mining Belt", "type": "Branch Post Office"},
        {"pincode": "524413", "area": "Krishnapatnam Port, Muthukur", "type": "Sub Post Office"}
    ],
    "14. Prakasam District": [
        {"pincode": "523002", "area": "Lawyerpet, Ongole", "type": "Sub Post Office"},
        {"pincode": "523003", "area": "Venkateswara Nagar, Ongole", "type": "Sub Post Office"},
        {"pincode": "523180", "area": "Pelluru, Ongole", "type": "Branch Post Office"},
        {"pincode": "523181", "area": "Koppole, Ongole", "type": "Branch Post Office"},
        {"pincode": "523226", "area": "Gundlapalli Granite Growth Center, Chimakurthy", "type": "Sub Post Office"},
        {"pincode": "523272", "area": "Jarugumalli, Singarayakonda", "type": "Mandal HQ"},
        {"pincode": "523273", "area": "Kandukur Rural", "type": "Branch Post Office"},
        {"pincode": "523315", "area": "Dupadu, Tripuranthakam", "type": "Branch Post Office"},
        {"pincode": "523331", "area": "Markapur RS", "type": "Sub Post Office"},
        {"pincode": "523372", "area": "Giddalur RS", "type": "Sub Post Office"}
    ],
    "15. Kurnool District": [
        {"pincode": "518002", "area": "Fort Kurnool / Old Town", "type": "Sub Post Office"},
        {"pincode": "518004", "area": "Budhawarapet, Kurnool", "type": "Sub Post Office"},
        {"pincode": "518005", "area": "Medical College, Kurnool", "type": "Sub Post Office"},
        {"pincode": "518006", "area": "NR Peta, Kurnool", "type": "Sub Post Office"},
        {"pincode": "518301", "area": "Adoni Bazaar", "type": "Sub Post Office"},
        {"pincode": "518302", "area": "Arts College, Adoni", "type": "Sub Post Office"},
        {"pincode": "518313", "area": "Siruguppa Road, Adoni", "type": "Sub Post Office"},
        {"pincode": "518360", "area": "Yemmiganur Cotton Mills", "type": "Sub Post Office"},
        {"pincode": "518466", "area": "Pyapili / Peapully Border, Dhone", "type": "Branch Post Office"},
        {"pincode": "518523", "area": "Banganapalle RS, Dhone Corridor", "type": "Branch Post Office"}
    ],
    "16. Nandyal District": [
        {"pincode": "518501", "area": "Nandyal RS", "type": "Sub Post Office"},
        {"pincode": "518503", "area": "Srinivasanagar, Nandyal", "type": "Sub Post Office"},
        {"pincode": "518504", "area": "Nandyal Oil Mills", "type": "Sub Post Office"},
        {"pincode": "518511", "area": "Ahobilam, Allagadda", "type": "Pilgrim Sub Post Office"},
        {"pincode": "518542", "area": "Allagadda Bazaar", "type": "Sub Post Office"},
        {"pincode": "518583", "area": "Panyam Cement Factory", "type": "Sub Post Office"},
        {"pincode": "518593", "area": "Giddalur Road, Sirvel", "type": "Branch Post Office"}
    ],
    "17. Anantapur District": [
        {"pincode": "515002", "area": "Old Town, Anantapur", "type": "Sub Post Office"},
        {"pincode": "515003", "area": "Engineering College (JNTU), Anantapur", "type": "Sub Post Office"},
        {"pincode": "515004", "area": "SK University, Anantapur", "type": "Sub Post Office"},
        {"pincode": "515005", "area": "Anantapur Collectorate", "type": "Sub Post Office"},
        {"pincode": "515408", "area": "Yerraguntla Border, Tadipatri", "type": "Branch Post Office"},
        {"pincode": "515412", "area": "UltraTech Cement Works, Tadipatri", "type": "Sub Post Office"},
        {"pincode": "515802", "area": "Guntakal Junction RS", "type": "Sub Post Office"},
        {"pincode": "515803", "area": "Hanumeshnagar, Guntakal", "type": "Sub Post Office"},
        {"pincode": "515811", "area": "Narpala Road, Singanamala", "type": "Branch Post Office"}
    ],
    "18. Sri Sathya Sai District": [
        {"pincode": "515135", "area": "Prasanthi Nilayam, Puttaparthi", "type": "Head Post Office"},
        {"pincode": "515144", "area": "Super Speciality Hospital, Puttaparthi", "type": "Sub Post Office"},
        {"pincode": "515202", "area": "MIG Colony, Hindupur", "type": "Sub Post Office"},
        {"pincode": "515211", "area": "Penukonda Fort", "type": "Sub Post Office"},
        {"pincode": "515235", "area": "Palasamudram (Kia Motors Industrial Hub), Gorantla", "type": "Sub Post Office"},
        {"pincode": "515592", "area": "Kadiri Town RS", "type": "Sub Post Office"},
        {"pincode": "515672", "area": "Dharmavaram Handloom Weavers Market", "type": "Sub Post Office"}
    ],
    "19. East Godavari District": [
        {"pincode": "533102", "area": "Aryapuram, Rajahmundry", "type": "Sub Post Office"},
        {"pincode": "533103", "area": "Innespeta, Rajahmundry", "type": "Sub Post Office"},
        {"pincode": "533104", "area": "Prakashnagar, Rajahmundry", "type": "Sub Post Office"},
        {"pincode": "533105", "area": "Danavaipeta, Rajahmundry", "type": "Sub Post Office"},
        {"pincode": "533106", "area": "Paper Mills, Rajahmundry", "type": "Sub Post Office"},
        {"pincode": "533107", "area": "Morampudi, Rajahmundry", "type": "Sub Post Office"},
        {"pincode": "533128", "area": "Kadiyapulanka Nursery Hub, Kadiyam", "type": "Sub Post Office"},
        {"pincode": "534341", "area": "Kovvur Sugar Factory Zone", "type": "Sub Post Office"}
    ],
    "20. Kakinada District": [
        {"pincode": "533002", "area": "Suryaraopeta, Kakinada", "type": "Sub Post Office"},
        {"pincode": "533003", "area": "Jagannaickpur, Kakinada", "type": "Sub Post Office"},
        {"pincode": "533004", "area": "Ramanayyapeta, Kakinada", "type": "Sub Post Office"},
        {"pincode": "533005", "area": "Kakinada Port", "type": "Sub Post Office"},
        {"pincode": "533006", "area": "NFCL Greenfields, Kakinada", "type": "Sub Post Office"},
        {"pincode": "533007", "area": "Vakalapudi Light House, Kakinada", "type": "Sub Post Office"},
        {"pincode": "533402", "area": "Payakaraopeta Border, Tuni", "type": "Sub Post Office"},
        {"pincode": "533441", "area": "Samalkot ADB Road", "type": "Sub Post Office"}
    ],
    "21. Dr. B.R. Ambedkar Konaseema District": [
        {"pincode": "533202", "area": "Clock Tower, Amalapuram", "type": "Sub Post Office"},
        {"pincode": "533203", "area": "Housing Board Colony, Amalapuram", "type": "Sub Post Office"},
        {"pincode": "533239", "area": "Jonnada, Ravulapalem", "type": "Sub Post Office"},
        {"pincode": "533241", "area": "Tatipaka, Razole", "type": "Major Trade Town / Sub Post Office"},
        {"pincode": "533243", "area": "Chintalapudi, Razole", "type": "Branch Post Office"},
        {"pincode": "533252", "area": "Mori, Sakhinetipalle", "type": "Branch Post Office"},
        {"pincode": "533307", "area": "Alamuru, Mandapeta", "type": "Mandal HQ"}
    ],
    "22. West Godavari District": [
        {"pincode": "534202", "area": "Juvalapalem Road, Bhimavaram", "type": "Sub Post Office"},
        {"pincode": "534203", "area": "Gunupudi, Bhimavaram", "type": "Sub Post Office"},
        {"pincode": "534204", "area": "SRKR Engineering College, Bhimavaram", "type": "Sub Post Office"},
        {"pincode": "534210", "area": "Dippalapatnam, Palacoderu", "type": "Branch Post Office"},
        {"pincode": "534261", "area": "Palakollu Bazaar", "type": "Sub Post Office"},
        {"pincode": "534276", "area": "Perupalem Beach, Narasapuram", "type": "Sub Post Office"},
        {"pincode": "534280", "area": "L.B.Cherla, Narasapuram", "type": "Branch Post Office"}
    ],
    "23. Eluru District": [
        {"pincode": "534002", "area": "Southern Street, Eluru", "type": "Sub Post Office"},
        {"pincode": "534003", "area": "Powerpet RS, Eluru", "type": "Sub Post Office"},
        {"pincode": "534004", "area": "Sanivarapupeta, Eluru", "type": "Sub Post Office"},
        {"pincode": "534005", "area": "Tangellamudi, Eluru", "type": "Sub Post Office"},
        {"pincode": "534006", "area": "RR Peta, Eluru", "type": "Sub Post Office"},
        {"pincode": "521202", "area": "Nuzvid IIIT Campus", "type": "Sub Post Office"},
        {"pincode": "534448", "area": "Jangareddygudem Bus Stand", "type": "Sub Post Office"}
    ],
    "24. Srikakulam District": [
        {"pincode": "532005", "area": "Arasavalli Sun Temple, Srikakulam", "type": "Sub Post Office"},
        {"pincode": "532006", "area": "Gujaratipeta, Srikakulam", "type": "Sub Post Office"},
        {"pincode": "532127", "area": "Srikakulam Road RS (Amadalavalasa)", "type": "Sub Post Office"},
        {"pincode": "532222", "area": "Kasibugga, Palasa", "type": "Major Commercial Suburb"},
        {"pincode": "532243", "area": "Sompeta RS", "type": "Sub Post Office"},
        {"pincode": "532408", "area": "Pydibhimavaram Pharma SEZ, Ranasthalam", "type": "Sub Post Office"}
    ],
    "25. Vizianagaram District": [
        {"pincode": "535002", "area": "Cantonment, Vizianagaram", "type": "Sub Post Office"},
        {"pincode": "535003", "area": "Phoolbagh, Vizianagaram", "type": "Sub Post Office"},
        {"pincode": "535004", "area": "Fort Vizianagaram", "type": "Sub Post Office"},
        {"pincode": "535182", "area": "Kothavalasa RS", "type": "Sub Post Office"},
        {"pincode": "535502", "area": "Bobbili Growth Center", "type": "Sub Post Office"}
    ],
    "26. Parvathipuram Manyam District": [
        {"pincode": "535502", "area": "Parvathipuram Town RS", "type": "Sub Post Office"},
        {"pincode": "535592", "area": "Salur Bazaar", "type": "Sub Post Office"},
        {"pincode": "535441", "area": "Palakonda RTC Complex", "type": "Sub Post Office"}
    ]
}

total_leftover_ap_pins = sum(len(pins) for pins in LEFTOVER_AP_PINCODES.values())
print(f"Total Leftover AP Postal PIN Codes & Sub-Office Hubs Identified: {total_leftover_ap_pins}")
