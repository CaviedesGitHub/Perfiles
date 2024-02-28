import requests
from flask_restful import Api
from flask_jwt_extended import JWTManager
import math
import random
from sqlalchemy import func, desc, asc
from sqlalchemy.orm import aliased

from flask import Flask, current_app
import os
from flask_cors import CORS

def create_app(config_name, settings_module='config.ProductionConfig'):
    app=Flask(__name__)
    app.config.from_object(settings_module)
    return app


settings_module = os.getenv('APP_SETTINGS_MODULE','config.ProductionConfig')
application = create_app('default', settings_module)
app_context=application.app_context()
app_context.push()




import enum
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from sqlalchemy import DateTime, Date
from sqlalchemy.sql import func

db = SQLAlchemy()

class Nivel_Habil(enum.Enum):
    ALTO = 1
    MEDIO = 2
    BAJO = 3

class Tipo_Habil(enum.Enum):
    TECNICA = 1
    BLANDA = 2
    PERSONALIDAD = 3

class Perfil(db.Model):
    __tablename__ = 'perfil'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def __init__(self, *args, **kw):
        super(Perfil, self).__init__(*args, **kw)

    def get_id(self):
        return self.id

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Perfil.query.get(id)

    @staticmethod
    def get_count():
        return Perfil.query.count()
    
    @staticmethod
    def get_perfil(id_perfil):   ##  ?????????
        return Perfil.query.count()
    
    @staticmethod
    def get_perfiles():
        return Perfil.query.all()

class PerfilSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Perfil
        include_relationships = True
        load_instance = True

perfil_schema = PerfilSchema()

class HabilPerfil(db.Model):
    __tablename__ = 'habilperfil'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_perfil = db.Column(db.Integer, nullable=False)
    id_habil = db.Column(db.Integer, nullable=False)
    valoracion = db.Column(db.Enum(Nivel_Habil), nullable=False, default=Nivel_Habil.BAJO)  
    calificacion = db.Column(db.Integer, nullable=False, default=0)  

    def __init__(self, *args, **kw):
        super(HabilPerfil, self).__init__(*args, **kw)

    def get_id(self):
        return self.id

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return HabilPerfil.query.get(id)
    
    @staticmethod
    def get_by_idPerfil(id_perfil):
        return HabilPerfil.query.filter_by(id_perfil=id_perfil).all()

    @staticmethod
    def get_countby_idPerfil(id_perfil):
        return HabilPerfil.query.filter_by(id_perfil=id_perfil).count()
    
    @staticmethod
    def get_count():
        return HabilPerfil.query.count()
    
    
class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        else:
            return value.name #{'llave':value.name, 'valor':value.value} #{value.name}  #{'llave':value.name, 'valor':value.value}

class HabilPerfilSchema(SQLAlchemyAutoSchema):
    valoracion=EnumADiccionario(attribute=('valoracion'))
    class Meta:
        model = HabilPerfil
        include_relationships = True
        load_instance = True

habilperfil_schema = HabilPerfilSchema()



class Habilidad(db.Model):
    __tablename__ = 'habilidad'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.Unicode(128), nullable=False, default='MISSING')
    tipo = db.Column(db.Enum(Tipo_Habil), nullable=False, default=Tipo_Habil.PERSONALIDAD)  

    def __init__(self, *args, **kw):
        super(Habilidad, self).__init__(*args, **kw)

    def get_id(self):
        return self.id

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id(id):
        return Habilidad.query.get(id)

    @staticmethod
    def get_count():
        return Habilidad.query.count()

    @staticmethod
    def get_by_tipo(tipo):
        return Habilidad.query.filter_by(tipo=tipo)

    @staticmethod
    def get_count_by_tipo(tipo):
        return Habilidad.query.filter_by(tipo=tipo).count()
    
    @staticmethod
    def get_all():
        return Habilidad.query.all()


class HabilidadSchema(SQLAlchemyAutoSchema):
    tipo=EnumADiccionario(attribute=('tipo'))
    class Meta:
        model = Habilidad
        include_relationships = True
        load_instance = True

