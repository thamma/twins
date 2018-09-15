#!/bin/python
a="Visier, roter Bauklotz in form einer brücke, eine von Kinderhand gezeichnete Schatzkarte, Walnuss, Kindermesser, roter Bauklotz in form einer brücke, Gabel der ein Zacken fehlt, Teddybär ohne Ohren, kleinen Kaktus im Blumentopf, blauer Wachsmalstift, gelber Bauklotz, Federmäppchen voller Buntstifte, Haarspange, Eine Metallbox voller weißer Kreide, Nussknacker, Brosche mit königlichem Wappen, gelber Bauklotz, Stoffmaus, Ein abgebrochener Glasboden eines Einmachglases, Taschenbuch mit einem getrockneten Falter, Flaschenöffner, Vinylschallplatte, Fingerhut, Nadelkissen in Holzrahmen, Walnuss"
a = a.split(",")
from random import shuffle
shuffle(a)
b = a[:]
shuffle(b)
c = a[:]
shuffle(c)
d = a[:]
shuffle(d)
for i in (a + b + c + d):
    print("\n"*40)
    print(i)
    input()
