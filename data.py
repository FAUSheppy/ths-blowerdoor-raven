class BlowerdoorData:
    def __init__(self, path, docName, location, customer, pdfDate, blowerdoorDate, inDocumentDate=None):
        self.path = path
        self.docName = docName
        self.location = location
        self.customer = customer
        self.blowerdoorDate = blowerdoorDate
        self.pdfDate = pdfDate
        self.inDocumentDate = inDocumentDate

        self.outdated = False

    
#print("Bauort: " + location)
#print("Bauherr: " + customer)
#print("Blowerdoor: " + blowerdoorDate)