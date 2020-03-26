import datetime

weekday_names = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]
month_names = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
named_days = {"heute":0, "morgen":1, "übermorgen":2}
named_times = {
    "Morgen": (datetime.time(6, 0), datetime.time(10, 0)),
    "Vormittag": (datetime.time(10, 0), datetime.time(12, 0)), 
    "Mittag": (datetime.time(12, 0), datetime.time(14, 0)), 
    "Nachmittag": (datetime.time(15, 0), datetime.time(18, 0)), 
    "Abend": (datetime.time(18, 0), datetime.time(22, 0)), 
    "Nacht": (datetime.time(22, 0), datetime.time(7, 0))
}
named_times_synonyms = {
    "früh": "Morgen"
}