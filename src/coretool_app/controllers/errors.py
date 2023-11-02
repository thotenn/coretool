from ..models.errors import ErrorEsperado, ErrorLog
from .pstruct import pstruct_is_valid


class Error:
    @staticmethod
    def send(pathfuncion: str, codigoerr: str, viewcode: str, tipoerror: str = 'E', errcatch: str = None,
             tipocaptura: str= 'str', nombre: str = None, solucion: str = None, modificable=True) -> ErrorLog or None:
        if codigoerr is None:
            return False
        if not pstruct_is_valid(viewcode):
            viewcode = 'Desconocido'
        errlog = None
        try:
            if tipoerror.upper() not in [te[0] for te in ErrorEsperado.TIPOERROR]:
                tipoerror = 'E'
            if ErrorEsperado.objects.filter(viewcode=viewcode, valor=codigoerr).count() == 0:
                erroresperado = ErrorEsperado(
                    tipoerror=tipoerror,
                    viewcode=viewcode,
                    solucion=solucion,
                    nombre=nombre,
                    valor=codigoerr,
                    descripcion=errcatch,
                    modificable=modificable
                )
                erroresperado.save()
            else:
                erroresperado = ErrorEsperado.objects.filter(viewcode=viewcode, valor=codigoerr).last()
            if pathfuncion is None:
                pathfuncion = viewcode
            errlog = ErrorLog.objects.create(
                viewcode=viewcode,
                erroresperado=erroresperado,
                pathfunction=pathfuncion,
                tipocaptura=tipocaptura,
                catchstr=errcatch
            )

        except Exception as err:
            print('Error in system.controllers.errors.Error.send')
            print(err)
            return None
        return errlog
