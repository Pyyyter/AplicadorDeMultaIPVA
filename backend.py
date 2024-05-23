import csv
from datetime import datetime
import cv2
import easyocr
import numpy as np
import matplotlib.pyplot as plt
from ultralytics import YOLO
class Vehicle:
    def __init__(self, plateCode, isIPVAPaid,isCRLVPaid, ownerRegisterNumber):
        self.plate = plateCode
        self.isIPVAPaid = int(isIPVAPaid)
        self.isCRLVPaid = int(isCRLVPaid)
        self.ownerRegisterNumber = ownerRegisterNumber

class Owner:
    def __init__(self, registerNumber, name, points, capital, isLicenseActive):
        if registerNumber == "None":
            self.registerNumber = None
        else:
            self.registerNumber = int(registerNumber)
        self.name = name
        self.capital = int(capital)
        self.points = int(points)
        self.isLicenseActive = int(isLicenseActive)
    
    def printOwner(self):
        print(self.registerNumber, self.name, self.points, self.capital, self.isLicenseActive)

class GenericDB:
    def __init__(self, params):
        self.params = params

    def generateVehicle(self, data):
        pass
    
    def returnCar(self, plate):
        pass

    def generateOwner(self, data):
        pass

    def returnOwner(self, registerNumber):
        pass

    def updateOwner(self, owner):
        pass

    def updateVehicle(self, vehicle):
        pass
    