habilidad_schema = HabilidadSchema()

db.init_app(application)
db.create_all()


CORS(application)


from flask_restful import Resource
from flask import jsonify
from flask import request
from sqlalchemy import func
#from perfiles.modelos.modelos import db, Perfil, HabilPerfil, Habilidad, Nivel_Habil

class VistaPerfil(Resource):
    def get(self, id_perfil):
        print("Obteniendo Perfil")
        lstHabils=db.session.query(Perfil.id, (HabilPerfil.id).label('num_habilperfil'), HabilPerfil.calificacion, HabilPerfil.valoracion, (Habilidad.id).label('num_habil'), Habilidad.nombre, Habilidad.tipo
           ).filter(Perfil.id==HabilPerfil.id_perfil
           ).filter(HabilPerfil.id_habil==Habilidad.id
           ).filter(Perfil.id==id_perfil).all()
        for h in lstHabils:
            print(h.id, h.num_habil, h.nombre, h.tipo)

        data = []
        for h in lstHabils:
            habil_data = {
                'id_hp': h.num_habilperfil,
                'id_perfil': h.id,
                'id_habil': h.num_habil ,
                'nombre': h.nombre,
                'tipo_habil': h.tipo.name,
                'cod_habil': h.tipo.value,
                'valoracion': h.valoracion.name,
                'calificacion': h.calificacion
            }
            data.append(habil_data)
        return {'Habilidades': data, 'totalCount': len(data)}, 200

class VistaPerfiles(Resource):
    def get(self):
        print("Obteniendo Perfiles")
        return [perfil_schema.dump(perfil) for perfil in Perfil.get_perfiles()] 

class VistaHabilsPerfiles(Resource):
    def post(self):
        print("Consulta Habilidades Perfiles")
        lstPerfiles=request.get_json().get("lstPerfiles", None)
        if lstPerfiles is not None and len(lstPerfiles)!=0:
            lstDetPerfiles=[]
            for p in lstPerfiles:
                perfil=Perfil.get_by_id(p)
                perfilJSON=perfil_schema.dump(perfil)
                cont=HabilPerfil.get_countby_idPerfil(p)
                lstHP=HabilPerfil.get_by_idPerfil(p)
                lstHT=[]
                lstHB=[]
                lstHP=[]
                if cont > 0:    
                    print("mayor")
                    for i in HabilPerfil.get_by_idPerfil(p):
                        print("en el for")
                        print("hp", i)
                        habilidad=Habilidad.get_by_id(i.id_habil)
                        habilidadJSON=habilidad_schema.dump(habilidad)
                        habilidadJSON["id_ph"]=i.id
                        habilidadJSON["valoracion"]=i.valoracion.name
                        if habilidad.tipo==Tipo_Habil.TECNICA:
                            lstHT.append(habilidadJSON)
                        elif habilidad.tipo==Tipo_Habil.BLANDA:
                            lstHB.append(habilidadJSON)
                        else:
                            lstHP.append(habilidadJSON)
                    print("despues del for")
                perfilJSON["lstHT"]=lstHT
                perfilJSON["lstHB"]=lstHB
                perfilJSON["lstHP"]=lstHP
                lstDetPerfiles.append(perfilJSON)
            return {"lstDetPerfiles":lstDetPerfiles}, 200
        else:
            return {"Mensaje":"Falta la lista de perfiles.", "lstDetPerfiles":[]}, 400


class VistaCreaPerfil(Resource):
    def post(self):
        print("Creando Perfil")
        print(request.get_json())
        lstHabils=request.get_json().get("lstHabils", None)
        print(lstHabils)
        if lstHabils is not None and len(lstHabils)!=0:
            p=existePerfil(lstHabils)
            if p==0:
                np=creaPerfil(lstHabils)
            else:
                return {"Mensaje":"Perfil ya existe.", "id_perfil":p}, 200    
        else:
            return {"Mensaje":"Falta la lista de habilidades.", "id_perfil":0}, 400
        return {"Mensaje":"Nuevo Perfil creado.", "id_perfil":np}, 200

