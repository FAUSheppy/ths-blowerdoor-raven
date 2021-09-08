import fitz
import data
import dateutil.parser
import os.path


BLOCK_TUP_TEXT = 4

def load(filename):
    doc = fitz.open(filename)
    FIRST_P = True

    # pop vars
    customer = "NOT_FOUND"
    location = ""
    startDate = doc.metadata["creationDate"].split("D:")[1].split("+")[0]
    startDateParsed = dateutil.parser.parse(startDate)
    blowerdoorDate = "NOT_FOUND"

    for p in doc:
        blocks = p.get_text("blocks")
        for i in range(0, len(blocks)):
        
            text = blocks[i][BLOCK_TUP_TEXT]
        
            textNoSpaceNewline = text.replace("\n", "")
            textNoSpaceNewline = textNoSpaceNewline.replace(" ", "")
            if FIRST_P and i < 3 and textNoSpaceNewline:
                FIRST_P = False
                customer = text
            
            if "Bauort:" in text:
                location += text.split("Bauort:")[1]

            if "Thermoscan" in text:
                kwParts = text.split("\n")
                kw = ""
                title = ""
                contractor = ""
                for p in kwParts:
                    pClean = p.strip()
                    if not pClean:
                        continue
                    elif not kw:
                        kw = int(pClean.split(". KW")[0])
                    elif not title:
                        title = pClean
                    elif not contractor:
                        contractor = pClean

                ISO_CAL_KW_LOC = 1
                kwStartDate = startDateParsed.isocalendar()[ISO_CAL_KW_LOC]
                if kw < kwStartDate:
                    blowerdoorDate = "{} KW-{}".format(startDateParsed.year +1, kw)
                else:
                    blowerdoorDate = "{} KW-{}".format(startDateParsed.year, kw)



    location = location.replace("\n\n", "\n").strip("n")
    customer = customer.replace("\n \n", "\n").strip("n")
    customer = customer.replace("\n\n", "\n").strip("n")

    filename = filename.replace("\\","/")
    return data.BlowerdoorData(filename, os.path.basename(filename), location, 
                                    customer, startDateParsed, blowerdoorDate)
