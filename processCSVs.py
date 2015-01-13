import sys, glob, csv, re, os, shutil, math, operator, collections
from os.path import join, getsize
sys.path.append("D:\\_Python\\Library")
import mgr, textwrap
from bs4 import BeautifulSoup

# Some collected statistics
hadithNumber =   34175 #    34,175
asanidLen    =  420095 #   420,095 > top 200 tokens: 382,541; top 100 > 354,759; 1977 unique tokens (freq 2up)
mutunLen     = 1879849 # 1,879,849
ahadithLen   = 2270039 # 2,270,039

csvFolder = "D:/_Python/HadithCorpus/newCSV/"
workingFolder = "D:/_Python/HadithCorpus/WorkingData/"

def collectCSV(csvFolder):
    new = ""
    fileList = os.listdir(csvFolder)
    for file in fileList:
        print(file)
        newFile = open(csvFolder+file, "r", encoding="utf-8").read()
        new = new+"\n"+newFile
    new = re.sub("(\n)+", "\n", new)
    new = re.sub("(\n$|^\n)", "", new)
    cumulativeCSV = open("all_Hadith.txt", "w", encoding="utf-8")
    cumulativeCSV.write(new)
    cumulativeCSV.close()

def collectData(mainFile):
    print("sorting cumulativeCSV...")
    asanid  = []
    mutun   = []
    mutunIndexed = []
    ahadith = []
    with open(mainFile, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            matnClean = re.sub("\W", " ", row[2])
            mutunIndexedLine = row[0]+"\t"+matnClean
            mutunIndexed.append(mutunIndexedLine)
            asanid.append(row[1])
            mutun.append(row[2])
            ahadith.append(row[3])
    asanid = "\n".join(asanid)
    tempFile = open(workingFolder+"all_Hadith_asanid.txt", "w", encoding="utf-8")
    tempFile.write(asanid)
    tempFile.close()

    mutun = "\n".join(mutun)
    tempFile = open(workingFolder+"all_Hadith_mutun.txt", "w", encoding="utf-8")
    tempFile.write(mutun)
    tempFile.close()

    mutunIndexed = "\n".join(mutunIndexed)
    tempFile = open(workingFolder+"all_Hadith_mutun_indexed.txt", "w", encoding="utf-8")
    tempFile.write(mutunIndexed)
    tempFile.close()

    ahadith = "\n".join(ahadith)
    tempFile = open(workingFolder+"all_Hadith_ahadith.txt", "w", encoding="utf-8")
    tempFile.write(ahadith)
    tempFile.close()

def processSingleFile(fileName, freq):
    print(fileName)
    # freqList > unique word forms
    fileNameBase = re.sub("\..*?$", "", fileName)
    fileText = open(fileName, 'r', encoding='utf-8').read()
    fileText = mgr.normalizeArabicVeryLight(fileText)
    fileText = re.sub("\W+", " ", fileText)
    fileText = re.sub("[a-zA-Z0-9]", " ", fileText)
    fileText = re.sub("( )+", " ", fileText)
    fileText = re.sub(r"(^|\n) | (\n|$)", r"\1", fileText)
    fileText = re.sub("( )+", "\n", fileText)
    
    fileText = mgr.freqListNoNorm(fileText, freq)
    with open(fileNameBase+"_FreqList.txt", "w", encoding='utf-8') as f:
        f.write(fileText)
    fileText = re.sub("\d+\t", "", fileText)
    with open(fileNameBase+"_UniqueTokens.txt", "w", encoding='utf-8') as f:
        f.write(fileText)
    
    # nGrams   > freqList

# splits unique words into 1,000 word chunks for easier buckwaltering
def hadithCorpusForBW(fileName):
    counter = 0
    newFile = ""
    fileText = open(fileName, 'r', encoding='utf-8').readlines()
    for line in fileText:
        newFile = newFile+line
        counter = counter +1
        if counter % 1000 == 0:
            with open(workingFolder+"tokens%06d.txt" % counter, "w", encoding='utf-8') as f:
                f.write(newFile)
                newFile = ""

def convertWordsToNumbers():
    print("starting complex replace...")
    lineCounter = 0
    newFile = open(workingFolder+"all_Hadith_mutun_indexed.txt", 'r', encoding='utf-8').read()
    newFile = mgr.normalizeArabicVeryLight(newFile)
    freqListRef = ""
    freqFile = open(workingFolder+"all_Hadith_mutun_FreqList.txt", 'r', encoding='utf-8').read()
    freqFile = re.sub("0000000[1]\t.*(\n|$)", "", freqFile)
    allFreqs = re.findall("\d{8}", freqFile)
    allFreqs = list(set(allFreqs))
    allFreqs = sorted(allFreqs)
    nameOfNewFile = "all_Hadith_mutun_numbers.txt"
    print("Number of unique frequencies: %d" % len(allFreqs))
    for freqVal in allFreqs:
        #print("\t"+freqVal)
        lineCounter = mgr.counter(lineCounter, 100)
        replaceList = re.findall("%s\t(.*)" % freqVal, freqFile)
        if len(replaceList) == 1:
            newFile = re.sub(r"\b(%s)\b" % replaceList[0], freqVal, newFile)
            with open(workingFolder+nameOfNewFile, "w", encoding='utf-8') as f:
                f.write(newFile)
        else:
            listOfPhrasesRE = mgr.reFromListNoNorm(replaceList)
            print("Multiple freqItems: %d (freq: %s)" % (len(listOfPhrasesRE), freqVal))
            for i in listOfPhrasesRE:
                newFile = re.sub(r"\b(%s)\b" % i, freqVal, newFile)
                with open(workingFolder+nameOfNewFile, "w", encoding='utf-8') as f:
                    f.write(newFile)
    newFile = re.sub(r"\b(%s+)\b" % mgr.arLetters, "00000001", newFile) # for words with freqs 1-5
    with open(workingFolder+nameOfNewFile, "w", encoding='utf-8') as f:
        f.write(newFile)

# calculate probabilities
##def vocabProbabilities():
##    total = 1879825
##    mainFile = workingFolder+"all_Hadith_mutun_FreqList.txt"
##    ofile  = open(workingFolder+"all_Hadith_mutun_Probabilities.txt", "w", encoding='utf-8')
##    writer = csv.writer(ofile, delimiter='\t', lineterminator='\n')
##    with open(mainFile, 'r', encoding='utf-8') as f:
##        reader = csv.reader(f, delimiter='\t')
##        for row in reader:
    
# calculate weights
def weightHadith():
    print("Calculating weights...")
    mainFile = workingFolder+"all_Hadith_mutun_numbers.txt"
    hadithCorpus = open(mainFile, 'r', encoding='utf-8').read()
    #total = len(re.findall("\d{8}", hadithCorpus))
    total = 1879825
    ofile  = open(workingFolder+"all_Hadith_mutun_weights.txt", "w", encoding='utf-8')
    writer = csv.writer(ofile, delimiter='\t', lineterminator='\n')
    with open(mainFile, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            hadithID = row[0]
            #print(hadithID)
            hadithNums = re.sub("( )+", " ", row[1].strip())
            hadithNums = hadithNums.split(" ")
            hadithNums = list(map(int, hadithNums)) # converts numbers into integers
            matnLen = len(hadithNums)
            hadithProbs = [x/total for x in hadithNums]
            cumulProb = sum(hadithProbs)/matnLen
            #cumulProb = round(cumulProb,15)
            cumulProb = "%.20f" % cumulProb
            writer.writerow([cumulProb, hadithID, matnLen])

    ofile.close()

# generate hadith reader with data
def generateReader():
    print("generating reader...")
    # open freq file
    freqFile = open(workingFolder+"all_Hadith_mutun_FreqList.txt", 'r', encoding='utf-8').read()
    corpusFile = open(workingFolder+"all_Hadith.txt", 'r', encoding='utf-8').read()

    newFile = ""
    div = "\n================================"

    counter = 0

    with open(workingFolder+"all_Hadith_mutun_weights_desc.txt", 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            weight = row[0]
            hadithID = row[1]
            length = row[2]
            counter = mgr.counter(counter, 100)
            rank = '{0:>6}'.format(counter)

            entireHadith = re.search(r"%s\t.*" % hadithID, corpusFile).group()
            entireHadith = entireHadith.split("\t")

            # matn only : entireHadith[2]
            # entire hadith : entireHadith[3]

            matn = "# "+entireHadith[3]
            matnWrapped = "\n  ".join(textwrap.wrap(matn))
            
            translation = "# "+entireHadith[4].strip()
            transWrapped = "\n  ".join(textwrap.wrap(translation))

            weights = []
            listWords = re.sub("\W", " ", matn)
            listWords = re.sub("( )+", " ", listWords)
            listWords = listWords.strip()
            listWords = mgr.normalizeArabicVeryLight(listWords)
            listWords = listWords.split(" ")
            #input(listWords)

            for word in listWords:
                #print(word)
                if re.search("\d+\t%s" % word, freqFile):
                    item = re.search("\d+\t%s" % word, freqFile).group()
                    weights.append(item)

            weights = list(set(weights))
            weights = sorted(weights, reverse=True)
            weights = "\n".join(weights)
            #input(weights)

            block = ""
            block = block+div+div+"\n# RANK: " + rank + "; ID: " + hadithID+ "\n# length: %s; weight: %s" % (length, weight)
            block = block+div+"\n# HADITH #\n" + matnWrapped
            block = block+div+"\n# TRANSLATION #\n" + transWrapped
            block = block+div+"\n# FREQUENCIES #\n" + weights
            block = block+div+div+"\n\n"

            #input(block)
            newFile = newFile+block
            with open(workingFolder+"_HadithWeightedReader.txt", "w", encoding='utf-8') as f:
                f.write(newFile)

    

#collectCSV(csvFolder)
#collectData(workingFolder+"all_Hadith.txt")
    
#processSingleFile(workingFolder+"all_Hadith_ahadith.txt",1)
#processSingleFile(workingFolder+"all_Hadith_asanid.txt",1)
#processSingleFile(workingFolder+"all_Hadith_mutun.txt",1)

#processSingleFile(workingFolder+"all_Hadith_ahadith.txt",2)
#processSingleFile(workingFolder+"all_Hadith_asanid.txt",2)
#processSingleFile(workingFolder+"all_Hadith_mutun.txt",2)

#hadithCorpusForBW(workingFolder+"all_Hadith_ahadith_UniqueTokens.txt")

#convertWordsToNumbers()
#weightHadith()
#generateReader() # should be modified: create a list of words, then run through the freq file and do re.sub

#mgr.ngraming(workingFolder+"all_Hadith_mutun.txt",2)
mgr.ngraming(workingFolder+"all_Hadith_mutun.txt",3)
mgr.ngraming(workingFolder+"all_Hadith_mutun.txt",4)

print("Done!")
