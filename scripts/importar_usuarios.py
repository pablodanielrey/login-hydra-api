

import sys
import uuid
import datetime
from users.model import open_session
from users.model.UsersModel import UsersModel
from users.model.entities.User import User, IdentityNumber, IdentityNumberTypes, Mail, MailTypes

from login.model import obtener_session
from login.model.LoginModel import LoginModel
from login.model.entities.Login import UserCredentials

f_to_read = sys.argv[1]
with open(f_to_read,'r') as f:
    with open('/var/log/supervisor/importar.log','a') as log:
        log.write(f'Ejecutando importación {datetime.datetime.utcnow()}\n')
        line = f.readline()
        while line:
            lastname, firstname, student_number, username, password, email = line.replace('\n','').split(';')
            dni = username
            try:            
                with open_session() as s:
                    #print(f'Buscando - {firstname} {lastname} {username} {email}')
                    uid = UsersModel.get_uid_person_number(s, dni)
                    #print(uid)
                    if uid:
                        users = UsersModel.get_users(s, [uid])
                        assert len(users) > 0
                        user = users[0]

                        if student_number and student_number != '':
                            # busco legajo y lo agrego en el caso de que no tenga
                            student_numbers = [l for l in user.identity_numbers if l.type == IdentityNumberTypes.STUDENT]
                            if len(student_numbers) < 0:
                                #print(f'Agregando legajo - {firstname} {lastname} {dni} {student_number}')
                                log.write(f'Agregando legajo - {firstname} {lastname} {dni} {student_number}\n')
                                l = IdentityNumber()
                                l.id = str(uuid.uuid4())
                                l.user_id = uid
                                l.type = IdentityNumberTypes.STUDENT
                                l.number = student_number
                                s.add(l)
                                s.commit()

                    if not uid:
                        log.write(f'Insertando - {firstname} {lastname} {username} {student_number} {email}\n')
                        uid = str(uuid.uuid4())
                        user = User()
                        user.id = uid
                        user.lastname = lastname
                        user.firstname = firstname
                        s.add(user)
                        
                        idni = IdentityNumber()
                        idni.id = str(uuid.uuid4())
                        idni.user_id = uid
                        idni.number = dni
                        idni.type = IdentityNumberTypes.DNI
                        s.add(idni)

                        if student_number and student_number != '':
                            student = IdentityNumber()
                            student.id = str(uuid.uuid4())
                            student.user_id = uid
                            student.number = student_number
                            student.type = IdentityNumberTypes.STUDENT
                            s.add(student)

                        m = Mail()
                        m.id = str(uuid.uuid4())
                        m.user_id = uid
                        m.email = email
                        m.type = MailTypes.ALTERNATIVE
                        s.add(m)
                        s.commit()

                if uid:
                    with obtener_session(False) as s2:
                        uc = s2.query(UserCredentials).filter(UserCredentials.username == dni).one_or_none()
                        if uc:
                            print(f'reseteando login para {uid} - {dni}')
                            uc.updated = datetime.datetime.utcnow()
                            uc.username = dni
                            uc.credentials = dni
                            uc.temporal = True
                            uc.expiration = datetime.datetime.utcnow() + datetime.timedelta(days=365)

                        if not uc:
                            log.write(f'creando login para {uid} - {dni}\n')
                            uc = UserCredentials()
                            uc.id = str(uuid.uuid4())
                            uc.user_id = uid
                            uc.username = dni
                            uc.credentials = dni
                            uc.temporal = True
                            uc.expiration = datetime.datetime.utcnow() + datetime.timedelta(days=365)
                            s2.add(uc)

                        s2.commit()

            except Exception as e:
                print(e)

            log.flush()

            line = f.readline()