class VistaCreaPerfilPlus(Resource):
    def post(self):
        print("Creando Perfil Plus")
        id_perfil=request.json.get("id_perfil")
        lstHabils=request.json.get("lstHabils")
        if lstHabils is not None and id_perfil is not None:
            lstHabilsPerfil=db.session.query(Perfil.id, HabilPerfil.id_habil, HabilPerfil.valoracion
            ).filter(Perfil.id==HabilPerfil.id_perfil
            ).filter(Perfil.id==id_perfil).all()
            lstHabilsCombinada=[]
            for h in lstHabilsPerfil:
                lstHabilsCombinada.append(h.id_habil)
            for h in lstHabils:
                if h not in lstHabilsCombinada:
                    lstHabilsCombinada.append(h)

            p=existePerfil(lstHabilsCombinada)
            if p==0:
                np=creaPerfil(lstHabilsCombinada)
            else:
                return {"Mensaje":"Perfil ya existe.", "id_perfil":p}, 200    
        else:
            return {"Mensaje":"Falta la lista de habilidades o el id de Perfil."}, 200
        return {"Mensaje":"Nuevo Perfil creado.", "id_perfil":np}, 200 

class VistaConsultaPerfil(Resource):
    def get(self):
        print("Consulta Perfil")
        lstHabils=request.json.get("lstHabils")
        if lstHabils is not None:
            p=existePerfil(lstHabils)
            if p==0:
                return {"Mensaje":"Perfil NO existe.", "id_perfil":p}, 200    
            else:
                return {"Mensaje":"Perfil ya existe.", "id_perfil":p}, 200    
        else:
            return {"Mensaje":"Falta la lista de habilidades."}, 200

class VistaConsultaPerfiles(Resource):
    def post(self):
        print("Consulta Perfiles.")
        lstHabils=request.json.get("lstHabils")
        if lstHabils is not None:
            long_lista=len(lstHabils)
            conteo=(func.count(HabilPerfil.id_perfil)).label('conteo')
            lstCumplenHabils = db.session.query(HabilPerfil.id_perfil, HabilPerfil.id_habil, HabilPerfil.valoracion, Habilidad.nombre, Habilidad.tipo).filter(HabilPerfil.id_habil==Habilidad.id).filter(HabilPerfil.id_perfil.in_(db.session.query(HabilPerfil.id_perfil).filter(HabilPerfil.id_habil.in_(lstHabils)).group_by(HabilPerfil.id_perfil).having(conteo==long_lista)))
            # Original lstCumplenHabils = db.session.query(HabilPerfil.id_perfil, HabilPerfil.id_habil, HabilPerfil.valoracion).filter(HabilPerfil.id_perfil.in_(db.session.query(HabilPerfil.id_perfil).filter(HabilPerfil.id_habil.in_(lstHabils)).group_by(HabilPerfil.id_perfil).having(conteo==long_lista)))
            l=0
            for h in lstCumplenHabils:
                l=l+1
                print(h)
            if l!=0:
                num_perfil=0
                data1 = []
                data = []
                for h in lstCumplenHabils:
                    if h.id_perfil!=num_perfil:
                        if num_perfil!=0:
                            resp={
                                'id_perfil': num_perfil, 
                                'lstHabils': data 
                            }   
                            data1.append(resp)
                            data = []
                        num_perfil=h.id_perfil
                    habil_data = {
                        'id_perfil': h.id_perfil,
                        'id_habil': h.id_habil,
                        'valoracion': h.valoracion.name,
                        'cod_valor': h.valoracion.value,
                        'nombre': h.nombre,
                        'tipo': h.tipo.name
                    }
                    data.append(habil_data)
                resp={
                        'id_perfil': num_perfil, 
                        'lstHabils': data 
                }
                data1.append(resp)
                return {'ListaPerfiles': data1, 'totalCount': len(data1)}, 200
            else:
                return {"Mensaje":"No existen perfiles con esa lista de habilidades.", 'ListaPerfiles': [], 'totalCount': 0}, 200    
        else:
            return {"Mensaje":"Falta la lista de habilidades.", 'ListaPerfiles': [], 'totalCount': 0}, 200