class CsvDB(GenericDB):
    def __init__(self, carsFile, ownersFile):
        self.carsFile = carsFile
        self.ownersFile = ownersFile

    def generateVehicle(self, data):
        return Vehicle(data[0], data[1], data[2], data[3])

    def returnCar(self, plate):
        with open(self.carsFile, "r") as file:
            for line in file:
                line = line.strip().split(",")
                if line[0] == plate:
                    return self.generateVehicle(line)
            print("Car not found")
            return None
    
    def generateOwner(self, data):
        return Owner(data[0], data[1], data[2], data[3], data[4])

    def returnOwner(self, vehicle):

        with open(self.ownersFile, "r") as file:
            for line in file:
                line = line.strip().split(",")
                if line[0] == vehicle.ownerRegisterNumber:
                    return self.generateOwner(line)
            print("Owner not found")
            return None
            
    def encontrar_indice_linha(self, registerNumber, dados):
        for i, linha in enumerate(dados):
            if i == 0:
                continue  
            if int(linha[0]) == int(registerNumber):
                return i
        return -1

    def updateOwner(self, owner):
        with open(self.ownersFile, 'r', newline='') as f:
            reader = csv.reader(f)
            data = list(reader)
        
        lineIndex = self.encontrar_indice_linha(owner.registerNumber, data)
        
        if lineIndex != -1:
            data[lineIndex] = [owner.registerNumber, owner.name, owner.points, owner.capital, owner.isLicenseActive]
            with open(self.ownersFile, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(data)
            print("Dados atualizados com sucesso.")
        else:
            print(f"Erro: Número de registro {owner.registerNumber} não encontrado.")

    # TODO
    # Update to the new implementation
    def updateVehicle(self, vehicle):
        # with open(self.ownersFile, 'r') as f:
        #     self.reader = csv.self.reader(f)
        #     data = list(self.reader)
        #     indice_linha = self.encontrar_indice_linha(vehicle.plate, data)
        # if indice_linha != -1:
        #     data[indice_linha] = [vehicle.plate, vehicle.isIPVAPaid, vehicle.isCRLVPaid, vehicle.ownerRegisterNumber]
        # else:
        #     print(f"Erro: Número de registro {vehicle.plate} não encontrado.")  
        pass

class MySQLDB(GenericDB):
    def __init__(self, params):
        self.openConnection(params)

    def openConnection(self, params):
        pass

    def generateVehicle(self, data):
        return Vehicle(data[0], data[1], data[2], data[4])
        
    def searchOnDB(self, plate):
        # query that returns the vehicle data
        pass

    def returnCar(self, plate):
        data = self.searchOnDB(plate)
        self.generateVehicle(data)
        pass
    
    def searchOwnerOnDB(self, registerNumber):
        # query that returns the owner data
        pass

    def generateOwner(self, data):
        return Owner(data[0], data[1], data[2], data[3])

class Manager():
    def __init__(self, db, computerVision):
        self.db = db
        self.computerVision = computerVision
        self.lastPlate = ""

    def isLicenseRevoked(self, owner):
        if owner.points > 20 and owner.capital >= 2:
            return True
        elif owner.points > 30 and owner.capital == 1:
            return True
        elif owner.points > 40:
            return True
        return False

    def checkOwner(self, plate):
        vehicle = self.db.returnCar(plate)
        owner = self.db.returnOwner(vehicle)
        print(owner.name)

    def applyTicket(self, owner, sentence, value, points):
        print(f"Aplicando multa de {value} reais para {owner.name} por {sentence}")
        # Chamada de API para envio de multa para sistema do DETRAN
        owner.points += points
        if points == 7 :
            owner.capital += 1
        self.db.updateOwner(owner)

    def inference(self, plate):
        vehicle = self.db.returnCar(plate)
        owner = self.db.returnOwner(vehicle)
        decision = "Veiculo regular"
        if self.isLicenseRevoked(owner):
            self.applyTicket(owner, "Dirigir com carteira cassada", 880.41, 7)
            decision = "Licenca cassada"

        if not vehicle.isIPVAPaid or not vehicle.isCRLVPaid:
            self.applyTicket(owner, "Dirigir com documento irregular, apreensão do veículo permitida", 293.47, 7)
            decision = "Documento irregular"

        if not owner.isLicenseActive:
            self.applyTicket(owner, "Licenca vencida", 293.47, 7)
            decision = "Licença vencida"
        return owner, decision

    def logger(self, image, owner, decision, logPath="assets/logs/", imagesPath="assets/logs/images/"):
        data_hora_atual = datetime.now()
        data_formatada = data_hora_atual.strftime("%d-%m-%Y")
        hora_formatada = data_hora_atual.strftime("%H-%M-%S")
        finalPath = f"{imagesPath}{owner.registerNumber}+{data_formatada}+{hora_formatada}.jpg"
        print(finalPath)
        cv2.imwrite(finalPath, image)
        with open(f"{logPath}log.csv", "a", newline='') as file:  # Adicionando newline=''
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([owner.registerNumber, owner.name, owner.points, owner.isLicenseActive, data_formatada, hora_formatada, decision, finalPath])

    def run(self, image, res):
        plates = self.computerVision.onlyOCRInference(image, res)
        for plate in plates:
            owner, decision = self.inference(plate)
            if decision != "Veículo regular" and plate != self.lastPlate:
                self.logger(image, owner, decision)
                self.lastPlate = plate
            else:
                pass
    
class ComputerVision:
    def __init__(self, model, reader):
        self.model = model
        self.reader = reader

    def inference(self, image):
        results = self.model.predict(image, image.shape[0] if image.shape[0] >= image.shape[1] else image.shape[1])
        placas = []
        for r in results:
            if r:
                for box in r.boxes:
                    x, y, w, h = box.xywh[0].tolist()
                    placas.append(self.getOCR(image, x, y, w, h))
        return placas
    def onlyOCRInference(self, image,results):
        placas = []
        for r in results:
            if r:
                for box in r.boxes:
                    x, y, w, h = box.xywh[0].tolist()
                    placas.append(self.getOCR(image, x, y, w, h))
        return placas


    def fixOCR(self, ocr):
        for i in range(len(ocr)):
            if i == 0 or i == 1 or i == 2 or i == 4:
                if ocr[i] == "0":
                    ocr = ocr[:i] + "O" + ocr[i+1:]
                if ocr[i] == "1":
                    ocr = ocr[:i] + "I" + ocr[i+1:]
                if ocr[i] == "5":
                    ocr = ocr[:i] + "S" + ocr[i+1:]
                if ocr[i] == "4":
                    ocr = ocr[:i] + "L" + ocr[i+1:]
                if ocr[i] == "8":
                    ocr = ocr[:i] + "B" + ocr[i+1:]
                if ocr[i] == "7":
                    ocr = ocr[:i] + "Z" + ocr[i+1:]
                if ocr[i] == "2":
                    ocr = ocr[:i] + "Z" + ocr[i+1:]
            if i == 3 or i == 5 or i == 6:
                if ocr[i] == "O" or ocr[i] == "o":
                    ocr = ocr[:i] + "0" + ocr[i+1:]
                if ocr[i] == "I" or ocr[i] == "i":
                    ocr = ocr[:i] + "1" + ocr[i+1:]
                if ocr[i] == "S" or ocr[i] == "s":
                    ocr = ocr[:i] + "5" + ocr[i+1:]
                if ocr[i] == "B" or ocr[i] == "b":
                    ocr = ocr[:i] + "8" + ocr[i+1:]
                if ocr[i] == "L" or ocr[i] == "l":
                    ocr = ocr[:i] + "4" + ocr[i+1:]
                if ocr[i] == "Z" or ocr[i] == "z":
                    ocr = ocr[:i] + "7" + ocr[i+1:]
                if ocr[i] == "C" or ocr[i] == "c":
                    ocr = ocr[:i] + "0" + ocr[i+1:]
                if ocr[i] == "G" or ocr[i] == "g":
                    ocr = ocr[:i] + "4" + ocr[i+1:]
        print(ocr)
        return ocr

    def getOCR(self, image, x, y, w, h):
        real_x = x - w/2
        real_y = y - h/2
        cropped = image[int(real_y):int(real_y+h), int(real_x):int(real_x+w)]
        cv2.imwrite("assets/croppedTESTE.jpg", cropped)
        gray = cv2.cvtColor(cropped, cv2.COLOR_RGB2GRAY)
        results = self.reader.readtext(gray)
        ocr = ""
        for item in results:
            if len(item[1]) == 7:
                ocr = item[1]
        ocr = ocr.upper()
        ocr = self.fixOCR(ocr)
        return ocr

    def getOCROnFullImage(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        results = self.reader.readtext(gray)
        ocr = ""
        for result in results:
            if len(results) == 1:
                ocr = result[1]
            if len(results) >1 and len(results[1])>6 and results[2]> 0.2:
                ocr = result[1]
        return ocr

    def ocrInResults(self, image, results):
        placas = []
        for r in results:
            if r:
                for box in r.boxes:
                    x, y, w, h = box.xywh[0].tolist()
                    placas.append(self.getOCR(image, x, y, w, h))
        return placas


