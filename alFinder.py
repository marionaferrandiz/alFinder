# -*- coding: utf-8 -*-
# thomas.bigot@tmgo.net


import read
import individual
import sys

print("       __               \n _  | |_  o __  _| _  __\n(_| | |   | | |(_|(/_ | \n")

INIVERSION = 2


# mini config parser inspired from http://www.decalage.info/fr/python/configparser
# (see the comment by “trinar”)

class ParseINI(dict):
  def __init__(self, f):
    self.f = f
    self.__read()

  def __read(self):
    with open(self.f, 'r') as f:
      soi = self
      for line in f:
        if not line.startswith("#") and not line.startswith(';') and line.strip() != "":
          line = line.replace('=', ':')
          line = line.replace(';', '#')
          index = line.find('#')
          line = line[:index]
          line = line.strip()
          if line.startswith("["):
            sections = line[1:-1].split('.')
            soi = self
            for section in sections:
              if section not in soi:
                soi[section] = {}
              soi = soi[section]
          else:
            if not self:
              soi['global'] = {}
              soi = soi['global']
            parts = line.split(":", 1)
            soi[parts[0].strip()] = parts[1].strip()

  def items(self, section):
    try:
      return self[section]
    except KeyError:
      return []
try:
    ini = ParseINI('settings.ini')
except IOError, e:
    print("You have no configuration file. Please copy settings.sample.ini to settings.ini and update the settings.")
    sys.exit()
    
if int(ini['global']['iniVersion']) < INIVERSION: 
    print("Your version of settings is too old. Please copy settings.sample.ini to settings.ini and update the settings.")
    sys.exit()

    
# sortie
# ======
# Fichier de sortie où seront écrits les résultats

resultFile = ini['Files']['fastaSequences'].split('.')[0] +"_result.csv"

### DÉFINITION DE QUELQUES FONCTIONS ###

def suffixFile(filename,suffix):
    filename = filename.split(".")
    begining = filename[:-1]
    for i in range(len(begining)-1):
        begining.insert(i*2+1,".")
    extension = filename[-1]
    return("".join(begining) + suffix + "." + extension)

    


### EXÉCUTION DES FONCTIONS ###

print("Loading sequences from file " + ini['Files']['fastaSequences'] + "…"),
sys.stdout.flush()
read.Read.loadFromFile(ini['Files']['fastaSequences'])
print("    [DONE]")

print("Loading individuals from file " + ini['Files']['tags'] + "…"),
sys.stdout.flush()
individual.Individual.loadFromFile(ini['Files']['tags'])
print("    [DONE]")

print("Loading loci markers…"),
sys.stdout.flush()
print(ini['LociMarkers'])
individual.Individual.setLociMarkers(ini['LociMarkers'])
print("    [DONE]")


print("Sequences are now being associated to loci/individual according to their tags…"),
sys.stdout.flush()
read.Read.identify(individual.Individual)
print("    [DONE]")


## getting alleles files

print("Loading alleles from " + str(ini['Files']['Alleles'].values()) +  " file…"),
sys.stdout.flush()
individual.Individual.loadLociFromFiles(ini['Files']['Alleles'])
print("    [DONE]")

print("Sequences are now being associated to allelles…"),
sys.stdout.flush()
read.Read.match(individual.Individual._alleles)
print("    [DONE]")


if ini['AlleleDiscovering']['discovering'] == "True":
    print("Discovering new alleles…"),
    sys.stdout.flush()
    
    # getting the name of the new alleles from the init files
    newAllelesFiles = []
    for currFile in ini['Files']['Alleles'].values():
        newAllelesFiles.append(suffixFile(currFile,"_new"))
    
    
    individual.Individual.discoverNewAlleles(newAllelesFiles,int(ini['AlleleDiscovering']['threshold']))
    print("    [DONE]")
    
    print("Unidentified sequences are now being associated to new allelles…"),
    sys.stdout.flush()
    read.Read.match(individual.Individual._newAlleles)
    print("    [DONE]")
    
    

print("Writing result to file " + resultFile +"…"),
sys.stdout.flush()
read.Read.writeTo(resultFile,int(ini['Results']['showUnidentified']))
print("    [DONE]")