class VistaListaHabils(Resource):
    def get(self):
        print("Lista de Habilidades")
        return [habilidad_schema.dump(hab) for hab in Habilidad.get_all()] 

class VistaListaHabilsLike(Resource):
    def post(self):
        print("Lista de Habilidades LIKE")
        patron=request.json.get("patron","")
        print("patron")
        print(patron)
        lstHabil = db.session.query(Habilidad.id, Habilidad.nombre).filter(Habilidad.nombre.ilike(f'%{patron}%')).order_by(asc(Habilidad.id)).all()
        print(lstHabil)
        data = []
        lstNumHabil = []
        for h in lstHabil:
            lstNumHabil.append(h.id)
            cand_data = {
                'id_habil': h.id,
                'nom_habil': h.nombre
            }
            data.append(cand_data)
        return {'lstNumHabilidades': lstNumHabil, 'totalCount': len(lstNumHabil)}, 200

class VistaAsignaPerfilCandidato(Resource):
    def post(self, id_cand):
        print("Asigna Perfil a Candidato")
        print('json')
        print(request.json)
        lstHabils=request.json.get("lstHabils")
        arrayHabils=lstHabils.split(',')
        lstHabilsNum=[]
        for h in arrayHabils:
            lstHabilsNum.append(int(h))
        lnum_perfil=0
        if lstHabilsNum is not None and len(lstHabilsNum)!=0:
            p=existePerfil(lstHabilsNum)
            lnum_perfil=p
            if p==0:
                np=creaPerfil(lstHabilsNum)
                lnum_perfil=np
        else:
            lnum_perfil=-1
        req_headers = request.headers  #{"Authorization": f"Bearer {lst[1]}"}
        perfil= {"id_perfil": lnum_perfil}
        r = requests.post(f"{current_app.config['HOST_PORT_CANDIDATO']}/candidatos/asignaPerfil/"+str(id_cand), headers=req_headers, json=perfil)
        print(r)
        return {}, 200

class VistaPing(Resource):
    def get(self):
        print("pong")
        return {"Mensaje":"Pong"}, 200


def existePerfil(lstHabilidades):
    long_lista=len(lstHabilidades)
    conteo=(func.count(HabilPerfil.id_perfil)).label('conteo')
    queryCumplenHabils=db.session.query(HabilPerfil.id_perfil, conteo).filter(HabilPerfil.id_habil.in_(lstHabilidades)).group_by(HabilPerfil.id_perfil).having(conteo==long_lista).all()
    if len(queryCumplenHabils)==0:
       return 0
    else:
       queryLongCorrecta=db.session.query(HabilPerfil.id_perfil, conteo).group_by(HabilPerfil.id_perfil).having(conteo==long_lista).all()    
       for h in queryCumplenHabils:
            for hh in queryLongCorrecta:
                if h.id_perfil==hh.id_perfil:
                   return h.id_perfil
       return 0

def creaPerfil(lsthabil):
    try:
        np=Perfil()
        db.session.add(np)
        db.session.commit()
        for h in lsthabil:
            nhp=HabilPerfil()
            nhp.id_habil=h
            nhp.id_perfil=np.id
            nhp.valoracion=Nivel_Habil.BAJO
            db.session.add(nhp)
            db.session.commit()
        return np.id
    except Exception as inst:
        db.session.rollback()
        print(type(inst))    # the exception instance
        #print(inst)
        print("habilidad no se pudo crear.")


