import csv

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
        #     reader = csv.reader(f)
        #     data = list(reader)
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
    def __init__(self, db):
        self.db = db
    
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
        owner.printOwner()
        if self.isLicenseRevoked(owner):
            self.applyTicket(owner, "Dirigir com carteira cassada", 880,41, 7)

        if not vehicle.isIPVAPaid or not vehicle.isCRLVPaid:
            self.applyTicket(owner, "Dirigir com documento irregular, apreensão do veículo permitida", 293.47, 7)
            
        if not owner.isLicenseActive:
            self.applyTicket(owner, "Licença vencida", 293.47, 7)
        
        owner.printOwner()
        print(vehicle.plate, vehicle.isIPVAPaid, vehicle.isCRLVPaid, vehicle.ownerRegisterNumber)

csvDB = CsvDB("cars.csv", "owners.csv")
manager = Manager(csvDB)
manager.inference("LNN2302")

