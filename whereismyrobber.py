import os


class Coord():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "({:g},{:g})".format(self.x, self.y)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def distance_from_coord(self, coord2):
        dx = self.x - coord2.x
        dy = self.y - coord2.y
        
        dist = (dx**2 + dy**2)**0.5
        return dist

    def steps_from_coord(self, coord2):
        dx = self.x - coord2.x
        dy = coord2.y - self.y
        return Coord(dx, dy)
        

class CRSEntity():
    len = 1384

    id = {"crobber"      : bytearray.fromhex("01 14 00 00 FE 03 00 00"),
          "vrobber"      : bytearray.fromhex("01 14 00 00 EE 03 00 00"),
          "bear"         : bytearray.fromhex("04 00 01 00 19 04 00 00"),
          "lynx"         : bytearray.fromhex("0C 00 01 00 10 04 00 00"),
          "wolf"         : bytearray.fromhex("03 00 01 00 0B 04 00 00"),
          "elk"          : bytearray.fromhex("0A 00 00 00 1A 04 00 00"),
          "reindeer"     : bytearray.fromhex("0A 00 00 00 1C 04 00 00")}
	
    def __init__(self, bytesarr):
        self.groupid = bytesarr[0:8]
        self.kind = bytesarr[8:48]
        self.name = bytesarr[48:62]
        self.location_zoomin_wens = bytesarr[744:748]
        self.location_bigmap_we = bytesarr[876:878]
        self.location_bigmap_ns = bytesarr[880:882]

        self.kind_str = self.kind.partition(b'\0')[0].decode('latin_1')
        self.name_str = self.name.partition(b'\0')[0].decode('latin_1')

    def __repr__(self):
        return self.kind_str

    def get_bigmap_coordinates(self):
        x = self.location_bigmap_we
        y = self.location_bigmap_ns
        return Coord(int.from_bytes(x, byteorder='little'), int.from_bytes(y, byteorder='little'))

    def isrobber(self):
        return self.groupid.startswith(bytearray.fromhex("01 14"))


class URWSaveScan():
    def __init__(self):
        self.savename = os.path.basename(os.path.abspath("."))
        print("Save name:", self.savename)
        
        self.ursname = self.savename + ".URS"
        self.crsname = self.savename + ".CRS"
        
        if not os.path.isfile(self.ursname):
            raise FileNotFoundError("{:s} not found".format(self.ursname))
        if not os.path.isfile(self.crsname):
            raise FileNotFoundError("{:s} not found".format(self.crsname))
            
    def get_player_coord(self):
        with open(self.ursname, 'rb') as furs:
            furs.seek(4604, 0)
            xb = furs.read(2)
            furs.seek(2, 1)
            yb = furs.read(2)
            
            self.xb_player = xb
            self.yb_player = yb
            
            #print(xb.hex(), yb.hex())
            
            self.coord_player = Coord(int.from_bytes(xb, byteorder='little'), int.from_bytes(yb, byteorder='little'))
            
            print("Found player coordinates at:\nx = {:d}\ny = {:d}\n".format(self.coord_player.x, self.coord_player.y))
        
        
    def scan_entities(self, gimmerobber=False):
        self.target_list = []
        with open(self.crsname, 'rb') as fcrs:
            while True:            
                entblock = fcrs.read(1384)
                if len(entblock) == 0: break
                
                if entblock.count(bytes(1)) != CRSEntity.len:
                    entity = CRSEntity(entblock)
                    
                    #print(entity.groupid.hex(' '))
                    #print(entity.kind_str)
                    #print(entity.name_str)
                    #print(entity.location_bigmap_we.hex(' '), entity.location_bigmap_ns.hex(' '))
                    #print(entity.location_zoomin_wens.hex(' '))
                    #print("")
                    
                    if gimmerobber is True:
                        if entity.isrobber():
                            self.target_list.append(entity)

    def get_robbers(self):
        self.get_player_coord()
        self.scan_entities(gimmerobber=True)
        self.target_list.sort(key=lambda x: x.get_bigmap_coordinates().distance_from_coord(self.coord_player))

        for ie, ent in enumerate(self.target_list):
            if ie > 0 and entcoord == ent.get_bigmap_coordinates(): continue
            entcoord = ent.get_bigmap_coordinates()
            print("Angry {:s} at only {:1.2f} km from you!".format(ent.kind_str, entcoord.distance_from_coord(self.coord_player)/10))
            toent = entcoord.steps_from_coord(self.coord_player)
            nsdir = "North" if toent.y > 0 else "South"
            wedir = "East" if toent.x > 0 else "West"
            
            print("To reach it, go {:d} tiles {:s} and {:d} tiles {:s}\n".format(abs(toent.x), wedir, abs(toent.y), nsdir))
            
            yesno = input("Do you want to find another robber near you? (Y/n)")
            if yesno.lower() == 'yes' or yesno.lower() == 'y' or yesno.lower() == '': pass
            if yesno.lower() == 'no' or yesno.lower() == 'n': break
            
        

if __name__ == "__main__":
    urws = URWSaveScan()

    yesno = input("Do you want to find robbers near you? (Y/n)")
    
    if yesno.lower() == 'yes' or yesno.lower() == 'y' or yesno.lower() == '':
        urws.get_robbers()
