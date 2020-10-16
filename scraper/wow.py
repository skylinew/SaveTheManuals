


from datetime import date
import pymongo
import ssl


today = date.today()


doc = {"date": str(date.today()), "cars":[]}

with open('./filtered_lists/2020-08-24.txt') as f:
    lines = f.readlines()
    for line in lines:
        arr = line.split(' ~')
        item = {"make": arr[0], "model": arr[1].rstrip()}
        doc["cars"].append(item)
    
    f.close()

myclient = pymongo.MongoClient('mongodb+srv://mfuFEyJVaMYWdMiI:gtrJ1i4100gUybbC@cluster0.\
bfhco.mongodb.net/SaveTheManuals?retryWrites=true&w=majority', ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
mydb = myclient["SaveTheManuals"]
mycol = mydb["cars"]

x = mycol.insert_one(doc)
print(x)

