import sys, glob, csv, re, os, shutil, math, operator, collections
from os.path import join, getsize
sys.path.append("C:\\My Documents\\Python\\Workspace\\scripts")
import mgr, textwrap
from bs4 import BeautifulSoup

isnadKW = """start
حدثت?ني
أخبرت?نا
حدثت?نا
عن
أخبره
#بن
end"""


def isnadRE(isnadKW):
    isnadKW = re.sub("\n", "|", isnadKW)
    isnadKW = mgr.deNormalize(isnadKW)
    isnadFin = re.sub("#", "", isnadKW)
    isnadKW = r"((%s) (\w+ ){1,8})+(%s)\b" % (isnadKW, isnadFin)
    print(isnadKW)
    return(isnadKW)

sanadRE = isnadRE(isnadKW)

def quickCleanAR(text):
    text = re.sub("\n", " ", text)
    text = re.sub("<.*?>", " ", text)
    text = re.sub('[\'"،\-.]', "", text)
    text = re.sub("( )+", " ", text)
    return(text)

def quickCleanEN(text):
    text = re.sub("\n", " ", text)
    text = re.sub("<.*?>", " ", text)
    text = re.sub("( )+", " ", text)
    return(text)

# - extract bookName
# - split into chapters, extract details on chapters
# - split chapters into hadith > process each hadith, adding data on book and chapter
def processBook(fileName,sanadRE):
    bookFile = open(fileName, "r", encoding="utf-8").read()
    bookFile = mgr.deNoise(bookFile)
    bookFile = re.sub('\u200f', "", bookFile)
    bookFile = re.sub("\n", "", bookFile)
    bookFile = re.sub("\t", " ", bookFile)
    bookFile = re.sub("( )+", " ", bookFile)
    bookFile = re.sub(r"(</div>)", r"\1\n", bookFile)
    bookFile = re.sub("<span class=saws></span>", "SL3M", bookFile)

    # remove noisy tags
    bookFile = re.sub(r'<span class="arabic_sanad arabic">((.){1,5})?</span>', '', bookFile)
    bookFile = re.sub(r'<(br|/?[pb])>', ' ', bookFile)

    bookFile = re.sub("( )+", " ", bookFile)

    # title metadata
    collectionTitle = re.search(r"collection = '(.*?)'", bookFile).group(1).strip()
    bookID          = re.search(r"bookID = '(.*?)'", bookFile).group(1).strip()
    newFileName     = collectionTitle+"%02d" % (int(bookID))
    print("collection: %s" % newFileName)

    csvFile = open(targetFolder+newFileName+".csv", "w", encoding="utf-8")
    csvWriter = csv.writer(csvFile, delimiter ="\t", lineterminator='\n')

    # book metadata
    bookArTitle = re.search(r"<div class=\"book_page_arabic_name arabic\">(.*)</div>", bookFile).group(1).strip()
    bookNo      = re.search(r"<div class=\"book_page_number\">(.*?)</div>", bookFile).group(1).strip()
    bookEnTitle = re.search(r"<div class=\"book_page_english_name\">(.*?)</div>", bookFile).group(1).strip()

##    # split into chapters
##    chapters    = re.split("<div class=chapter>", bookFile)
##    for chapter in chapters[1:]:
##            chapArTitle = re.search(r'<div class="arabicchapter arabic">(.*?)</div>', chapter).group(1).strip()
##            chapArNo    = re.search(r'<div class=achapno>\((.*?)\)</div>', chapter).group(1).strip()
##            chapEnTitle = re.search(r'<div class=englishchapter>(.*?)</div>', chapter).group(1).strip()
##            chapEnNo    = re.search(r'<div class=echapno>\((.*?)\)</div>', chapter).group(1).strip()

    # split chapter into hadiths
    #hadiths = re.split("class=actualHadithContainer", chapter)
    hadiths = re.split("class=actualHadithContainer", bookFile)
    for hadith in hadiths[1:]:
        hadithBS = BeautifulSoup(hadith)
        # get hadith ID
        hadithID = re.search(r"id=.(\d+)", hadith).group(1)
        hadithID = newFileName+"_"+hadithID
        print(hadithID)
        
        # get arabic hadith (both isnad and matn)
        arHadith = hadithBS.find("div", { "class" : "arabic_hadith_full arabic" })
        arHadith = quickCleanAR(str(arHadith).strip())
        #print("Arabic hadith:\n"+ str(arHadith))
        if re.search(r"^ ?%s" % sanadRE, arHadith):
            arIsnad = re.search(r"^ ?%s" % sanadRE, arHadith).group()
            arMatn  = re.sub(r"^ ?%s" % sanadRE, r"\2", arHadith)
        else:
            arIsnad = "not identified"
            arMatn  = arHadith
        #input(arHadith.split(" "))

        # get english hadith (both isnad and matn)
        enHadith = hadithBS.find("div", { "class" : "englishcontainer" })
        enHadith = quickCleanEN(str(enHadith).strip())
        #print("English hadith:\n"+ str(enHadith))

##                # get references and remaining valuables
##                gradeT = hadithBS.find("table", { "class" : "gradetable" })
##                print("Grade table:\n"+ str(gradeT))
##
##                refT = hadithBS.find("table", { "class" : "hadith_reference" })
##                print("HadithReference:\n"+ str(refT))
        #input([hadithID, arHadith, enHadith])
        csvWriter.writerow([hadithID, arIsnad, arMatn, arHadith, enHadith])
        #input()
    csvFile.close()


def applyToAllSources(sourceFolder):
    fileList = os.listdir(sourceFolder)
    for folder in fileList:
        print(folder)
        folderList = os.listdir(sourceFolder+folder)
        for file in folderList:
            fileName = sourceFolder+folder+"/"+file
            processBook(fileName,sanadRE)

def applyToCollections(collectionFolder):
    fileList = os.listdir(collectionFolder)
    for file in fileList:
        fileName = collectionFolder+file
        processBook(fileName,sanadRE)   

sourceFolder = "D:/_Python/HadithCorpus/sitta/"
targetFolder = "D:/_Python/HadithCorpus/newCSV/"

## CONVERT COLLECTIONS INTO CSVs (1st PASS)
#applyToCollections(sourceFolder+"abudawud/")
#applyToCollections(sourceFolder+"bukhari/")
#applyToCollections(sourceFolder+"ibnmajah/")
#applyToCollections(sourceFolder+"muslim/")
#applyToCollections(sourceFolder+"nasai/")
#applyToCollections(sourceFolder+"tirmidhi/")

print("Done!")
