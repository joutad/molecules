import os
import sqlite3
from MolDisplay import Atom, Bond, Molecule

class Database:
    def __init__(self, reset=False):
        self.reset = reset
        if self.reset == True:
            os.remove( 'molecule.db' )
        self.conn = sqlite3.connect( 'molecule.db' )

    def create_tables(self):
        if not self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Elements';").fetchall():
            self.conn.execute( """CREATE TABLE Elements
                 ( ELEMENT_NO     INTEGER       NOT NULL,
                   ELEMENT_CODE   VARCHAR(3)    NOT NULL    PRIMARY KEY,
                   ELEMENT_NAME   VARCHAR(32)   NOT NULL,
                   COLOUR1        CHAR(6)       NOT NULL,
                   COLOUR2        CHAR(6)       NOT NULL,
                   COLOUR3        CHAR(6)       NOT NULL,
                   RADIUS         DECIMAL(3)    NOT NULL)
                   ;""" )
        
        if not self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Atoms';").fetchall():
            self.conn.execute( """CREATE TABLE Atoms
                 ( ATOM_ID        INTEGER       NOT NULL    PRIMARY KEY AUTOINCREMENT,
                   ELEMENT_CODE   VARCHAR(3)    NOT NULL,
                   X              DECIMAL(7,4)  NOT NULL,
                   Y              DECIMAL(7,4)  NOT NULL,
                   Z              DECIMAL(7,4)  NOT NULL,
                   FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements(ELEMENT_CODE)
                   );""" )
            
        if not self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Bonds';").fetchall():
            self.conn.execute( """CREATE TABLE Bonds
                 ( BOND_ID        INTEGER       NOT NULL    PRIMARY KEY AUTOINCREMENT,
                   A1             INTEGER       NOT NULL,
                   A2             INTEGER       NOT NULL,
                   EPAIRS         INTEGER       NOT NULL)
                   ;""" )
            
        if not self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Molecules';").fetchall():
            self.conn.execute( """CREATE TABLE Molecules
                ( MOLECULE_ID     INTEGER       NOT NULL    PRIMARY KEY AUTOINCREMENT,
                  NAME            TEXT          NOT NULL    UNIQUE)
                  ;""" )
            
        if not self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='MoleculeAtom';").fetchall():
            self.conn.execute( """CREATE TABLE MoleculeAtom
                 ( MOLECULE_ID    INTEGER       NOT NULL,
                   ATOM_ID        INTEGER       NOT NULL,
                   PRIMARY KEY (MOLECULE_ID, ATOM_ID)
                   FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID)
                   FOREIGN KEY (ATOM_ID) REFERENCES Atoms(ATOM_ID))
                   ;""" )
            
        if not self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='MoleculeBond';").fetchall():
            self.conn.execute( """CREATE TABLE MoleculeBond
                 ( MOLECULE_ID    INTEGER       NOT NULL,
                   BOND_ID        INTEGER       NOT NULL,
                   PRIMARY KEY (MOLECULE_ID, BOND_ID)
                   FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID)
                   FOREIGN KEY (BOND_ID) REFERENCES Bonds(BOND_ID))
                   ;""" )
            
        if not self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Selected';").fetchall():
            self.conn.execute( """CREATE TABLE Selected
                (  NAME            TEXT          NOT NULL    UNIQUE)
                  ;""" )
            
    def __setitem__(self, table, values):
        query = "INSERT INTO " + table + " ("
        if table == "Elements":
            query += "ELEMENT_NO, ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3, RADIUS"
        elif table == "Atoms":
            query += "ELEMENT_CODE, X, Y, Z"
        elif table == "Bonds":
            query += "A1, A2, EPAIRS"
        elif table == "Molecules":
            query += "NAME"
        elif table == "MoleculeAtom":
            query += "MOLECULE_ID, ATOM_ID"
        elif table == "MoleculeBond":
            query += "MOLECULE_ID, BOND_ID"
        
        query += ") VALUES "

        if table == "Molecules":
            query += "(\'"

        if table == "Elements":
            query = "INSERT INTO " + table + " VALUES "

        query += str(values)

        if table == "Molecules":
            query += "\')"
        query += ";"

        # print(query)
        id = self.conn.execute(query).lastrowid

        self.conn.commit()

        return id

    def add_atom(self, molname, atom):
        values = (atom.atom.element, atom.atom.x, atom.atom.y, atom.atom.z)
        atomID = self.__setitem__("Atoms", values)
        
        moleculeID = self.conn.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME=?", (molname,)).fetchone()[0]
        values = (moleculeID, atomID)
        self.__setitem__("MoleculeAtom", values)
        
        self.conn.commit()
    
    def add_bond(self, molname, bond):
        values = (bond.bond.a1, bond.bond.a2, bond.bond.epairs)
        bondID = self.__setitem__("Bonds", values)

        moleculeID = self.conn.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME=?", (molname,)).fetchone()[0]
        
        values = (moleculeID, bondID)
        self.__setitem__("MoleculeBond", values)

        self.conn.commit()

    def add_molecule(self, name, fp):
        Mol = Molecule()
        Mol.parse(fp)

        print("file lines")##DEL
        print(fp.readlines())#DEL

        values = (name)
        self.__setitem__("Molecules", values)
        print("moleule", name, " set!")#DEL

        for i in range(Mol.atom_no):
            Atm = Atom(Mol.get_atom(i))
            self.add_atom(name, Atm)

        for i in range(Mol.bond_no):
            Bnd = Bond(Mol.get_bond(i))
            self.add_bond(name, Bnd)

    def load_mol(self, name):
        Mol = Molecule()

        lst_atom = self.conn.execute("SELECT Atoms.*, MoleculeAtom.*, Molecules.NAME FROM Atoms INNER JOIN MoleculeAtom ON Atoms.ATOM_ID = MoleculeAtom.ATOM_ID INNER JOIN Molecules ON MoleculeAtom.MOLECULE_ID = Molecules.MOLECULE_ID WHERE Molecules.NAME='"+ name + "' ORDER BY Atoms.ATOM_ID;").fetchall()

        lst_bond = self.conn.execute("SELECT Bonds.*, MoleculeBond.*, Molecules.NAME FROM Bonds INNER JOIN MoleculeBond ON Bonds.BOND_ID = MoleculeBond.BOND_ID INNER JOIN Molecules ON MoleculeBond.MOLECULE_ID = Molecules.MOLECULE_ID WHERE Molecules.NAME='"+ name + "' ORDER BY Bonds.BOND_ID;").fetchall()

        for i in range(len(lst_atom)):
            el = lst_atom[i][1]
            x = lst_atom[i][2]
            y = lst_atom[i][3]
            z = lst_atom[i][4]
            Mol.append_atom(el, x, y, z)

        for i in range(len(lst_bond)):
            a1 = lst_bond[i][1]+1
            a2 = lst_bond[i][2]+1
            epairs = lst_bond[i][3]
            Mol.append_bond(a1, a2, epairs)

        return Mol
    
    def radius(self):
        lst = self.conn.execute("SELECT * FROM Elements").fetchall()

        kv = {}
        for i in range(len(lst)):
            kv[lst[i][1]] = lst[i][6] 

        return kv
    
    def element_name(self):
        lst = self.conn.execute("SELECT * FROM Elements").fetchall()

        kv = {}
        for i in range(len(lst)):
            kv[lst[i][1]] = lst[i][2]
        
        return kv
    
    def radial_gradients(self):
        lst = self.conn.execute("SELECT * FROM Elements").fetchall()
        total = ""
        for i in range(len(lst)):
            radialGradientSVG = """
  <radialGradient id="{el_name:}" cx="-50%" cy="-50%" r="220%" fx="20%" fy="20%">
    <stop offset="0%" stop-color="#{c1:}"/>
    <stop offset="50%" stop-color="#{c2:}"/>
    <stop offset="100%" stop-color="#{c3:}"/>
  </radialGradient>""".format(el_name = lst[i][2], c1 = lst[i][3], c2 = lst[i][4], c3 = lst[i][5])
            total += radialGradientSVG
        
        return total

