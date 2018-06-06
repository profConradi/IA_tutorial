'''
Config file
'''

LenFifo = 20 #buffer length - original = 10
Athr = 0.04 #m/s^2
tCycle = 0.05 #s - original = 0.2
tDelay = 5 #s tempo di attesa tra un movimento e il successivo
#ricorrenze = numero di volte che appare un movimento, lunghezza pari al numero di movimenti
#movimenti: accendi luce(1), spegni luce(2), medicine(3), rumore(999)
ricorrenze = [0, 0, 0, 0, 0]
sogliaRic = 8
minMovRec = 6
