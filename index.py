import json
import requests

import routingModule

from requests.exceptions import HTTPError
from pathlib import Path

class pairings:
    def __init__(self):
        self.url = 'https://api-pub.bitfinex.com/v2/'
        self.masterDataParameter = 'tickers?symbols=ALL'
        self.filedir = './pairings/'
        self.filedirtemp = './pairings/temp/'
        p = Path('pairings/temp')
        p.mkdir(exist_ok=True)

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
            with open(self.filedir + 'pairing.json', 'w') as outfile:
                json.dump(validPairings, outfile)
            print(len(validPairings))
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6
        else:
            print('Success getting pairs!')

    def splitMasterdata(self, currency):
        f = open(self.filedir + "pairing.json", "r")
        jsonPairings = json.loads(f.read())
        validPairings = []
        for pair in jsonPairings:
            if currency in pair:
                if pair[1:4] != currency:
                    validPairings.append(pair)
                    #print(pair)
        with open(self.filedir + currency + '.json', 'w') as outfile:
            json.dump(validPairings, outfile)
    def getPairings(self):
        f = open(self.filedir + "pairing.json", "r")
        return json.loads(f.read())

    def findCircuit(self, startCurrency, compareCurrency):
        f = open(self.filedir + startCurrency + '.json', "r")
        startCurrencyPairings = json.loads(f.read())
        f = open(self.filedir + compareCurrency + '.json', "r")
        compairePairings = json.loads(f.read())
        validCircuit = []
        circuits = []
        for startCurPair in startCurrencyPairings:
            for comparePair in compairePairings:
                if startCurPair[1:4] == comparePair[1:4]:
                    # [Beginn : Beginn + Length]
                    validCircuit.append(startCurPair)
                    validCircuit.append(comparePair)
                    validCircuit.append('t' + compareCurrency + startCurrency)
                    circuits.append(validCircuit)
                validCircuit = []
                    #print("Found circuits")
                    #print(startCurPair[4:7] + '->' + startCurPair[1:4] + '->' + comparePair[4:7] + '->' + startCurPair[4:7])
        with open(self.filedir + compareCurrency + startCurrency + 'Circuit.json', 'w') as outfile:
            json.dump(circuits, outfile)

    def getOrderbooks(self, startCurrency, compareCurrency):
        f = open(self.filedir + compareCurrency + startCurrency + 'Circuit.json', "r")
        circuits = json.loads(f.read())
        precision = 'P0'
        for circuit in circuits:
            i = 0
            for pair in circuit:
                # Check if pair orderbook already fetched
                currentPair = Path(self.filedirtemp + pair + '.json')
                if not currentPair.exists():
                    try:
                        response = requests.get(self.url + '/book/' + pair + '/' + precision)
                        response.raise_for_status()
                        jsonOrderbook = json.loads(response.content)
                        jsonOrderbookFiltered = []
                        if(i > 0):
                            # seller
                            for order in jsonOrderbook:
                                if order[2] < 0:
                                    jsonOrderbookFiltered.append(order)
                        else:
                            # buyer
                            for order in jsonOrderbook:
                                if order[2] > 0:
                                    jsonOrderbookFiltered.append(order)
                        with open(self.filedirtemp + pair + '.json', 'w') as outfile:
                            json.dump(jsonOrderbookFiltered, outfile)
                    except HTTPError as http_err:
                        print(f'HTTP error occurred: {http_err}')  # Python 3.6
                    except Exception as err:
                        print(f'Other error occurred: {err}')  # Python 3.6
                    else:
                        print('Success getting pairs!')
                i = i + 1  
            self.calculateCircuit(circuit)

    def calculateCircuit(self, circuit):
        startOrderbook = []
        f = open(self.filedirtemp + circuit[0] + '.json', "r")
        startOrderbook = json.loads(f.read())
        tokenOrderbook = []
        f = open(self.filedirtemp + circuit[1] + '.json', "r")
        tokenOrderbook = json.loads(f.read())
        compareOrderbook = []
        f = open(self.filedirtemp + circuit[2] + '.json', "r")
        compareOrderbook = json.loads(f.read())
        #console.log((100 / toFixed(buyerE1[0][0])) * toFixed(sellerE2[0][0]) * toFixed(sellerE3[0][0]))
        arbitrage = 100 / float(startOrderbook[0][0]) * float(tokenOrderbook[0][0]) * compareOrderbook[0][0]
        print(circuit)
        print(arbitrage)
pairing = pairings()
#pairing.fetchMasterData()
#print(pairing.getPairings())
#pairing.splitMasterdata('ETH')
#pairing.splitMasterdata('USD')
#pairing.splitMasterdata('EUR')
#pairing.splitMasterdata('BTC')
#pairing.findCircuit('EUR', 'BTC')
pairing.getOrderbooks('EUR', 'BTC')