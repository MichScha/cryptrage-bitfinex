import json
import requests
from requests.exceptions import HTTPError

class pairings:
    def __init__(self):
        self.url = 'https://api-pub.bitfinex.com/v2/'
        self.masterDataParameter = 'tickers?symbols=ALL'
    def fetchMasterData(self):
        try:
            response = requests.get(self.url + self.masterDataParameter)
            response.raise_for_status()
            validPairings = []
            #print(response.content)
            jsonPairings = json.loads(response.content)
            for pair in jsonPairings:
                #print(len(pair[0]))
                if len(pair[0]) == 7:
                    #print('Correct Pairing: ' + pair[0])
                    validPairings.append(pair[0])
            with open('pairing.json', 'w') as outfile:
                json.dump(validPairings, outfile)
            print(len(validPairings))
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6
        else:
            print('Success getting pairs!')

    def getPairings(self):
        f = open("pairing.json", "r")
        return json.loads(f.read())

    def getTransactionData(self):
        print("getTransactionData")

pairing = pairings()
pairing.fetchMasterData()
print(pairing.getPairings())