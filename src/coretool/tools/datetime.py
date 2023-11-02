from datetime import datetime, timedelta, date
import calendar

def dt_add_one_month(orig_date):
    # advance year and month by one month
    new_year = orig_date.year
    new_month = orig_date.month + 1
    # note: in datetime.date, months go from 1 to 12
    if new_month > 12:
        new_year += 1
        new_month -= 12
    last_day_of_month = calendar.monthrange(new_year, new_month)[1]
    new_day = min(orig_date.day, last_day_of_month)
    return orig_date.replace(year=new_year, month=new_month, day=new_day)


def dt_convert24(str1):
    # Checking if last two elements of time 
    # is AM and first two elements are 12 
    if str1[-2:] == "AM" and str1[:2] == "12": 
        return "00" + str1[2:-3] 
          
    # remove the AM     
    elif str1[-2:] == "AM": 
        return str1[:-3]
      
    # Checking if last two elements of time 
    # is PM and first two elements are 12    
    elif str1[-2:] == "PM" and str1[:2] == "12": 
        return str1[:-3] 
          
    else:
        return str(int(str1[:2]) + 12) + str1[2:8] 

def  dt_str_to_dt24_format(dtstr: str):
    res = dtstr.split(' ')
    if len(res) == 2:
        if len(res[1].split(':')) == 2:
            dtstr = res[0] + ' ' + res[1] + ':00'

        return datetime.strptime(dtstr, '%d/%m/%Y %H:%M:%S')
    elif len(res) == 3:
        if res[2] == 'a.m.' or res[2] == 'p.m.':
            res[2] = res[2].replace('a.m.', 'AM')
            res[2] = res[2].replace('p.m.', 'PM')
        #dtconv = dt_convert24("{} {} {}".format( res[0], res[1], res[2]))[0:-1]
        #dtconv = res[0] + ' ' + dt_convert24("{} {}".format(res[1], res[2]))
        hora = dt_convert24("{} {}".format(res[1], res[2])).split(' ')[0]
        if len(hora.split(':')) == 2:
            hora = hora + ':00'
        return datetime.strptime(
                                 (res[0] + ' ' + hora),
                                 '%d/%m/%Y %H:%M:%S'
                                )
    else:
        return None

def dt_str_to_time24_format(horastr):
    return datetime.strptime(horastr, '%d/%m/%Y %H:%M:%S').time()

def dt_time_to_operatable_format(hora):
    '''
    Retorna un objecto time operable, es decir se podra sumar y restar
    de otros objetos 'timedelta'
    '''
    return datetime.strptime(str(hora), '%H:%M:%S')

def dt_get_dayname(fecha):
    day_name= ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado','Domingo']
    return day_name[fecha.weekday()]

def dt_are_these_dates_intersected(da1: date, da2: date, db1: date, db2: date) -> bool:
    if da1 > da2:
        dtemp = da1
        da1 = da2
        da2 = dtemp
    if db1 > db2:
        dtemp = db1
        db1 = db2
        db2 = dtemp
    if ((db1 <= da1 <= db2) or (db1 <= da2 <= db2)) or ((da1 <= db1) and (da2 >= db2)):
        return True
    return False

def dt_difftimedelta_str(td: timedelta, fecharef: date, upside: bool=False,
                         getstr: bool=False) -> str or dict:
    '''
    Retorna la diferencia neta en anhos, meses y dias de un date con un time delta.

    :param td: timedelta que se desea comparar
    :param fecharef: fecha de referencia
    :param upside: si el timedelta se suma o se resta a la fecha de referencia
    :param getstr: si se quiere que se retorne en un string con texto predefinido
    :return: dict y,m,d que representan anho/s, mes/es, dia/s de la diferencia
    '''
    if upside:
        fechaextremo = fecharef + td
    else:
        fechaextremo = fecharef - td
    y = abs(fecharef.year - fechaextremo.year)

    f1 = fechaextremo
    f2 = fecharef
    if fecharef < fechaextremo:
        f1 = fecharef
        f2 = fechaextremo
    m1 = f1.month
    m2 = f2.month
    if y == 0:
        m = abs(m1 - m2)
    else:
        if m2 < m1:
            y = y - 1
            m = 12 - m1 + m2
        else:
            m = m2 - m1
    d = abs(f1.day - f2.day)
    if getstr:
        return (str(y) + ' año' + ('s' if y != 1 else '') + ', ' +
                str(m) + ' mes' + ('es' if m != 1 else '') + ', ' +
                str(d) + ' día' + ('s' if d != 1 else ''))
    return {'y': y, 'm': m, 'd': d}
