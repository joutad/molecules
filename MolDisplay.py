import molecule
from io import TextIOWrapper
import re

header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">"""
footer = """</svg>"""
offsetx = 500
offsety = 500
radius: dict
element_name: dict
# radius = {
#     'H': 25,
#     'C': 40,
#     'O': 40,
#     'N': 40,
# }
# element_name = {
#     'H': 'grey',
#     'C': 'black',
#     'O': 'red',
#     'N': 'blue',
# }

class Atom:
    def __init__(self, c_atom: molecule.atom):
        self.atom = c_atom
        self.z = c_atom.z

    def __str__(self) -> str:
        return self.atom.element + " " + str(self.atom.x) + " " + str(self.atom.y) + " " + str(self.atom.z)

    def svg(self) -> str:
        x = self.atom.x
        y = self.atom.y
        rad = radius[self.atom.element]
        colour = element_name[self.atom.element]
        return (' <circle cx="{x:.2f}" cy="{y:.2f}" r="{rad:}" fill="url(#{colour:})"/>\n').format(x = (x*100.0)+offsetx, y = (y*100.0)+offsety, rad = rad, colour = colour)

class Bond:
    def __init__(self, c_bond: molecule.bond) -> None:
        self.bond = c_bond
        self.z = c_bond.z

    def __str__(self) -> str:
        a1 = self.bond.a1
        a2 = self.bond.a2
        epairs = self.bond.epairs
        x1 = self.bond.x1
        x2 = self.bond.x2
        y1 = self.bond.y1
        y2 = self.bond.y2
        z = self.bond.z
        len = self.bond.len
        dx = self.bond.dx
        dy = self.bond.dy
        return str(a1) + " " + str(a2) + " " + str(epairs) + " " + str(x1) + " " + str(x2) + " " + str(y1) + " " + str(y2) + " " + str(z) + " " + str(len) + " " + str(dx) + " " + str(dy)

    def svg(self) -> str:
        x1top = self.bond.x1*100 + offsetx - self.bond.dy*10
        x2top = self.bond.x2*100 + offsetx - self.bond.dy*10
        x1bottom = self.bond.x1*100 + offsetx + self.bond.dy*10
        x2bottom = self.bond.x2*100 + offsetx + self.bond.dy*10
        y1top = self.bond.y1*100 + offsety + self.bond.dx*10
        y2top = self.bond.y2*100 + offsety + self.bond.dx*10
        y1bottom = self.bond.y1*100 + offsety - self.bond.dx*10
        y2bottom = self.bond.y2*100 + offsety - self.bond.dx*10
        return (' <polygon points="{x1_top:.2f},{y1_top:.2f} {x1_bottom:.2f},{y1_bottom:.2f} {x2_bottom:.2f},{y2_bottom:.2f} {x2_top:.2f},{y2_top:.2f}" fill="green"/>\n').format(x1_top = x1top, y1_top = y1top, x2_top = x2top, y2_top = y2top, x1_bottom = x1bottom, y1_bottom = y1bottom, x2_bottom = x2bottom, y2_bottom = y2bottom)
    
class Molecule(molecule.molecule):
    def __str__(self) -> str:
        totalCat = "Atoms:\n"

        for i in range(self.atom_no):
            atom = self.get_atom(i)
            c_Atom = Atom(atom).__str__()
            totalCat += c_Atom + "\n"

        for i in range(self.bond_no):
            bond = self.get_bond(i)
            c_Bond = Bond(bond).__str__()
            totalCat += c_Bond + "\n"

        return totalCat

    def svg(self) -> str:
        atoms = []
        bonds = []
        
        for i in range(self.atom_no):
            atom = self.get_atom(i)
            cAtom = Atom(atom)
            atoms.append(cAtom)

        for i in range (self.bond_no):
            bond = self.get_bond(i)
            cBond = Bond(bond)
            bonds.append(cBond)

        svg = header + '\n'

        print("TOTAL LOOP = " + str(len(atoms)+len(bonds)))
        totalSize = len(atoms) + len(bonds)
        a1 = atoms.pop(0)
        b1 = bonds.pop(0)
        
        while totalSize > 0:
            if a1.z < b1.z:
                # print("A1, " + str(a1.z) + ",, " + a1.__str__())
                svg += a1.svg()
                if len(atoms) > 0:
                    a1 = atoms.pop(0)
                else:
                    a1.z = b1.z + 5
            else:
                # print("B1, " + str(b1.z) + ",, " + b1.__str__())
                svg += b1.svg()
                if len(bonds) > 0:
                    b1 = bonds.pop(0)
                else:
                    b1.z = a1.z + 5
            totalSize -= 1
        
        svg += footer

        return svg
    
    def parse(self, file: TextIOWrapper):
        mol = self

        title = ""
        program = ""
        comment = ""
        counts = ""
        numAtoms = 0
        numBonds = 0
        atomNo = 0
        bondNo = 0

        lines = file.readlines()

        for i in range(len(lines)):
            if i is 0:
                title += lines[i]
            elif i is 1:
                program += lines[i]
            elif i is 2:
                comment += lines[i]
            elif i is 3:
                counts += lines[i]
                x = re.findall(r"\d+", counts)
                numAtoms = int(x[0])
                numBonds = int(x[1])
            else:
                x = re.findall(r"\S+", lines[i])

                if len(x) > 3 and x[3].isalpha() and (atomNo < numAtoms):
                    mol.append_atom(x[3], float(x[0]), float(x[1]), float(x[2]))
                    atomNo += 1
                elif len(x) > 3 and x[3].isnumeric() and (bondNo < numBonds):
                    mol.append_bond(int(x[0]), int(x[1]), int(x[2]))
                    bondNo += 1
        return self