api = Api(application)
api.add_resource(VistaPing, '/perfiles/ping')
api.add_resource(VistaPerfil, '/perfil/<int:id_perfil>')
api.add_resource(VistaPerfiles, '/perfiles')
api.add_resource(VistaCreaPerfil, '/perfil/crear')
api.add_resource(VistaCreaPerfilPlus, '/perfil/crear/plus')
api.add_resource(VistaConsultaPerfil, '/perfil/consultar')
api.add_resource(VistaConsultaPerfiles, '/perfil/consultar/perfiles')
api.add_resource(VistaHabilsPerfiles, '/perfiles/habilidades')
api.add_resource(VistaListaHabils, '/perfiles/lstHabilidades')
api.add_resource(VistaListaHabilsLike, '/habilidades/like')
api.add_resource(VistaAsignaPerfilCandidato, '/perfil/asignaCandidato/<int:id_cand>')

jwt = JWTManager(application)

def queHabil(lstHabil, orden):
    i=1
    for h in lstHabil:
        if i==orden:
            return h.id
        i=i+1
    return None

def adicionarPerfil(lsthabil):
    try:
        np=Perfil()
        db.session.add(np)
        db.session.commit()
        for h in lsthabil:
            nhp=HabilPerfil()
            nhp.id_habil=h
            nhp.id_perfil=np.id
            nhp.valoracion=Nivel_Habil.BAJO
            nhp.calificacion=random.randint(0, 100)
            db.session.add(nhp)
            db.session.commit()
    except Exception as inst:
        db.session.rollback()
        print(type(inst))    # the exception instance
        #print(inst)
        print("habilidad no se pudo crear.")


if Habilidad.get_count()==0:
    print("Creando Habilidades.")
    regT=0
    with open("./lenguajes.txt") as archivo:
        for linea in archivo:
            try:
                nombre=linea.split(sep=',')[1]
                nh=Habilidad()
                nh.nombre=nombre[0:-1]
                nh.tipo=Tipo_Habil.TECNICA
                db.session.add(nh)
                db.session.commit()
                regT=regT+1
            except Exception as inst:
                db.session.rollback()
                print(type(inst))    # the exception instance
                #print(inst)
                print("habil tecnica no se pudo crear.")
    regB=0
    with open("./habilblandas.txt") as archivo:
        for linea in archivo:
            try:
                nombre=linea.split(sep=':')[1]
                nh=Habilidad()
                nh.nombre=nombre[0:-1]
                nh.tipo=Tipo_Habil.BLANDA
                db.session.add(nh)
                db.session.commit()
                regB=regB+1
            except Exception as inst:
                db.session.rollback()
                print(type(inst))    # the exception instance
                #print(inst)
                print("habil blanda no se pudo crear.")
    regP=0
    with open("./personalidad.txt") as archivo:
        for linea in archivo:
            try:
                nombre=linea.split(sep=',')[1]
                nh=Habilidad()
                nh.nombre=nombre[0:-1]
                nh.tipo=Tipo_Habil.PERSONALIDAD
                db.session.add(nh)
                db.session.commit()
                regP=regP+1
            except Exception as inst:
                db.session.rollback()
                print(type(inst))    # the exception instance
                #print(inst)
                print("rasgo personalidad no se pudo crear.")
    print("registros guardados: "+str(regT)+" "+str(regB)+" "+str(regP))

if Perfil.get_count()==0:
    print("Creando Perfiles.")
    regT=0  #"id"
    with open("./perfil.csv") as archivo:
        for linea in archivo:
            try:
                campos=linea.split(sep=',')
                cn=Perfil()
                cn.id=int(campos[0])

                db.session.add(cn)
                db.session.commit()
                regT=regT+1
                #print("=====================")
                #print(cn.id)
                #print(regT)
            except Exception as inst:
                db.session.rollback()
                print(type(inst))    # the exception instance
                #print(inst)
                print("Perfil no se pudo crear.")

