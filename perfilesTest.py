import json
import time
from flask import Response
from flask_jwt_extended import create_access_token
from datetime import timedelta

from unittest import TestCase
from unittest.mock import Mock, patch
import uuid 
import random
import os
from application import application

class testBlackList(TestCase):

    def setUp(self):
        self.client=application.test_client()
        self.tokenfijo="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY4MDYyMzQwNCwianRpIjoiZmVjYTI5NTAtY2I1My00ZWVkLWFiN2ItZjM5ZTMwMDg2NzkxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNjgwNjIzNDA0fQ.aF924YU7GlLR_u6YuFZeZgul2o75ltDYrNkIC6e4a4Q"
        self.userId=2
        self.offerId=1
        self.postId=1
        access_token_expires = timedelta(minutes=120)
        self.token=create_access_token(identity=self.userId, expires_delta=access_token_expires)
        access_token_expires = timedelta(seconds=3)
        self.tokenexpired=create_access_token(identity=self.userId, expires_delta=access_token_expires)
        #self.token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3NTczMTY3MywianRpIjoiOGU1OWJjZmQtNTJlYi00YzQ1LWI1NDUtZTU3MGYxMDBiNTQ0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MiwibmJmIjoxNjc1NzMxNjczLCJleHAiOjE2NzU3Mzg4NzN9.iPaNwx0Sp2TcPOyv5p12e7RyPAUDih3lrLxV0mVN43Q"
        #self.tokenexpired="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3NTY4NDg3NiwianRpIjoiZjdkYzNlN2QtMzFhNy00NWZhLTg3NjItNzIwZDQ0NTUyMWZjIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MiwibmJmIjoxNjc1Njg0ODc2LCJleHAiOjE2NzU2ODY2NzZ9.fPQFhAK_4k16NqpMGcT2eV-q-PQRUKHrLMiQY-xzDYM"


    def test_ping(self):
        endpoint_ping='/perfiles/ping'
        solicitud_ping=self.client.get(endpoint_ping)
        respuesta_ping=json.loads(solicitud_ping.get_data())
        msg=respuesta_ping["Mensaje"]
        self.assertEqual(solicitud_ping.status_code, 200)
        self.assertIn("Pong", msg)

    def test_crea_perfil(self):
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.tokenfijo)
        }

        endpoint_perfil='/perfil/crear'

        lstHabils=[]
        for i in range(7):
            num = random.randint(1, 56)  #57-80    81-90
            if num in lstHabils:
                print("Numero aleatorio existe")
            else:
                lstHabils.append(num)

        for i in range(3):
            num = random.randint(57, 80)  #57-80    81-90
            if num in lstHabils:
                print("Numero aleatorio existe")
            else:
                lstHabils.append(num)
        
        for i in range(1):
            num = random.randint(81, 90)  #57-80    81-90
            if num in lstHabils:
                print("Numero aleatorio existe")
            else:
                lstHabils.append(num)
        lstHabils.sort()
        habils={
            "lstHabils":lstHabils
        }  #[1,10,15,20,30,40,50,70,85]


        solicitud_crear=self.client.post(endpoint_perfil, 
                                                data=json.dumps(habils), 
                                                headers=headers)
        respuesta_crear=json.loads(solicitud_crear.get_data())
        id_perfil=respuesta_crear['id_perfil']
        self.assertIn("Perfil", respuesta_crear['Mensaje'])
        self.assertEqual(solicitud_crear.status_code, 200)

        endpoint_consulta_perfil='/perfil/consultar'
        solicitud_consulta_perfil=self.client.get(endpoint_consulta_perfil, 
                                                data=json.dumps(habils), 
                                                headers=headers)
        respuesta_consulta_perfil=json.loads(solicitud_consulta_perfil.get_data())
        self.assertEqual(respuesta_consulta_perfil['id_perfil'], id_perfil)
        self.assertEqual(solicitud_consulta_perfil.status_code, 200)

    def test_crea_perfilExistente(self):
        modo = os.getenv('APP_SETTINGS_MODULE')

        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.tokenfijo)
        }
        endpoint_consulta_todosPerfiles='/perfiles'
        solicitud_consulta_todosPerfiles=self.client.get(endpoint_consulta_todosPerfiles, headers=headers)
        respuesta_consulta_todosPerfiles=json.loads(solicitud_consulta_todosPerfiles.get_data())
        max_perf=5
        ii=0
        for p in respuesta_consulta_todosPerfiles:
            ii=ii+1
            if modo!="config.DevelopmentConfig":
                if ii>max_perf:
                    break
            numPerfil=p["id"]
            endpoint_consulta_1perfil='/perfil/'+str(numPerfil) #/perfil/<int:id_perfil>
            solicitud_consulta_1perfil=self.client.get(endpoint_consulta_1perfil,   
                                                headers=headers)
            respuesta_consulta_1perfil=json.loads(solicitud_consulta_1perfil.get_data())
            self.assertNotEqual(respuesta_consulta_1perfil['totalCount'],0)
            lstHabils=[]
            for h in respuesta_consulta_1perfil['Habilidades']:
                lstHabils.append(h['id_habil'])
                print(h['id_habil'])
            habils={
                "lstHabils":lstHabils
            }  #[1,10,15,20,30,40,50,70,85]

            endpoint_crea_perfilexistente='/perfil/crear'
            solicitud_crear=self.client.post(endpoint_crea_perfilexistente, 
                                                data=json.dumps(habils), 
                                                headers=headers)
            respuesta_crear=json.loads(solicitud_crear.get_data())
            print(respuesta_crear)
            id_perfil=respuesta_crear['id_perfil']
            self.assertIn(respuesta_crear['Mensaje'], "Perfil ya existe.")
            self.assertEqual(id_perfil, numPerfil)
            self.assertEqual(solicitud_crear.status_code, 200)


    def test_consulta_perfiles(self):
        modo = os.getenv('APP_SETTINGS_MODULE')
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.tokenfijo)
        }
        endpoint_consulta_todosPerfiles='/perfiles'
        solicitud_consulta_todosPerfiles=self.client.get(endpoint_consulta_todosPerfiles, headers=headers)
        respuesta_consulta_todosPerfiles=json.loads(solicitud_consulta_todosPerfiles.get_data())
        max_perf=5
        ii=0        
        for p in respuesta_consulta_todosPerfiles:
            ii=ii+1
            if modo!="config.DevelopmentConfig":
                if ii>max_perf:
                    break
            numPerfil=p["id"]
            endpoint_consulta_1perfil='/perfil/'+str(numPerfil) #/perfil/<int:id_perfil>
            solicitud_consulta_1perfil=self.client.get(endpoint_consulta_1perfil,   
                                                headers=headers)
            respuesta_consulta_1perfil=json.loads(solicitud_consulta_1perfil.get_data())
            self.assertNotEqual(respuesta_consulta_1perfil['totalCount'],0)
            lstHabils=[]
            for h in respuesta_consulta_1perfil['Habilidades']:
                lstHabils.append(h['id_habil'])
                print(h['id_habil'])

            #print(respuesta_consulta_1perfil['Habilidades'])

            endpoint_perfil='/perfil/consultar/perfiles'
            lstHabils.sort()
            habils={
                "lstHabils":lstHabils
            }  #[1,10,15,20,30,40,50,70,85]


            solicitud_consultar_perfiles=self.client.post(endpoint_perfil, 
                                                data=json.dumps(habils), 
                                                headers=headers)
            respuesta_consultar_perfiles=json.loads(solicitud_consultar_perfiles.get_data())
            self.assertEqual(solicitud_consultar_perfiles.status_code, 200)
            self.assertNotEqual(respuesta_consultar_perfiles['totalCount'],0)

            badPerfil=[]
            PerfilBase=False
            for p in respuesta_consultar_perfiles['ListaPerfiles']:
                lPerfil=p['id_perfil']
                lHabils=p['lstHabils']
                auxHabils=[]
                for h in lHabils:
                    auxHabils.append(h['id_habil'])
            
                Contiene=True
                for h1 in lstHabils:
                    if h1 not in auxHabils:
                        Contiene=False
                        break
                if Contiene==False:
                    badPerfil.append(lPerfil)
                if lPerfil==numPerfil:
                    PerfilBase=True
            long=len(badPerfil)
            self.assertEqual(long, 0)
            self.assertEqual(PerfilBase, True)


    def test_consulta_perfilInexistente(self):
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.tokenfijo)
        }            
        endpoint_perfil='/perfil/consultar/perfiles'
        habils={
            "lstHabils":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,20,30,40,56,57,58,59,60,61,62,63,64,65,70,81,82,83,84,85]
        }  #[1,10,15,20,30,40,50,70,85]
        solicitud_consultar_perfiles=self.client.post(endpoint_perfil, 
                                                data=json.dumps(habils), 
                                                headers=headers)
        respuesta_consultar_perfiles=json.loads(solicitud_consultar_perfiles.get_data())
        print(respuesta_consultar_perfiles)
        self.assertEqual(solicitud_consultar_perfiles.status_code, 200)
        self.assertEqual(respuesta_consultar_perfiles['totalCount'], 0)

    def test_consulta_1perfilInexistente(self):
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.tokenfijo)
        }            
        endpoint_perfil='/perfil/consultar'
        habils={
            "lstHabils":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,20,30,40,56,57,58,59,60,61,62,63,64,65,70,81,82,83,84,85]
        }  #[1,10,15,20,30,40,50,70,85]
        solicitud_consultar_perfiles=self.client.get(endpoint_perfil, 
                                                data=json.dumps(habils), 
                                                headers=headers)
        respuesta_consultar_perfiles=json.loads(solicitud_consultar_perfiles.get_data())
        print(respuesta_consultar_perfiles)
        self.assertEqual(solicitud_consultar_perfiles.status_code, 200)
        self.assertEqual(respuesta_consultar_perfiles['Mensaje'], "Perfil NO existe.")
        self.assertEqual(respuesta_consultar_perfiles['id_perfil'], 0)
