from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO, TextIOWrapper
import re
import urllib.parse
import json
from molsql import Database
import MolDisplay
import molecule
import sys

db = Database(reset=True) #Use existing DB: reset = false, comment create_tables()
db.create_tables()
db['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 );
db['Elements'] = ( 6, 'C', 'Carbon', '808080', '010101', '000000', 40 );
db['Elements'] = ( 7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40 );
db['Elements'] = ( 8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40 );

public_files = [ '/index.html', '/upload.html', '/select.html', '/display.html', '/style.css', '/script.js' ];

class SubBHRH(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in public_files:
            self.send_response( 200 )
            if self.path.endswith(".css"):
                self.send_header( "Content-type", "text/css" )
            else:
                self.send_header( "Content-type", "text/html" )

            fp = open( self.path[1:] );
            page = fp.read()
            fp.close()

            self.send_header( "Content-length", len(page) )
            self.end_headers()

            # print(page)

            self.wfile.write( bytes( page, "utf-8" ) )

        if self.path == '/':
            self.path = '/index.html'
            self.send_response(302)
            self.send_header('Location', 'index.html')
            self.end_headers()
            # content = ""
            # with open('index.html', 'r') as f:
                # content = f.read()
            # elements = db.element_name()
            # response = {'status': 'success', 'elements': elements}
            # json.dumps(response)
        
        
            # # self.send_header('Content-Type', 'text/html')
            # self.send_header('Content-Type', 'application/json')
            # # print(content)
            # self.send_header('Content-Length', len(json.dumps(response)))
            # self.end_headers()
            # # self.wfile.write(bytes(content, 'utf-8'))
            # self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path.lower() == '/loadelements':
            elements = db.element_name()
            elementsList = db.conn.execute("SELECT * FROM Elements").fetchall()

            for e in elementsList:
                print(e)

            response = {'status': 'success', 'elements': elements, 'elementsList': elementsList}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(json.dumps(response)))
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == "/loadSDF":
            molecules = db.conn.execute("SELECT * FROM Molecules").fetchall()

            response = {'status': 'success', 'molecules': molecules}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(json.dumps(response)))
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == "/loadMolecules":
            molecules = db.conn.execute("SELECT * FROM Molecules").fetchall()

            atom_no = {}
            bond_no = {}

            print(molecules)

            for m in molecules:
                print(m[1])
                selectedM = db.load_mol(m[1])
                atom_no[m[1]] = selectedM.atom_no
                bond_no[m[1]] = selectedM.bond_no

            print(atom_no)
            print(bond_no)

            selectedMolecule = db.conn.execute("SELECT * FROM Selected").fetchall()[0][0]

            print(selectedMolecule)

            response = {'status': 'success', 'molecules': molecules, 'atom_no': atom_no, 'bond_no': bond_no, 'selected': selectedMolecule}

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(json.dumps(response)))
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == "/displayMolecule":
            MolDisplay.radius = db.radius()
            MolDisplay.element_name = db.element_name()
            MolDisplay.header += db.radial_gradients()

            selectedMolecule = db.conn.execute("SELECT * FROM Selected").fetchall()[0][0]
            que = "SELECT NAME FROM Molecules WHERE Molecules.NAME = ('" + str(selectedMolecule) + "');"
            print(que)
            selectedM = db.conn.execute(que).fetchall()[0][0]

            mol = db.load_mol(selectedM)
            molecule.molsort(mol)
            svg = mol.svg()

            response = {'status': 'success', 'svg': svg}

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(json.dumps(response)))
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', 0)
            self.end_headers()

    def do_POST(self):
        if self.path == '/addElement':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            invalid = False

            element_num = data['number'][0]
            element_code = data['code'][0]
            element_name = data['name'][0]
            color1 = data['color1'][0]
            color2 = data['color2'][0]
            color3 = data['color3'][0]
            radius = data['radius'][0]

            def checkColorField(color):
                if len(color) != 6 or len(re.findall(r'[g-z]|\W', color, re.IGNORECASE)) >= 1:
                    print("Error: color field", color, "is invalid!")
                    print(len(color), len(re.findall(r'[g-z]|\W', color, re.IGNORECASE)))
                    return False
                return True
            
            if not checkColorField(color1) or not checkColorField(color2) or not checkColorField(color3):
                invalid = True

            elements = db.element_name()
            response = {'status': 'success', 'elements': elements, 'color1': color1, 'color2': color2, 'color3': color3}
            
            print(invalid)
            print(db.element_name().get(element_code))
            if not invalid and not db.element_name().get(element_code):
                # print("add to elements list")
                db['Elements'] = (element_num, element_code, element_name, color1, color2, color3, radius)
            else:
                print("Cannot add more than one of the same element! If changes need to be made, remove the existing element and add again.")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == "/removeElements":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode('utf-8'))

            element_code = data['code'][0]

            response = {'status': 'success'}

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

            db.conn.execute("DELETE FROM Elements WHERE ELEMENT_CODE = ?", (element_code,))
            db.conn.commit()

        elif self.path == "/uploadSDF":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            byt = BytesIO(post_data)
            next(byt)
            next(byt)
            next(byt)
            next(byt)
            f = TextIOWrapper(byt)

            data = urllib.parse.parse_qs(post_data.decode('utf-8'))

            molName = data[' name'][1]

            molName = molName.splitlines()
            molName = molName[2]

            tableMatch = db.conn.execute("SELECT * FROM Molecules").fetchall()
            print("table match ==== ", len(tableMatch))

            x = ""
            matches = 0
            for e in tableMatch:
                print(e[1])
                x = re.findall(e[1], molName, re.I)
                matches = len(x)
                if matches >= 1:
                    break

            response = ""
            molecules = {}

            if matches == 0:
                mTable = db.conn.execute("""SELECT * FROM Molecules""").fetchall()

                for i in range(len(mTable)):
                    molecules[mTable[i][0]] = mTable[i][1]

                print("Molecule doesnt exist!")
                response = {'status': 'success', 'molecules': molecules}

                db.add_molecule( molName, f )
                db.conn.commit()
                if len(tableMatch) == 0:
                    print("ADD FIRST INDEX TO SELECTED!!!\n")
                    selectedName = molName
                    que = "INSERT OR REPLACE INTO Selected (NAME) VALUES ('" + str(selectedName) + "');"
                    print(que)
                    db.conn.execute(que)
                    db.conn.commit()
            else:
                print("Molecule already exists!")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == "/removeSDF":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode('utf-8'))

            sdfName = data['name'][0]

            response = {'status': 'success'}

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

            db.conn.execute("DELETE FROM Molecules WHERE Molecules.NAME = ?", (sdfName,))
            db.conn.commit()

        elif self.path == "/selectMolecule":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode('utf-8'))

            selectedName = data['name'][0]
            print(selectedName)

            db.conn.execute("DELETE FROM Selected").fetchall()

            que = "INSERT OR REPLACE INTO Selected (NAME) VALUES ('" + str(selectedName) + "');"
            print(que)
            db.conn.execute(que)
            db.conn.commit()

            response = {'status': 'success'}

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', 0)
            self.end_headers()

httpd = HTTPServer(("localhost", int(sys.argv[1])), SubBHRH)
httpd.serve_forever()
