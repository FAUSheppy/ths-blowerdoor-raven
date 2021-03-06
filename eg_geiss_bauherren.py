import fitz
import data
import dateutil.parser
import os.path


BLOCK_TUP_TEXT = 4

def load(filename):
    print(filename)
    doc = fitz.open(filename)
    FIRST_P = True

    # pop vars
    customer = "NOT_FOUND"
    location = ""
    inDocumentDate = None
    startDate = doc.metadata["creationDate"].split("D:")[1].split("+")[0]
    startDateParsed = dateutil.parser.parse(startDate)
    blowerdoorDate = "NOT_FOUND"

    datumNext = False
    page = -1
    for p in doc:
        page += 1
        blocks = p.get_text("blocks")
        for i in range(0, len(blocks)):
        

            text = blocks[i][BLOCK_TUP_TEXT]
        
            textNoSpaceNewline = text.replace("\n", "")
            textNoSpaceNewline = textNoSpaceNewline.replace(" ", "")

            
            if datumNext and page == 0:
                try:
                    #if "Bauablaufplan11.pdf" in filename:
                    #    print(textNoSpaceNewline)
                    inDocumentDate= dateutil.parser.parse(textNoSpaceNewline)
                    datumNext = False
                except ValueError:
                    try:
                        split = textNoSpaceNewline.split(".de")[1]
                        inDocumentDate = dateutil.parser.parse(split)
                    except ValueError:
                        pass
                    except IndexError:
                        pass

            if FIRST_P and i < 3 and textNoSpaceNewline:
                FIRST_P = False
                customer = text

            if "Datum:" in text:
                datumNext = True
            
            if "Bauort:" in text:
                location += text.split("Bauort:")[1]

            kwErrorInfo = None
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
                        try:
                            kw = int(pClean.split(". KW")[0])
                        except ValueError:
                            kwErrorInfo = "Kalenderwochen Info nicht gefunden."
                    elif not title:
                        title = pClean
                    elif not contractor:
                        contractor = pClean

                ISO_CAL_KW_LOC = 1
                kwStartDate = startDateParsed.isocalendar()[ISO_CAL_KW_LOC]

                if kwErrorInfo:
                    blowerdoorDate = None
                else:
                    if kw < kwStartDate:
                        blowerdoorDate = "{} KW-{:02d}".format(startDateParsed.year +1, kw)
                    else:
                        blowerdoorDate = "{} KW-{}".format(startDateParsed.year, kw)



    location = location.replace("\n\n", "\n").strip("n")
    customer = customer.replace("\n \n", "\n").strip("n")
    customer = customer.replace("\n\n", "\n").strip("n")

    filename = filename.replace("\\","/")
    return data.BlowerdoorData(filename, os.path.basename(filename), location, 
                                    customer, startDateParsed, blowerdoorDate, inDocumentDate)