# import MolDisplay
# if __name__ == "__main__":
#  db = Database(reset=True);
#  db.create_tables();
#  db['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 );
#  db['Elements'] = ( 6, 'C', 'Carbon', '808080', '010101', '000000', 40 );
#  db['Elements'] = ( 7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40 );
#  db['Elements'] = ( 8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40 );
#  fp = open( 'water-3D-structure-CT1000292221.sdf' );
#  db.add_molecule( 'Water', fp );
#  fp = open( 'caffeine-3D-structure-CT1001987571.sdf' );
#  db.add_molecule( 'Caffeine', fp );
#  fp = open( 'CID_31260.sdf' );
#  db.add_molecule( 'Isopentanol', fp );
#  # display tables
#  print( db.conn.execute( "SELECT * FROM Elements;" ).fetchall() );
#  print( db.conn.execute( "SELECT * FROM Molecules;" ).fetchall() );
#  print( db.conn.execute( "SELECT * FROM Atoms;" ).fetchall() );
#  print( db.conn.execute( "SELECT * FROM Bonds;" ).fetchall() );
#  print( db.conn.execute( "SELECT * FROM MoleculeAtom;" ).fetchall() );
#  print( db.conn.execute( "SELECT * FROM MoleculeBond;" ).fetchall() );

# if __name__ == "__main__":
#  if __name__ == "__main__":
#     db = Database(reset=False); # or use default
#     MolDisplay.radius = db.radius();
#     MolDisplay.element_name = db.element_name();
#     MolDisplay.header += db.radial_gradients();
#     for m in [ 'Water', 'Caffeine', 'Isopentanol' ]:
#         mol = db.load_mol( m );
#         mol.sort();
#         fp = open( m + ".svg", "w" );
#         fp.write( mol.svg() );
#         fp.close();