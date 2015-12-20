import zpl2
import cups


class Label:

    def __init__(self):
        self.zpl = None
        pass

    def cupsPrint(self, printerName):
        if self.zpl is None:
            return

        data = self.zpl.getAllBytes()

        conn = cups.Connection()
        job = conn.createJob(printer=printerName,
                             title='PartDB label', options={})
        doc = conn.startDocument(printer=printerName, job_id=job,
                                 doc_name='', format=cups.CUPS_FORMAT_RAW,
                                 last_document=1)
        conn.writeRequestData(data, len(data))
        conn.finishDocument(printer=printerName)

    def createLabelFromData(self, data):
        self.zpl = zpl2.Zpl2(firmware='V45.11.7ZA')

        # label data
        labelWidth = 900
        labelHeight = 300

        # barcode dimensions/position
        barCodeDotHeight = 9
        barCodeHeight = 22 * barCodeDotHeight
        barCodeWidth = 22 * barCodeDotHeight
        barCodePosY = int((labelHeight - barCodeHeight) / 2)
        barCodePosX = barCodePosY

        # font dimensions
        sizeLarge = 50
        sizeSmall = 30

        # text positions
        textPosX = 2 * barCodePosX + barCodeWidth
        textPosYFirst = barCodePosY

        fieldSpacing = 5

        offsetY = textPosYFirst

        self.zpl.StartFormat()
        self.zpl.LabelTop(10)
        self.zpl.ChangeInternationalFontEncoding('cp850')
        self.zpl.PrintWidth(labelWidth)

        if 'manufacturerName' in data:
            self.zpl.printText(
                x=textPosX,
                y=offsetY,
                width=550,
                fontWidth=sizeSmall,
                fontHeight=sizeSmall,
                text=data['manufacturerName'])
            offsetY += sizeSmall + fieldSpacing

        self.zpl.printText(
            x=textPosX,
            y=offsetY,
            width=550,
            fontWidth=sizeLarge,
            fontHeight=sizeLarge,
            text=data['manufacturerPartNumber'])
        offsetY += sizeLarge

        self.zpl.printText(
            x=textPosX,
            y=offsetY,
            width=550,
            fontWidth=sizeSmall,
            fontHeight=sizeSmall,
            text=data['description'],
            maximumNumberOfLines=4)
        offsetY += sizeSmall + fieldSpacing

        self.zpl.printDataMatrixBarCode(
            x=barCodePosX,
            y=barCodePosY,
            height=barCodeDotHeight,
            data=data['id'])

        self.zpl.EndFormat()