if HabilPerfil.get_count()==0:
    print("Creando Habilidades-Perfiles.")
    regT=0  #"id","id_perfil","id_habil","valoracion","calificacion"
    with open("./habilperfil.csv") as archivo:
        for linea in archivo:
            try:
                campos=linea.split(sep=',')
                cn=HabilPerfil()
                cn.id_perfil=int(campos[1])
                cn.id_habil=int(campos[2])
                cn.valoracion=Nivel_Habil[campos[3][1:-1]]
                cn.calificacion=int(campos[4])

                db.session.add(cn)
                db.session.commit()
                regT=regT+1
                print("=====================")
                print(cn.id)
                print(regT)
            except Exception as inst:
                db.session.rollback()
                print(type(inst))    # the exception instance
                #print(inst)
                print("HabilPerfil no se pudo crear.")

if Perfil.get_count()==0 and False:
    for i in range (4500):
        lstHabilidades=[]

        lstHabilTecnica=Habilidad.get_by_tipo(Tipo_Habil.TECNICA)
        num_habilTecnica=Habilidad.get_count_by_tipo(Tipo_Habil.TECNICA)
        max_habilTecnica=math.trunc(num_habilTecnica*15/100)
        num_habilTecnicaAsignar = random.randint(1, max_habilTecnica)
        #print(num_habilTecnica," ",max_habilTecnica," ",num_habilTecnicaAsignar)
        for i in range(num_habilTecnicaAsignar):
            num_reg=random.randint(1, num_habilTecnica)
            id_habil=queHabil(lstHabilTecnica, num_reg)
            #print(num_reg," ",id_habil)
            if id_habil not in lstHabilidades:
                lstHabilidades.append(id_habil) 
            #print(lstHabilidades)

        lstHabilBlan=Habilidad.get_by_tipo(Tipo_Habil.BLANDA)
        num_habilBlanda = Habilidad.get_count_by_tipo(Tipo_Habil.BLANDA)
        max_habilBlanda=math.trunc(num_habilBlanda*20/100)
        num_habilBlandaAsignar = random.randint(1, max_habilBlanda)
        #print(num_habilBlanda," ",max_habilBlanda," ",num_habilBlandaAsignar)
        for i in range(num_habilBlandaAsignar):
            num_reg=random.randint(1, num_habilBlanda)
            id_habil=queHabil(lstHabilBlan, num_reg)
            #print(num_reg," ",id_habil)
            if id_habil not in lstHabilidades:
                lstHabilidades.append(id_habil) 
            #print(lstHabilidades)

        lstHabilPers=Habilidad.get_by_tipo(Tipo_Habil.PERSONALIDAD)
        num_habilPers=Habilidad.get_count_by_tipo(Tipo_Habil.PERSONALIDAD)
        max_habilPers=math.trunc(num_habilPers*30/100)
        num_habilPersAsignar = random.randint(1, max_habilPers)
        #print(num_habilPers," ",max_habilPers," ",num_habilPersAsignar)
        for i in range(num_habilPersAsignar):
            num_reg=random.randint(1, num_habilPers)
            id_habil=queHabil(lstHabilPers, num_reg)
            #print(num_reg," ",id_habil)
            if id_habil not in lstHabilidades:
                lstHabilidades.append(id_habil) 
            #print(lstHabilidades)

        long_lista=len(lstHabilidades)
        print(lstHabilidades)
        conteo=(func.count(HabilPerfil.id_perfil)).label('conteo')
        queryCumplenHabils=db.session.query(HabilPerfil.id_perfil, conteo).filter(HabilPerfil.id_habil.in_(lstHabilidades)).group_by(HabilPerfil.id_perfil).having(conteo==long_lista).all()
        if len(queryCumplenHabils)==0:
            print("Adicionar1")
            adicionarPerfil(lstHabilidades)
        else:
            queryLongCorrecta=db.session.query(HabilPerfil.id_perfil, conteo).group_by(HabilPerfil.id_perfil).having(conteo==long_lista).all()    
            existe=False
            for h in queryCumplenHabils:
                for hh in queryLongCorrecta:
                    if h.id_perfil==hh.id_perfil:
                        existe=True
                        break
                if existe==True:
                    break
            if not existe:
                print("Adicionar2")
                adicionarPerfil(lstHabilidades)


